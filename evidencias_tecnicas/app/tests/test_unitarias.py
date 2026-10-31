import unittest
from datetime import timedelta
from rgbeauty.reglas import *
from rgbeauty.seguridad import emitir_token_servicio, verificar_token_servicio, TokenInvalido
from .base import AHORA, SECRETO

class Unitarias(unittest.TestCase):
    def test_PU01_validaciones_de_rut_telefono_y_correo(self):
        for ok in ("11.111.111-1", "12.345.678-5", "9.876.543-3", "123456785"): self.assertTrue(validar_rut(ok), ok)
        for mal in ("12.345.678-9", "1-9", "abc", "", None, "12.345.678-5; DROP TABLE"): self.assertFalse(validar_rut(mal), str(mal))
        self.assertTrue(validar_rut(next(f"{n}-K" for n in range(10000000, 10000200) if validar_rut(f"{n}-K"))))
        for ok in ("+56911111111", "911111111", "+56 9 1111 1111"): self.assertTrue(validar_telefono_cl(ok), ok)
        for mal in ("12345", "+5622233444", "811111111", "", None): self.assertFalse(validar_telefono_cl(mal), str(mal))
        for ok in ("a@b.cl", "ana.munoz@correo.test"): self.assertTrue(validar_correo(ok))
        for mal in ("sin-arroba", "a@b", "a b@c.cl", "", None): self.assertFalse(validar_correo(mal), str(mal))
    def test_PU02_politica_de_contrasenas(self):
        self.assertEqual(validar_password("Tarde-Lluviosa-84", "ana@x.cl"), [])
        self.assertIn("minimo 10 caracteres", validar_password("Ab1", ""))
        self.assertIn("debe combinar letras y numeros", validar_password("sololetrasaqui", ""))
        self.assertIn("clave demasiado comun", validar_password("password123", ""))
        self.assertIn("no debe contener el correo", validar_password("asistente2026!", "asistente@rgbeauty.test"))
    def test_PU03_sanitizacion_de_contenido_y_slug(self):
        self.assertEqual(sanitizar_html('<p onclick="x()">Hola</p><script>alert(1)</script>'), "<p>Hola</p>")
        self.assertEqual(sanitizar_html('<a href="javascript:alert(1)">x</a>'), "<a>x</a>")
        self.assertEqual(sanitizar_html("<img src=x onerror=alert(1)>"), "")
        self.assertEqual(sanitizar_html("<b>ok</b> &amp; <i>bien</i>"), "<b>ok</b> &amp; <i>bien</i>")
        self.assertIn('rel="noopener noreferrer"', sanitizar_html('<a href="https://rgbeauty.test">sitio</a>'))
        self.assertEqual(slugify("Ofertas de Primavera 2026!"), "ofertas-de-primavera-2026"); self.assertEqual(slugify("Niñas & Más"), "ninas-mas")
    def test_PU04_validacion_de_archivos_subidos(self):
        jpg = b"\xff\xd8\xff" + b"0" * 100; png = b"\x89PNG\r\n\x1a\n" + b"0" * 100
        self.assertTrue(validar_archivo("foto.jpg", jpg)[0]); self.assertTrue(validar_archivo("foto.png", png)[0])
        for nombre, datos in [("foto.php.jpg", jpg), ("../foto.jpg", jpg), ("script.js", b"x"), ("foto.jpg", png), ("foto.png", jpg), ("grande.jpg", b"\xff\xd8\xff" + b"0" * 2_000_001), ("sinext", jpg), ("logo.svg", b"<svg>")]:
            self.assertFalse(validar_archivo(nombre, datos)[0], nombre)
    def test_PU05_transiciones_de_estado_de_pagina(self):
        self.assertEqual(permiso_requerido("BORRADOR", "EN_REVISION"), "CONTENIDO_EDITAR")
        self.assertEqual(permiso_requerido("EN_REVISION", "PUBLICADA"), "CONTENIDO_PUBLICAR")
        for a, n in [("BORRADOR", "PUBLICADA"), ("PUBLICADA", "EN_REVISION"), ("BORRADOR", "BORRADOR")]:
            with self.assertRaises(ReglaNegocioError): permiso_requerido(a, n)
    def test_PU06_token_de_servicio_firmado_con_expiracion(self):
        t = emitir_token_servicio("u1", "CLIENTE", SECRETO, AHORA); self.assertEqual(verificar_token_servicio(t, SECRETO, AHORA), {"sub": "u1", "rol": "CLIENTE"})
        with self.assertRaises(TokenInvalido): verificar_token_servicio(t, "otro-secreto", AHORA)
        with self.assertRaises(TokenInvalido): verificar_token_servicio(t.replace("CLIENTE", "DUENA"), SECRETO, AHORA)     # rol alterado
        with self.assertRaises(TokenInvalido): verificar_token_servicio(t, SECRETO, AHORA + timedelta(seconds=61))           # expirado
        with self.assertRaises(TokenInvalido): verificar_token_servicio("basura", SECRETO, AHORA)
