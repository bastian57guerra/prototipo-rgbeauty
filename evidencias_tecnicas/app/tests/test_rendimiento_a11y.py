import statistics, time, unittest
from rgbeauty.gateway import ClienteModulo, agregar
from rgbeauty.modulos_sim import *
from rgbeauty.contraste import PARES, PROHIBIDOS, ratio
from .base import Reloj, SECRETO

UMBRAL_P95_MS = 500          # presupuesto del gateway dentro del limite de 2 s del RNF04
class Rendimiento(unittest.TestCase):
    def test_PR01_gateway_agrega_tres_modulos_en_paralelo_con_latencias_simuladas(self):
        r = Reloj(); ven = VentasSim("ventas", SECRETO, r, latencia_s=0.080); cit = CitasSim("citas", SECRETO, r, latencia_s=0.050); inv = InventarioSim("inventario", SECRETO, r, latencia_s=0.120)
        cv, cc, ci = (ClienteModulo(n, s, CONTRATOS[n], SECRETO, r) for n, s in (("ventas", ven), ("citas", cit), ("inventario", inv)))
        pagina = {"ventas": lambda: cv.llamar("/productos"), "citas": lambda: cc.llamar("/disponibilidad"), "inventario": lambda: ci.llamar("/stock")}
        par, seq = [], []
        for _ in range(60):
            t0 = time.perf_counter(); res = agregar(pagina); par.append((time.perf_counter() - t0) * 1000); assert all(v["estado"] == "OK" for v in res.values())
        for _ in range(20):
            t0 = time.perf_counter(); [f() for f in pagina.values()]; seq.append((time.perf_counter() - t0) * 1000)
        q = statistics.quantiles(par, n=100)
        print(f"\n    [PR-01] paralelo (60 cargas de pagina): p50={statistics.median(par):.0f} ms p95={q[94]:.0f} ms max={max(par):.0f} ms | secuencial (20): p50={statistics.median(seq):.0f} ms | latencias simuladas 50/80/120 ms (umbral p95 <= {UMBRAL_P95_MS} ms)")
        self.assertLessEqual(q[94], UMBRAL_P95_MS); self.assertLess(statistics.median(par), statistics.median(seq))
class Accesibilidad(unittest.TestCase):
    def test_PA01_contraste_de_la_paleta_cumple_WCAG_AA_cuando_se_usa_segun_la_guia(self):
        rechazados = []
        for desc, fg, bg, minimo in PARES:
            x = ratio(fg, bg); print(f"\n    [PA-01] {x:5.2f}:1 (min {minimo}) {'OK   ' if x >= minimo else 'FALLA'} {desc}", end="")
            if x < minimo: rechazados.append(desc)
        for desc, fg, bg, minimo in PROHIBIDOS:
            x = ratio(fg, bg); print(f"\n    [PA-01] {x:5.2f}:1 (min {minimo}) USO PROHIBIDO EN LA GUIA -> {desc}", end=""); self.assertLess(x, minimo)
        self.assertEqual(rechazados, [], "pares que no cumplen: %s" % rechazados)
