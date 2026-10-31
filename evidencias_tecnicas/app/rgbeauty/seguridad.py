"""Hash de claves, login con bloqueo, recuperacion de clave y tokens de servicio entre gateway y modulos."""
import hashlib, hmac, os, html, secrets
from datetime import datetime, timedelta
from .reglas import validar_password

ITERACIONES = 600_000
def hashear_password(clave, sal=None, iteraciones=ITERACIONES):
    sal = sal or os.urandom(16).hex()
    return f"pbkdf2_sha256${iteraciones}${sal}${hashlib.pbkdf2_hmac('sha256', clave.encode(), sal.encode(), iteraciones).hex()}"
def verificar_password(clave, almacenado):
    try:
        _, it, sal, h = almacenado.split("$")
        return hmac.compare_digest(hashlib.pbkdf2_hmac("sha256", clave.encode(), sal.encode(), int(it)).hex(), h)
    except Exception: return False
def escapar_salida(t): return html.escape(t, quote=True)

MAX_INTENTOS, BLOQUEO_MIN = 5, 15
def login_vulnerable(conn, correo):
    """MAL EJEMPLO (solo para demostrar el riesgo): concatena la entrada en el SQL."""
    return conn.execute("SELECT id_usuario FROM usuario WHERE correo = '" + correo + "'").fetchall()
def buscar_usuario_seguro(conn, correo):
    return conn.execute("SELECT id_usuario, password_hash, intentos_fallidos, bloqueado_hasta FROM usuario WHERE correo = ? AND activo = 1", (correo,)).fetchone()
def intentar_login(conn, correo, clave, ahora):
    G = "Credenciales invalidas"; u = buscar_usuario_seguro(conn, correo)
    if u is None: return False, G
    uid, h, intentos, bloq = u
    if bloq and ahora < datetime.fromisoformat(bloq): return False, "Cuenta bloqueada temporalmente"
    if verificar_password(clave, h):
        conn.execute("UPDATE usuario SET intentos_fallidos=0, bloqueado_hasta=NULL, ultimo_login=? WHERE id_usuario=?", (ahora.strftime("%Y-%m-%d %H:%M:%S"), uid)); return True, "ok"
    intentos += 1
    hasta = (ahora + timedelta(minutes=BLOQUEO_MIN)).strftime("%Y-%m-%d %H:%M:%S") if intentos >= MAX_INTENTOS else None
    conn.execute("UPDATE usuario SET intentos_fallidos=?, bloqueado_hasta=? WHERE id_usuario=?", (intentos, hasta, uid)); return False, G

MENSAJE_RECUPERACION = "Si el correo existe, te enviamos un enlace para restablecer tu contrasena."
def solicitar_recuperacion(conn, correo, ahora):
    """Devuelve (mensaje_para_el_usuario, token_para_enviar_por_correo_o_None). El mensaje es identico exista o no la cuenta."""
    u = conn.execute("SELECT id_usuario FROM usuario WHERE correo=? AND activo=1", (correo,)).fetchone()
    if not u: return MENSAJE_RECUPERACION, None
    raw = secrets.token_urlsafe(32)
    conn.execute("INSERT INTO token_recuperacion (id_usuario,hash_token,expira_en,usado,creado_en) VALUES (?,?,?,0,?)",
                 (u[0], hashlib.sha256(raw.encode()).hexdigest(), (ahora + timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S"), ahora.strftime("%Y-%m-%d %H:%M:%S")))
    return MENSAJE_RECUPERACION, raw
def usar_token_recuperacion(conn, raw, nueva_clave, ahora):
    f = conn.execute("SELECT id_token,id_usuario,expira_en,usado FROM token_recuperacion WHERE hash_token=?", (hashlib.sha256(raw.encode()).hexdigest(),)).fetchone()
    if not f or f[3] or ahora > datetime.fromisoformat(f[2]): return False
    correo = conn.execute("SELECT correo FROM usuario WHERE id_usuario=?", (f[1],)).fetchone()[0]
    if validar_password(nueva_clave, correo): return False
    conn.execute("UPDATE usuario SET password_hash=?, intentos_fallidos=0, bloqueado_hasta=NULL WHERE id_usuario=?", (hashear_password(nueva_clave), f[1]))
    conn.execute("UPDATE token_recuperacion SET usado=1 WHERE id_token=?", (f[0],)); return True

class TokenInvalido(Exception): pass
def emitir_token_servicio(sub, rol, secreto, ahora, ttl_s=60):
    cuerpo = f"{sub}|{rol}|{int((ahora + timedelta(seconds=ttl_s)).timestamp())}"
    return cuerpo + "|" + hmac.new(secreto.encode(), cuerpo.encode(), hashlib.sha256).hexdigest()
def verificar_token_servicio(token, secreto, ahora):
    try: sub, rol, exp, firma = token.split("|")
    except Exception: raise TokenInvalido("formato")
    esperado = hmac.new(secreto.encode(), f"{sub}|{rol}|{exp}".encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(esperado, firma): raise TokenInvalido("firma")
    if ahora.timestamp() > int(exp): raise TokenInvalido("expirado")
    return {"sub": sub, "rol": rol}
