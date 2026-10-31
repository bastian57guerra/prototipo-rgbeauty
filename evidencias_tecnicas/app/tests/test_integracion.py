import unittest
from rgbeauty.gateway import *
from rgbeauty.modulos_sim import *
from rgbeauty.reglas import ReglaNegocioError
from rgbeauty.autorizacion import cambiar_estado_pagina, cambiar_precio
from rgbeauty.reglas import PermisoDenegado
from .base import BaseBD, Reloj, SECRETO, AHORA

def cliente(sim, reloj, nombre, **k): return ClienteModulo(nombre, sim, CONTRATOS[nombre], SECRETO, reloj, **k)

class Integracion(unittest.TestCase):
    def setUp(self): self.r = Reloj()
    def test_PI01_gateway_consulta_y_normaliza_la_respuesta_del_modulo_de_citas(self):
        c = cliente(CitasSim("citas", SECRETO, self.r), self.r, "citas"); resp = c.llamar("/disponibilidad", {"servicio": 1})
        self.assertEqual([h["hora"] for h in resp["horarios"]], ["10:00", "11:00"]); self.assertEqual(c.bitacora[-1]["resultado"], "OK")
    def test_PI02_modulo_caido_degrada_solo_esa_parte_del_sitio(self):
        citas = cliente(CitasSim("citas", SECRETO, self.r, modo="timeout"), self.r, "citas"); ventas = cliente(VentasSim("ventas", SECRETO, self.r), self.r, "ventas")
        res = agregar({"citas": lambda: citas.llamar("/disponibilidad"), "ventas": lambda: ventas.llamar("/productos")})
        self.assertEqual(res["citas"]["estado"], "NO_DISPONIBLE"); self.assertIn("WhatsApp", res["citas"]["mensaje"])
        self.assertEqual(res["ventas"]["estado"], "OK"); self.assertEqual(len(res["ventas"]["datos"]["items"]), 3)
    def test_PI03_circuit_breaker_abre_no_llama_y_se_recupera(self):
        sim = CitasSim("citas", SECRETO, self.r, modo="timeout"); c = cliente(sim, self.r, "citas", reintentos=0)
        for _ in range(3):
            with self.assertRaises(ModuloNoDisponible): c.llamar("/disponibilidad")
        self.assertEqual(c.breaker.estado, "ABIERTO"); antes = sim.llamadas
        with self.assertRaises(ModuloNoDisponible): c.llamar("/disponibilidad")
        self.assertEqual(sim.llamadas, antes, "con el circuito abierto no se debe llamar al modulo")
        self.r.avanzar(31); sim.modo = "ok"; self.assertEqual(len(c.llamar("/disponibilidad")["horarios"]), 2); self.assertEqual(c.breaker.estado, "CERRADO")
    def test_PI04_reintenta_errores_transitorios_pero_no_los_de_cliente(self):
        s500 = CitasSim("citas", SECRETO, self.r, modo="500"); c = cliente(s500, self.r, "citas", reintentos=1)
        with self.assertRaises(ModuloNoDisponible): c.llamar("/disponibilidad")
        self.assertEqual(s500.llamadas, 2)                                                   # 1 intento + 1 reintento
        s404 = CitasSim("citas", SECRETO, self.r); c2 = cliente(s404, self.r, "citas")
        with self.assertRaises(ErrorCliente): c2.llamar("/ruta-inexistente")
        self.assertEqual(s404.llamadas, 1)                                                   # error 4xx: no se reintenta
    def test_PI05_respuesta_que_viola_el_contrato_se_rechaza_y_se_registra(self):
        c = cliente(VentasSim("ventas", SECRETO, self.r, modo="contrato"), self.r, "ventas")
        with self.assertRaises(ContratoInvalido): c.llamar("/productos")
        self.assertEqual(c.bitacora[-1]["resultado"], "CONTRATO_INVALIDO")
    def test_PI06_checkout_ignora_precios_del_navegador_y_evita_pedidos_duplicados(self):
        sim = VentasSim("ventas", SECRETO, self.r); c = cliente(sim, self.r, "ventas"); cache = {}
        items = [{"id": 1, "cantidad": 2, "precio": 1}]                                       # el navegador "dice" que cuesta $1
        r1 = checkout(c, items, "idem-1", "cliente-1", cache); r2 = checkout(c, items, "idem-1", "cliente-1", cache); r3 = checkout(c, items, "idem-1", "cliente-1", cache)
        self.assertEqual(r1["total"], 25980); self.assertEqual(r1, r2); self.assertEqual(r2, r3); self.assertEqual(len(sim.pedidos), 1)
        self.assertNotIn("precio", str(sim.ultimo_cuerpo))
        with self.assertRaises(ReglaNegocioError): checkout(c, [{"id": 1, "cantidad": 99}], "idem-2", "cliente-1", cache)
    def test_PI07_el_modulo_recibe_la_identidad_firmada_y_rechaza_tokens_falsos(self):
        sim = VentasSim("ventas", SECRETO, self.r); c = cliente(sim, self.r, "ventas"); c.llamar("/productos", usuario="asistente-2", rol="ASISTENTE")
        self.assertEqual(sim.tokens_vistos[-1], {"sub": "asistente-2", "rol": "ASISTENTE"})
        falso = cliente(VentasSim("ventas", "secreto-del-atacante", self.r), self.r, "ventas")
        mal = ClienteModulo("ventas", sim, CONTRATOS["ventas"], "secreto-del-atacante", self.r)
        with self.assertRaises(ErrorCliente): mal.llamar("/productos")                         # el modulo responde 401
class IntegracionBD(BaseBD):
    def test_PI08_acciones_administrativas_quedan_auditadas_incluso_las_rechazadas(self):
        cambiar_estado_pagina(self.c, 2, 3, "EN_REVISION", AHORA)                              # asistente envia a revision (permitido)
        cambiar_estado_pagina(self.c, 1, 3, "PUBLICADA", AHORA)                                # duena publica
        with self.assertRaises(PermisoDenegado): cambiar_precio(self.c, 2, 1, 100, AHORA)     # asistente intenta bajar precio
        acciones = [r[0] for r in self.c.execute("SELECT accion FROM auditoria WHERE id_auditoria > 4 ORDER BY id_auditoria")]
        self.assertEqual(acciones, ["PAGINA_EN_REVISION", "PAGINA_PUBLICADA"])
        with self.assertRaises(PermisoDenegado): cambiar_estado_pagina(self.c, 2, 4, "PUBLICADA", AHORA)
        self.assertEqual(self.c.execute("SELECT accion,id_usuario FROM auditoria ORDER BY id_auditoria DESC LIMIT 1").fetchone(), ("ACCESO_DENEGADO", 2))
        self.assertEqual(self.c.execute("SELECT estado FROM pagina WHERE id_pagina=4").fetchone()[0], "EN_REVISION")
