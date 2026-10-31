"""Demostracion tecnica 4.7.1 (estructurada): crea, inserta, consulta y prueba restricciones."""
import sqlite3, datetime, platform, sys, os
base = os.path.dirname(os.path.abspath(__file__))
rd = lambda f: open(os.path.join(base, "sql", f), encoding="utf-8").read()
conn = sqlite3.connect(":memory:"); conn.execute("PRAGMA foreign_keys = ON")
out = []
def p(s=""): out.append(s); print(s)
def tabla(cur):
    cols = [d[0] for d in cur.description]; rows = cur.fetchall()
    w = [max(len(str(c)), *(len(str(r[i])) for r in rows)) if rows else len(c) for i, c in enumerate(cols)]
    p(" | ".join(str(c).ljust(w[i]) for i, c in enumerate(cols))); p("-+-".join("-" * x for x in w))
    for r in rows: p(" | ".join(str(v).ljust(w[i]) for i, v in enumerate(r)))
    p(f"({len(rows)} filas)")
p("EVIDENCIA 4.7.1 - Base estructurada | fecha de ejecucion: " + datetime.datetime.now().strftime("%d-%m-%Y %H:%M"))
p(f"Motor: SQLite {sqlite3.sqlite_version} | Python {platform.python_version()}"); p("=" * 78)
conn.executescript(rd("01_schema.sql")); p("[1] Creacion de esquema: OK")
tablas = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY 1")]
p("    Tablas creadas (%d): %s" % (len(tablas), ", ".join(tablas)))
conn.executescript(rd("02_datos_ficticios.sql")); p("[2] Insercion de datos ficticios: OK")
for t in ("usuario", "rol", "permiso", "rol_permiso", "modulo_externo", "pagina", "auditoria"):
    p(f"    {t}: {conn.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]} filas")
for q in rd("03_consultas.sql").split("-- Q")[1:]:
    titulo, sql = q.split("\n", 1); p(); p("[3] Consulta Q" + titulo.strip()); tabla(conn.execute(sql))
p(); p("[4] Pruebas de integridad (cada intento debe ser RECHAZADO por el motor, salvo I10)")
H = "'2026-10-24 10:00:00'"
casos = [
 ("I1 Correo de usuario duplicado (UNIQUE)", f"INSERT INTO usuario (id_usuario,correo,nombres,apellidos,password_hash,creado_en) VALUES (9,'duena@rgbeauty.test','X','Y','h',{H})", False),
 ("I2 Asignar un rol inexistente (FK)", "INSERT INTO usuario_rol VALUES (2,99)", False),
 ("I3 Repetir permiso del mismo rol (PK compuesta)", "INSERT INTO rol_permiso VALUES (1,5)", False),
 ("I4 Pagina con slug repetido (UNIQUE)", f"INSERT INTO pagina VALUES (9,'inicio','Otra','BORRADOR',1,NULL,1,{H},NULL)", False),
 ("I5 Pagina con estado inexistente (CHECK)", f"INSERT INTO pagina VALUES (9,'x','X','ARCHIVADA',1,NULL,1,{H},NULL)", False),
 ("I6 Pagina PUBLICADA sin publicador (CHECK)", f"INSERT INTO pagina VALUES (9,'y','Y','PUBLICADA',2,NULL,1,{H},NULL)", False),
 ("I7 Modulo con timeout de 50.000 ms (CHECK)", "INSERT INTO modulo_externo VALUES (9,'otro','https://x.test','v1',50000,'ACTIVO',NULL)", False),
 ("I8 Token de recuperacion con hash repetido (UNIQUE)", f"INSERT INTO token_recuperacion VALUES (9,2,'a3f1c0de5b7a4c1e9d2f8b6a0c4e7d19a3f1c0de5b7a4c1e9d2f8b6a0c4e7d19',{H},0,{H})", False),
 ("I9 Intentos fallidos negativos (CHECK)", f"INSERT INTO usuario (id_usuario,correo,nombres,apellidos,password_hash,intentos_fallidos,creado_en) VALUES (9,'z@x.test','Z','Z','h',-1,{H})", False),
 ("I10 Pagina BORRADOR valida (debe ser ACEPTADA)", f"INSERT INTO pagina VALUES (9,'preguntas-frecuentes','Preguntas frecuentes','BORRADOR',2,NULL,1,{H},NULL)", True),
]
ok_total = True
for nombre, sql, debe_pasar in casos:
    try: conn.execute(sql); res = "ACEPTADO"; det = ""
    except sqlite3.Error as e: res = "RECHAZADO"; det = f"-> {type(e).__name__}: {e}"
    esp = "ACEPTADO" if debe_pasar else "RECHAZADO"
    p(f"    {nombre}\n        resultado: {res} (esperado: {esp}) {'[OK]' if res == esp else '[FALLA]'} {det}"); ok_total &= (res == esp)
p(); p("RESUMEN: " + ("todas las verificaciones de integridad se comportaron como se esperaba" if ok_total else "HAY FALLAS"))
open(os.path.join(base, "salidas", "sql_demo.txt"), "w", encoding="utf-8").write("\n".join(out)); sys.exit(0 if ok_total else 1)
