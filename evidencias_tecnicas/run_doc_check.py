"""Verificacion LOCAL de coherencia de los JSON (no reemplaza la ejecucion en MongoDB)."""
import json, os, sqlite3, datetime
b = os.path.dirname(os.path.abspath(__file__)); out = []
def p(s=""): out.append(s); print(s)
c = sqlite3.connect(":memory:")
for f in ("01_schema.sql", "02_datos_ficticios.sql"): c.executescript(open(f"{b}/sql/{f}", encoding="utf-8").read())
cp = json.load(open(f"{b}/mongo/contenido_pagina.json", encoding="utf-8")); ev = json.load(open(f"{b}/mongo/eventos_integracion.json", encoding="utf-8"))
p("EVIDENCIA 4.7.1 - Documentos no estructurados | fecha: " + datetime.datetime.now().strftime("%d-%m-%Y %H:%M"))
p(f"Colecciones: contenido_pagina ({len(cp)} documentos), eventos_integracion ({len(ev)} documentos)")
p("NOTA: verificacion local en Python; la insercion/consulta en MongoDB se evidencia con mongosh (consultas_mongosh.js)."); p("=" * 78)
p("C1 find({'bloques.boton.destino.modulo':'citas'}):")
for d in cp:
    if any(bl.get("boton", {}).get("destino", {}).get("modulo") == "citas" for bl in d["bloques"]): p(f"   {d['_id']} | {d['slug']} | version {d['version']}")
p("C2 find({resultado:{$ne:'OK'}}) ordenado por inicio desc:")
for d in sorted((d for d in ev if d["resultado"] != "OK"), key=lambda d: d["inicio"], reverse=True): p(f"   {d['_id']} | {d['modulo']} | {d['resultado']} | {d['duracion_ms']} ms")
p("C3 aggregate por modulo y resultado:")
cnt = {}
for d in ev: cnt[(d["modulo"], d["resultado"])] = cnt.get((d["modulo"], d["resultado"]), 0) + 1
for k, v in cnt.items(): p(f"   {k[0]} / {k[1]}: {v}")
p("Integridad referencial entre almacenes (documental -> relacional):"); ok = True
for d in cp:
    r = c.execute("SELECT slug FROM pagina WHERE id_pagina=?", (d["id_pagina"],)).fetchone(); good = bool(r and r[0] == d["slug"]); ok &= good
    p(f"   {d['_id']}: pagina {d['id_pagina']} ({d['slug']}) {'OK' if good else 'INCONSISTENTE'}")
    u = c.execute("SELECT 1 FROM usuario WHERE id_usuario=?", (d["actualizado_por"],)).fetchone(); ok &= bool(u); p(f"      actualizado_por {d['actualizado_por']} {'OK' if u else 'NO EXISTE'}")
for d in ev:
    m = c.execute("SELECT 1 FROM modulo_externo WHERE nombre=?", (d["modulo"],)).fetchone(); ok &= bool(m); p(f"   {d['_id']}: modulo {d['modulo']} {'OK' if m else 'NO REGISTRADO'}")
p("RESUMEN: " + ("referencias coherentes con el modelo relacional" if ok else "HAY INCONSISTENCIAS"))
open(f"{b}/salidas/documental_check.txt", "w", encoding="utf-8").write("\n".join(out))
