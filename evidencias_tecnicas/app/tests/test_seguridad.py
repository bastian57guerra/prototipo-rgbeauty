from datetime import timedelta
from rgbeauty.seguridad import *
from rgbeauty.autorizacion import *
from rgbeauty.reglas import PermisoDenegado, ReglaNegocioError, sanitizar_html
from .base import BaseBD, AHORA

class Seguridad(BaseBD):
    def test_PS01_inyeccion_sql_funciona_con_concatenacion_y_falla_con_consulta_parametrizada(self):
        payload = "x' OR '1'='1"
        self.assertGreater(len(login_vulnerable(self.c, payload)), 0, "el mal ejemplo deberia ser explotable")
        self.assertIsNone(buscar_usuario_seguro(self.c, payload)); self.assertIsNone(buscar_usuario_seguro(self.c, "x'; DROP TABLE usuario;--"))
        self.assertEqual(self.c.execute("SELECT COUNT(*) FROM usuario").fetchone()[0], 3)
    def test_PS02_claves_con_hash_salado_y_verificable(self):
        h1, h2 = hashear_password("Clave-Segura-2026"), hashear_password("Clave-Segura-2026")
        self.assertNotIn("Clave-Segura-2026", h1); self.assertNotEqual(h1, h2); self.assertTrue(verificar_password("Clave-Segura-2026", h1)); self.assertFalse(verificar_password("otra", h1))
    def test_PS03_bloqueo_tras_5_intentos_y_mensaje_generico(self):
        self.c.execute("UPDATE usuario SET password_hash=? WHERE id_usuario=2", (hashear_password("Correcta-12345"),))
        for _ in range(5): ok, msg = intentar_login(self.c, "asistente@rgbeauty.test", "mala", AHORA)
        self.assertEqual(msg, "Credenciales invalidas")
        ok, msg = intentar_login(self.c, "asistente@rgbeauty.test", "Correcta-12345", AHORA + timedelta(minutes=1)); self.assertFalse(ok); self.assertIn("bloqueada", msg)
        self.assertTrue(intentar_login(self.c, "asistente@rgbeauty.test", "Correcta-12345", AHORA + timedelta(minutes=16))[0])
        self.assertEqual(intentar_login(self.c, "no-existe@x.cl", "x", AHORA)[1], "Credenciales invalidas")
        self.assertEqual(intentar_login(self.c, "asistente2@rgbeauty.test", "x", AHORA)[1], "Credenciales invalidas")        # usuario desactivado
    def test_PS04_contenido_editable_no_puede_inyectar_scripts(self):
        self.assertEqual(escapar_salida('<script>alert("x")</script>'), '&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;')
        malo = '<h2>Oferta</h2><script>document.location="http://x"</script><a href="javascript:steal()">ver</a><img src=x onerror=alert(1)>'
        limpio = sanitizar_html(malo); self.assertNotIn("script", limpio); self.assertNotIn("javascript", limpio); self.assertNotIn("onerror", limpio); self.assertIn("<h2>Oferta</h2>", limpio)
    def test_PS05_asistente_no_escala_privilegios_ni_ve_borradores_publicamente(self):
        self.assertEqual(permisos_de(self.c, 2), {"CONTENIDO_EDITAR", "PRODUCTO_EDITAR", "AGENDA_VER"}); self.assertEqual(len(permisos_de(self.c, 1)), 7)
        self.assertEqual(permisos_de(self.c, 3), set())                                       # usuario desactivado: sin permisos
        for accion in ("USUARIO_GESTIONAR", "PRECIO_EDITAR", "CONTENIDO_PUBLICAR", "AUDITORIA_VER"):
            with self.assertRaises(PermisoDenegado): exigir(self.c, 2, accion)
        editar_titulo_pagina(self.c, 2, 3, "Resultados reales", AHORA)                        # borrador: permitido
        with self.assertRaises(ReglaNegocioError): editar_titulo_pagina(self.c, 2, 1, "x", AHORA)   # publicada: hay que despublicar primero
        self.assertIsNotNone(obtener_pagina_publica(self.c, "inicio")); self.assertIsNone(obtener_pagina_publica(self.c, "resultados")); self.assertIsNone(obtener_pagina_publica(self.c, "ofertas-de-primavera"))
    def test_PS06_recuperacion_de_contrasena_segura(self):
        m1, t1 = solicitar_recuperacion(self.c, "asistente@rgbeauty.test", AHORA); m2, t2 = solicitar_recuperacion(self.c, "no-existe@x.cl", AHORA)
        self.assertEqual(m1, m2); self.assertIsNotNone(t1); self.assertIsNone(t2)              # el mensaje no revela si la cuenta existe
        guardado = self.c.execute("SELECT hash_token FROM token_recuperacion ORDER BY id_token DESC LIMIT 1").fetchone()[0]; self.assertNotEqual(guardado, t1)   # solo se guarda el hash
        self.assertFalse(usar_token_recuperacion(self.c, t1, "123", AHORA + timedelta(minutes=5)))                                   # clave debil
        self.assertTrue(usar_token_recuperacion(self.c, t1, "Nueva-Clave-2026x", AHORA + timedelta(minutes=5)))
        self.assertFalse(usar_token_recuperacion(self.c, t1, "Otra-Clave-2026x", AHORA + timedelta(minutes=6)))                      # un solo uso
        _, t3 = solicitar_recuperacion(self.c, "asistente@rgbeauty.test", AHORA); self.assertFalse(usar_token_recuperacion(self.c, t3, "Nueva-Clave-2026y", AHORA + timedelta(minutes=31)))   # expirado
