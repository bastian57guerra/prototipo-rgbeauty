"""API Gateway del sitio: cliente de modulos con timeout, reintento, circuit breaker, contrato y token firmado."""
import threading, time
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor
from .reglas import ReglaNegocioError
from .seguridad import emitir_token_servicio

class ModuloNoDisponible(Exception): pass
class ErrorCliente(Exception): pass
class ContratoInvalido(Exception): pass

def validar_contrato(cuerpo, esquema, ruta="$"):
    if isinstance(esquema, dict):
        if not isinstance(cuerpo, dict): raise ContratoInvalido(f"{ruta}: se esperaba objeto")
        for k, sub in esquema.items():
            if k not in cuerpo: raise ContratoInvalido(f"{ruta}.{k}: campo faltante")
            validar_contrato(cuerpo[k], sub, f"{ruta}.{k}")
    elif isinstance(esquema, list):
        if not isinstance(cuerpo, list): raise ContratoInvalido(f"{ruta}: se esperaba lista")
        for i, it in enumerate(cuerpo): validar_contrato(it, esquema[0], f"{ruta}[{i}]")
    elif isinstance(cuerpo, bool) or not isinstance(cuerpo, esquema):
        raise ContratoInvalido(f"{ruta}: tipo {type(cuerpo).__name__}, se esperaba {esquema.__name__}")

class CircuitBreaker:
    def __init__(self, umbral=3, espera_s=30):
        self.umbral, self.espera = umbral, timedelta(seconds=espera_s); self.fallos = 0; self.abierto_desde = None; self.estado = "CERRADO"; self._l = threading.Lock()
    def permitir(self, ahora):
        with self._l:
            if self.estado == "CERRADO": return True
            if self.estado == "ABIERTO" and ahora - self.abierto_desde >= self.espera: self.estado = "SEMI_ABIERTO"; return True   # una sola llamada de prueba
            return False
    def exito(self):
        with self._l: self.fallos = 0; self.estado = "CERRADO"
    def fallo(self, ahora):
        with self._l:
            self.fallos += 1
            if self.estado == "SEMI_ABIERTO" or self.fallos >= self.umbral: self.estado = "ABIERTO"; self.abierto_desde = ahora

class ClienteModulo:
    def __init__(self, nombre, transporte, contratos, secreto, reloj, timeout=3.0, reintentos=1, breaker=None):
        self.nombre, self.transporte, self.contratos, self.secreto, self.reloj = nombre, transporte, contratos, secreto, reloj
        self.timeout, self.reintentos, self.breaker = timeout, reintentos, breaker or CircuitBreaker(); self.bitacora = []
    def _log(self, ruta, ms, res): self.bitacora.append({"modulo": self.nombre, "ruta": ruta, "ms": ms, "resultado": res})
    def llamar(self, ruta, params=None, usuario="anonimo", rol="PUBLICO", idem=None, cuerpo=None):
        ahora = self.reloj()
        if not self.breaker.permitir(ahora): self._log(ruta, 0, "CIRCUITO_ABIERTO"); raise ModuloNoDisponible(f"{self.nombre}: circuito abierto")
        for _ in range(self.reintentos + 1):
            t0 = time.perf_counter()
            try:
                status, resp = self.transporte(ruta, params or {}, emitir_token_servicio(usuario, rol, self.secreto, ahora), self.timeout, idem, cuerpo)
            except (TimeoutError, ConnectionError) as e:
                self._log(ruta, int((time.perf_counter() - t0) * 1000), "ERROR_TRANSITORIO:" + type(e).__name__); continue
            ms = int((time.perf_counter() - t0) * 1000)
            if status >= 500: self._log(ruta, ms, f"HTTP_{status}"); continue
            if status >= 400: self._log(ruta, ms, f"HTTP_{status}"); raise ErrorCliente(f"{self.nombre}: HTTP {status}")
            esquema = self.contratos.get(ruta)
            if esquema is not None:
                try: validar_contrato(resp, esquema)
                except ContratoInvalido as e: self._log(ruta, ms, "CONTRATO_INVALIDO"); raise
            self.breaker.exito(); self._log(ruta, ms, "OK"); return resp
        self.breaker.fallo(ahora); raise ModuloNoDisponible(f"{self.nombre}: sin respuesta tras {self.reintentos + 1} intentos")

MENSAJE_DEGRADADO = "Este servicio no esta disponible por ahora. Intenta mas tarde o escribenos por WhatsApp."
def agregar(llamadas):
    """Ejecuta en paralelo; un modulo caido no tumba al resto (degradacion elegante)."""
    with ThreadPoolExecutor(max_workers=max(1, len(llamadas))) as ex:
        futs = {k: ex.submit(f) for k, f in llamadas.items()}
    res = {}
    for k, f in futs.items():
        try: res[k] = {"estado": "OK", "datos": f.result()}
        except (ModuloNoDisponible, ErrorCliente, ContratoInvalido): res[k] = {"estado": "NO_DISPONIBLE", "mensaje": MENSAJE_DEGRADADO}
    return res

def checkout(cliente_ventas, items_navegador, idem, usuario, cache):
    """Cierre de venta: del navegador solo se aceptan ids y cantidades; el precio lo calcula el modulo de ventas."""
    if idem in cache: return cache[idem]
    items = []
    for it in items_navegador:
        idp, cant = int(it["id"]), int(it["cantidad"])
        if not 1 <= cant <= 10: raise ReglaNegocioError("cantidad fuera de rango (1-10)")
        items.append({"id": idp, "cantidad": cant})          # cualquier 'precio' enviado por el navegador se descarta
    resp = cliente_ventas.llamar("/pedidos", usuario=usuario, rol="CLIENTE", idem=idem, cuerpo={"items": items})
    cache[idem] = resp; return resp
