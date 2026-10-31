"""Modulos simulados (citas, ventas, inventario). Representan a OTROS equipos; sirven para probar el gateway."""
import time
from .seguridad import verificar_token_servicio, TokenInvalido

CONTRATOS = {
  "ventas": {"/productos": {"items": [{"id": int, "nombre": str, "precio": int, "stock": int}], "pagina": int},
             "/pedidos": {"id_pedido": int, "total": int, "url_pago": str}},
  "citas": {"/disponibilidad": {"horarios": [{"hora": str, "profesional": str}]}},
  "inventario": {"/stock": {"stock": [{"id": int, "disponible": int}]}},
}
class ModuloSim:
    def __init__(self, nombre, secreto, reloj, latencia_s=0.0, modo="ok"):
        self.nombre, self.secreto, self.reloj, self.latencia, self.modo = nombre, secreto, reloj, latencia_s, modo; self.llamadas = 0; self.tokens_vistos = []
    def __call__(self, ruta, params, token, timeout, idem, cuerpo):
        self.llamadas += 1
        if self.latencia: time.sleep(self.latencia)
        if self.modo == "timeout": raise TimeoutError("sin respuesta")
        if self.modo == "500": return 500, {"error": "interno"}
        try: self.tokens_vistos.append(verificar_token_servicio(token, self.secreto, self.reloj()))
        except TokenInvalido: return 401, {"error": "token invalido"}
        return self.responder(ruta, params, idem, cuerpo)
    def responder(self, ruta, params, idem, cuerpo): return 404, {}

class VentasSim(ModuloSim):
    PRODUCTOS = [{"id": 1, "nombre": "Crema hidratante", "precio": 12990, "stock": 8}, {"id": 2, "nombre": "Serum vitamina C", "precio": 18990, "stock": 3}, {"id": 4, "nombre": "Mascarilla de arcilla", "precio": 9990, "stock": 0}]
    def __init__(self, *a, **k): super().__init__(*a, **k); self.pedidos = {}
    def responder(self, ruta, params, idem, cuerpo):
        if self.modo == "contrato" and ruta == "/productos": return 200, {"items": [{"id": "1", "nombre": "x"}]}
        if ruta == "/productos": return 200, {"items": self.PRODUCTOS, "pagina": 1}
        if ruta == "/pedidos":
            if idem in self.pedidos: return 200, self.pedidos[idem]
            precios = {p["id"]: p["precio"] for p in self.PRODUCTOS}; total = 0
            for it in cuerpo["items"]:
                if it["id"] not in precios: return 422, {"error": "producto inexistente"}
                total += precios[it["id"]] * it["cantidad"]
            self.pedidos[idem] = {"id_pedido": len(self.pedidos) + 1, "total": total, "url_pago": "https://pago.rgbeauty.test/o/" + str(len(self.pedidos) + 1)}
            self.ultimo_cuerpo = cuerpo; return 201, self.pedidos[idem]
        return 404, {}
class CitasSim(ModuloSim):
    def responder(self, ruta, params, idem, cuerpo):
        return (200, {"horarios": [{"hora": "10:00", "profesional": "Francisca"}, {"hora": "11:00", "profesional": "Paula"}]}) if ruta == "/disponibilidad" else (404, {})
class InventarioSim(ModuloSim):
    def responder(self, ruta, params, idem, cuerpo):
        return (200, {"stock": [{"id": 1, "disponible": 8}, {"id": 2, "disponible": 3}]}) if ruta == "/stock" else (404, {})
