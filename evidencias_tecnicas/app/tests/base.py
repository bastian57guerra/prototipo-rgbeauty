import os, sqlite3, unittest
from datetime import datetime, timedelta
SQLD = os.path.join(os.path.dirname(__file__), "..", "..", "sql")
SECRETO = "secreto-solo-para-pruebas"
AHORA = datetime(2026, 10, 24, 12, 0, 0)
def nueva_bd():
    c = sqlite3.connect(":memory:"); c.execute("PRAGMA foreign_keys = ON")
    for f in ("01_schema.sql", "02_datos_ficticios.sql"): c.executescript(open(os.path.join(SQLD, f), encoding="utf-8").read())
    return c
class Reloj:
    def __init__(self, t=AHORA): self.t = t
    def __call__(self): return self.t
    def avanzar(self, s): self.t += timedelta(seconds=s)
class BaseBD(unittest.TestCase):
    def setUp(self): self.c = nueva_bd()
    def tearDown(self): self.c.close()
