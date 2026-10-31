"""Ejecuta toda la bateria y deja la salida en ../salidas/pruebas.txt"""
import sys, os, io, time, platform, sqlite3, unittest, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
class R(unittest.TextTestResult):
    def __init__(s, *a, **k): super().__init__(*a, **k); s.filas = []; s.t0 = 0
    def startTest(s, t): s.t0 = time.perf_counter(); super().startTest(t)
    def _f(s, t, e): s.filas.append((t._testMethodName.split("_")[1], t._testMethodName.split("_", 2)[2], e, (time.perf_counter() - s.t0) * 1000))
    def addSuccess(s, t): super().addSuccess(t); s._f(t, "APROBADA")
    def addFailure(s, t, err): super().addFailure(t, err); s._f(t, "FALLIDA")
    def addError(s, t, err): super().addError(t, err); s._f(t, "ERROR")
buf = io.StringIO(); real = sys.stdout; sys.stdout = buf
suite = unittest.defaultTestLoader.discover(os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests"), pattern="test_*.py", top_level_dir=os.path.dirname(os.path.abspath(__file__)))
res = unittest.TextTestRunner(stream=io.StringIO(), resultclass=R, verbosity=0).run(suite)
sys.stdout = real
cab = ["EVIDENCIA 4.9 - Ejecucion de pruebas | fecha: " + datetime.datetime.now().strftime("%d-%m-%Y %H:%M"),
       f"Ambiente: Python {platform.python_version()} | SQLite {sqlite3.sqlite_version} | {platform.system()} {platform.machine()} | BD en memoria con datos ficticios", "=" * 100,
       f"{'ID':7}{'Estado':11}{'ms':>9}  Descripcion"]
lin = [f"{i.upper():7}{e:11}{ms:9.1f}  {d.replace('_', ' ')}" for i, d, e, ms in sorted(res.filas)]
pie = ["-" * 100, f"Total: {res.testsRun} | Aprobadas: {res.testsRun - len(res.failures) - len(res.errors)} | Falladas: {len(res.failures)} | Errores: {len(res.errors)}"]
for t, tb in res.failures + res.errors: pie += ["", "DETALLE FALLA " + t.id(), tb]
det = ["", "Salida detallada de mediciones:", buf.getvalue()]
txt = "\n".join(cab + lin + pie + det); print(txt)
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "salidas", "pruebas.txt"), "w", encoding="utf-8").write(txt)
sys.exit(0 if res.wasSuccessful() else 1)
