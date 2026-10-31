"""RBAC desde la base de datos, cambio de estado de paginas y auditoria."""
from .reglas import PermisoDenegado, ReglaNegocioError, permiso_requerido
FMT = "%Y-%m-%d %H:%M:%S"
def permisos_de(conn, id_usuario):
    return {r[0] for r in conn.execute("SELECT DISTINCT p.codigo FROM usuario u JOIN usuario_rol ur ON ur.id_usuario=u.id_usuario JOIN rol_permiso rp ON rp.id_rol=ur.id_rol JOIN permiso p ON p.id_permiso=rp.id_permiso WHERE u.id_usuario=? AND u.activo=1", (id_usuario,))}
def puede(conn, id_usuario, codigo): return codigo in permisos_de(conn, id_usuario)
def exigir(conn, id_usuario, codigo):
    if not puede(conn, id_usuario, codigo): raise PermisoDenegado(codigo)
def auditar(conn, id_usuario, accion, entidad, id_ent, detalle, ahora, ip="n/a"):
    conn.execute("INSERT INTO auditoria (id_usuario,accion,entidad,id_entidad,detalle,ip_origen,fecha) VALUES (?,?,?,?,?,?,?)", (id_usuario, accion, entidad, id_ent, detalle, ip, ahora.strftime(FMT)))
def cambiar_estado_pagina(conn, id_usuario, id_pagina, nuevo, ahora):
    actual = conn.execute("SELECT estado FROM pagina WHERE id_pagina=?", (id_pagina,)).fetchone()[0]
    try: req = permiso_requerido(actual, nuevo)
    except ReglaNegocioError: auditar(conn, id_usuario, "TRANSICION_RECHAZADA", "pagina", id_pagina, f"{actual}->{nuevo}", ahora); raise
    try: exigir(conn, id_usuario, req)
    except PermisoDenegado: auditar(conn, id_usuario, "ACCESO_DENEGADO", "pagina", id_pagina, f"{actual}->{nuevo} requiere {req}", ahora); raise
    pub = (id_usuario, ahora.strftime(FMT)) if nuevo == "PUBLICADA" else (None, None)
    conn.execute("UPDATE pagina SET estado=?, id_publicador=?, publicada_en=?, version=version+1 WHERE id_pagina=?", (nuevo, pub[0], pub[1], id_pagina))
    auditar(conn, id_usuario, "PAGINA_" + nuevo, "pagina", id_pagina, f"{actual}->{nuevo}", ahora)
def editar_titulo_pagina(conn, id_usuario, id_pagina, titulo, ahora):
    exigir(conn, id_usuario, "CONTENIDO_EDITAR")
    if conn.execute("SELECT estado FROM pagina WHERE id_pagina=?", (id_pagina,)).fetchone()[0] == "PUBLICADA": raise ReglaNegocioError("despublicar antes de editar")
    conn.execute("UPDATE pagina SET titulo=? WHERE id_pagina=?", (titulo, id_pagina)); auditar(conn, id_usuario, "EDITAR_PAGINA", "pagina", id_pagina, "titulo", ahora)
def cambiar_precio(conn, id_usuario, id_producto, precio, ahora):
    exigir(conn, id_usuario, "PRECIO_EDITAR"); auditar(conn, id_usuario, "CAMBIO_PRECIO", "producto", id_producto, f"nuevo precio {precio}", ahora)
def obtener_pagina_publica(conn, slug):
    return conn.execute("SELECT slug,titulo FROM pagina WHERE slug=? AND estado='PUBLICADA'", (slug,)).fetchone()
