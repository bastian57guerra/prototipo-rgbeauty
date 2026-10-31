"""Validaciones y reglas de negocio del sitio web (RG Beauty Spa)."""
import html, re, unicodedata
from html.parser import HTMLParser

class ReglaNegocioError(ValueError): pass
class PermisoDenegado(Exception): pass

def _dv_rut(cuerpo):
    suma, mult = 0, 2
    for d in reversed(cuerpo):
        suma += int(d) * mult; mult = 2 if mult == 7 else mult + 1
    r = 11 - (suma % 11)
    return "0" if r == 11 else "K" if r == 10 else str(r)

def validar_rut(rut):
    if not isinstance(rut, str): return False
    limpio = rut.replace(".", "").replace("-", "").strip().upper()
    return re.fullmatch(r"\d{7,8}[\dK]", limpio) is not None and _dv_rut(limpio[:-1]) == limpio[-1]

def validar_telefono_cl(tel):
    return re.fullmatch(r"(\+?56)?9\d{8}", re.sub(r"[\s\-]", "", tel or "")) is not None

def validar_correo(correo):
    return isinstance(correo, str) and len(correo) <= 120 and re.fullmatch(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9\-]+(\.[A-Za-z0-9\-]+)*\.[A-Za-z]{2,}", correo) is not None

COMUNES = {"password123", "1234567890", "qwertyuiop", "contrasena1", "rgbeauty123", "admin12345", "abc1234567"}
def validar_password(clave, correo=""):
    """Devuelve la lista de problemas (vacia si la clave es aceptable)."""
    pr = []
    if not isinstance(clave, str) or len(clave) < 10: pr.append("minimo 10 caracteres")
    if isinstance(clave, str):
        if not re.search(r"[A-Za-z]", clave) or not re.search(r"\d", clave): pr.append("debe combinar letras y numeros")
        if clave.lower() in COMUNES: pr.append("clave demasiado comun")
        local = (correo or "").split("@")[0].lower()
        if len(local) >= 4 and local in clave.lower(): pr.append("no debe contener el correo")
    return pr

def slugify(titulo):
    t = unicodedata.normalize("NFKD", titulo).encode("ascii", "ignore").decode().lower()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", t)).strip("-")

PERMITIDAS = {"p", "b", "strong", "i", "em", "ul", "ol", "li", "a", "h2", "h3", "br"}
class _San(HTMLParser):
    def __init__(self): super().__init__(convert_charrefs=True); self.out = []; self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"): self.skip += 1; return
        if self.skip or tag not in PERMITIDAS: return
        if tag == "a":
            href = (dict(attrs).get("href") or "").strip()
            if href.lower().startswith(("http://", "https://", "mailto:", "/")): self.out.append(f'<a href="{html.escape(href, quote=True)}" rel="noopener noreferrer">')
            else: self.out.append("<a>")
        else: self.out.append(f"<{tag}>")
    def handle_endtag(self, tag):
        if tag in ("script", "style"): self.skip = max(0, self.skip - 1); return
        if not self.skip and tag in PERMITIDAS and tag != "br": self.out.append(f"</{tag}>")
    def handle_data(self, d):
        if not self.skip: self.out.append(html.escape(d))
def sanitizar_html(texto):
    p = _San(); p.feed(texto); p.close(); return "".join(p.out)

EXT_OK = {"jpg", "jpeg", "png", "webp"}; EXT_PELIGROSAS = {"php", "exe", "js", "html", "htm", "sh", "bat", "svg"}
def validar_archivo(nombre, datos, max_bytes=2_000_000):
    if not nombre or any(c in nombre for c in ("/", "\\", "\x00")) or ".." in nombre: return False, "nombre invalido"
    partes = nombre.lower().split(".")
    if len(partes) < 2: return False, "sin extension"
    if any(p in EXT_PELIGROSAS for p in partes[1:]): return False, "extension peligrosa"
    if partes[-1] not in EXT_OK: return False, "extension no permitida"
    if len(datos) > max_bytes: return False, "supera el tamano maximo"
    ext = partes[-1]
    firma_ok = (ext in ("jpg", "jpeg") and datos[:3] == b"\xff\xd8\xff") or (ext == "png" and datos[:8] == b"\x89PNG\r\n\x1a\n") or (ext == "webp" and datos[:4] == b"RIFF" and datos[8:12] == b"WEBP")
    return (True, "ok") if firma_ok else (False, "el contenido no corresponde a la extension")

TRANSICIONES = {("BORRADOR", "EN_REVISION"): "CONTENIDO_EDITAR", ("EN_REVISION", "PUBLICADA"): "CONTENIDO_PUBLICAR",
                ("EN_REVISION", "BORRADOR"): "CONTENIDO_PUBLICAR", ("PUBLICADA", "BORRADOR"): "CONTENIDO_PUBLICAR"}
def permiso_requerido(actual, nuevo):
    if (actual, nuevo) not in TRANSICIONES: raise ReglaNegocioError(f"transicion no permitida: {actual} -> {nuevo}")
    return TRANSICIONES[(actual, nuevo)]
