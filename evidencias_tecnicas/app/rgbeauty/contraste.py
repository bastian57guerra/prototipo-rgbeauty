def _lin(c):
    c = c / 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
def luminancia(hexcol):
    h = hexcol.lstrip("#"); r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
    return 0.2126*_lin(r) + 0.7152*_lin(g) + 0.0722*_lin(b)
def ratio(fg, bg):
    a, b = sorted((luminancia(fg), luminancia(bg)), reverse=True)
    return (a + 0.05) / (b + 0.05)
# (descripcion, texto, fondo, minimo exigido WCAG 2.1 AA)
PARES = [
 ("Texto principal sobre blanco",            "#3A3A3A", "#FFFFFF", 4.5),
 ("Texto principal sobre beige de fondo",    "#3A3A3A", "#EFE7DD", 4.5),
 ("Texto de boton primario (blanco/vino)",   "#FFFFFF", "#8C4A57", 4.5),
 ("Enlaces y titulos vino sobre blanco",     "#8C4A57", "#FFFFFF", 4.5),
 ("Vino sobre beige",                        "#8C4A57", "#EFE7DD", 4.5),
 ("Rosa AD6B78 como borde de campo (UI)",    "#AD6B78", "#FFFFFF", 3.0),
 ("Mensaje de exito (verde oscuro/verde claro)", "#24511A", "#E4EFD6", 4.5),
 ("Mensaje de error (rojo/rosa palido)",     "#9F1D14", "#FDECEA", 4.5),
 ("Mensaje de aviso (ocre/crema)",           "#6B4200", "#FFF1D6", 4.5),
 ("Texto secundario gris sobre blanco",      "#595959", "#FFFFFF", 4.5),
 ("Horario ocupado (gris/gris claro)",       "#6B6B6B", "#EDEDED", 4.5),
]
# Usos PROHIBIDOS por la guia de estilo (decision tras la corrida 1 de PA-01): deben seguir sin cumplir AA,
# lo que justifica la prohibicion.
PROHIBIDOS = [("Rosa AD6B78 como texto sobre blanco", "#AD6B78", "#FFFFFF", 4.5)]
