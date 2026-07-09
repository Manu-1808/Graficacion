import numpy as np
import pygame


def normalizar(v):
    # esta funcion deja los vectores con tamaño uno.
    # asi se pueden comparar y usar mejor en los calculos.
    v = np.asarray(v, dtype=float)
    norma = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.where(norma > 0, norma, 1)


def modelo_phong(N, L, V, ka=0.1, kd=0.6, ks=0.4, n=32):
    # este modelo mide como se ve la luz en la superficie.
    # combina luz ambiental, difusa y especular para dar efecto.

    N = normalizar(N)
    L = normalizar(L)
    V = normalizar(V)

    dot_nl = np.sum(N * L, axis=-1)
    dot_nl = np.maximum(dot_nl, 0)

    R = normalizar(
        2 * dot_nl[..., np.newaxis] * N - L
    )

    dot_rv = np.sum(R * V, axis=-1)
    dot_rv = np.maximum(dot_rv, 0)

    return ka + kd * dot_nl + ks * (dot_rv ** n)


def baricentrica_vectorizada(X, Y, A, B, C):
    v0 = B - A
    v1 = C - A

    v2x = X - A[0]
    v2y = Y - A[1]

    d00 = np.dot(v0, v0)
    d01 = np.dot(v0, v1)
    d11 = np.dot(v1, v1)

    d20 = v2x * v0[0] + v2y * v0[1]
    d21 = v2x * v1[0] + v2y * v1[1]

    denom = d00 * d11 - d01 * d01

    if abs(denom) < 1e-8:
        u = np.zeros_like(X, dtype=float)
        v = np.zeros_like(X, dtype=float)
        w = np.zeros_like(X, dtype=float)
        return u, v, w

    v = (d11 * d20 - d01 * d21) / denom
    w = (d00 * d21 - d01 * d20) / denom
    u = 1.0 - v - w

    return u, v, w


def colorizar_intensidad(intensidad):
    i = np.clip(intensidad, 0, 1)

    r = np.clip(40 + 230 * i, 0, 255)
    g = np.clip(20 + 120 * (i ** 0.8), 0, 255)
    b = np.clip(90 + 140 * (1 - i) + 50 * i, 0, 255)

    rgb = np.stack([r, g, b], axis=-1)
    return rgb.astype(np.uint8)


class EstadoSombreadoInteractivo:

    def __init__(self, resolucion=260):
        self.resolucion = resolucion

        # Triángulo en coordenadas internas de la imagen.
        self.A = np.array([35.0, 40.0])
        self.B = np.array([225.0, 70.0])
        self.C = np.array([130.0, 225.0])

        # Normales en cada vértice.
        self.NA = normalizar(np.array([-1.0, -1.0, 1.0]))
        self.NB = normalizar(np.array([1.0, -1.0, 1.0]))
        self.NC = normalizar(np.array([0.0, 1.0, 1.0]))

        # Luz y cámara/observador.
        self.luz = np.array([130.0, 80.0, 220.0])
        self.vista = np.array([130.0, 130.0, 400.0])

        # Coeficientes de iluminación.
        self.ka = 0.12
        self.kd = 0.62
        self.ks = 0.42
        self.brillo_n = 32

        # Interacción.
        self.vertice_arrastrando = None
        self.ultima_pos_luz_2d = (130, 80)

        # Renderizado.
        self.img_gouraud = None
        self.img_phong = None
        self.surface_gouraud = None
        self.surface_phong = None
        self.dirty = True

        # Rectángulos de dibujo, se actualizan al dibujar.
        self.rect_gouraud = None
        self.rect_phong = None
        self.escala_dibujo = 1.0

    def puntos(self):
        return [self.A, self.B, self.C]

    def normales(self):
        return [self.NA, self.NB, self.NC]

    def reiniciar(self):
        nuevo = EstadoSombreadoInteractivo(self.resolucion)
        self.__dict__.update(nuevo.__dict__)

    def marcar_dirty(self):
        self.dirty = True

    def mover_luz_desde_lienzo(self, pos_local):
        if self.rect_gouraud and self.rect_gouraud.collidepoint(pos_local):
            x = (pos_local[0] - self.rect_gouraud.x) / max(1, self.escala_dibujo)
            y = (pos_local[1] - self.rect_gouraud.y) / max(1, self.escala_dibujo)
        elif self.rect_phong and self.rect_phong.collidepoint(pos_local):
            x = (pos_local[0] - self.rect_phong.x) / max(1, self.escala_dibujo)
            y = (pos_local[1] - self.rect_phong.y) / max(1, self.escala_dibujo)
        else:
            # Si está fuera de los paneles, usa la posición relativa general.
            x = pos_local[0]
            y = pos_local[1]

        x = float(np.clip(x, 0, self.resolucion - 1))
        y = float(np.clip(y, 0, self.resolucion - 1))

        self.luz[0] = x
        self.luz[1] = y
        self.ultima_pos_luz_2d = (int(x), int(y))
        self.marcar_dirty()

    def iniciar_arrastre_vertice(self, pos_local):
        """Detecta si se hizo click cerca de un vértice."""
        punto_img = self._convertir_pos_a_img(pos_local)
        if punto_img is None:
            return False

        vertices = self.puntos()
        distancias = [np.linalg.norm(v - punto_img) for v in vertices]
        idx = int(np.argmin(distancias))

        if distancias[idx] <= 14:
            self.vertice_arrastrando = idx
            return True

        return False

    def arrastrar_vertice(self, pos_local):
        if self.vertice_arrastrando is None:
            return

        punto_img = self._convertir_pos_a_img(pos_local)
        if punto_img is None:
            return

        punto_img[0] = np.clip(punto_img[0], 8, self.resolucion - 8)
        punto_img[1] = np.clip(punto_img[1], 8, self.resolucion - 8)

        if self.vertice_arrastrando == 0:
            self.A = punto_img
        elif self.vertice_arrastrando == 1:
            self.B = punto_img
        elif self.vertice_arrastrando == 2:
            self.C = punto_img

        self.marcar_dirty()

    def terminar_arrastre(self):
        self.vertice_arrastrando = None

    def cambiar_brillo(self, delta):
        self.brillo_n = int(np.clip(self.brillo_n + delta, 4, 128))
        self.marcar_dirty()

    def _convertir_pos_a_img(self, pos_local):
        if self.rect_gouraud and self.rect_gouraud.collidepoint(pos_local):
            return np.array([
                (pos_local[0] - self.rect_gouraud.x) / max(1, self.escala_dibujo),
                (pos_local[1] - self.rect_gouraud.y) / max(1, self.escala_dibujo)
            ], dtype=float)

        if self.rect_phong and self.rect_phong.collidepoint(pos_local):
            return np.array([
                (pos_local[0] - self.rect_phong.x) / max(1, self.escala_dibujo),
                (pos_local[1] - self.rect_phong.y) / max(1, self.escala_dibujo)
            ], dtype=float)

        return None

    def recalcular(self):
        # aqui se generan las dos imagenes para comparar los estilos.
        res = self.resolucion
        A, B, C = self.A, self.B, self.C
        NA, NB, NC = self.NA, self.NB, self.NC

        xs = np.arange(res)
        ys = np.arange(res)
        X, Y = np.meshgrid(xs, ys)

        u, v, w = baricentrica_vectorizada(X, Y, A, B, C)
        mascara = (u >= 0) & (v >= 0) & (w >= 0)

        fondo = np.zeros((res, res), dtype=float)
        img_gouraud = fondo.copy()
        img_phong = fondo.copy()

        # Intensidad en los vértices para Gouraud.
        PA = np.array([A[0], A[1], 0.0])
        PB = np.array([B[0], B[1], 0.0])
        PC = np.array([C[0], C[1], 0.0])

        IA = modelo_phong(NA, self.luz - PA, self.vista - PA,
                          self.ka, self.kd, self.ks, self.brillo_n)
        IB = modelo_phong(NB, self.luz - PB, self.vista - PB,
                          self.ka, self.kd, self.ks, self.brillo_n)
        IC = modelo_phong(NC, self.luz - PC, self.vista - PC,
                          self.ka, self.kd, self.ks, self.brillo_n)

        img_gouraud[mascara] = (
            u[mascara] * IA +
            v[mascara] * IB +
            w[mascara] * IC
        )

        # Phong: interpola normales y calcula luz por píxel.
        N_interp = (
            u[..., np.newaxis] * NA +
            v[..., np.newaxis] * NB +
            w[..., np.newaxis] * NC
        )
        N_interp = normalizar(N_interp)

        pos_pixeles = np.stack(
            [X.astype(float), Y.astype(float), np.zeros_like(X, dtype=float)],
            axis=-1
        )

        L = self.luz.reshape(1, 1, 3) - pos_pixeles
        V = self.vista.reshape(1, 1, 3) - pos_pixeles

        intensidad_phong = modelo_phong(
            N_interp,
            L,
            V,
            self.ka,
            self.kd,
            self.ks,
            self.brillo_n
        )

        img_phong[mascara] = intensidad_phong[mascara]

        # Normalización visual suave.
        maximo = max(float(img_gouraud.max()), float(img_phong.max()), 1.0)
        img_gouraud = np.clip(img_gouraud / maximo, 0, 1)
        img_phong = np.clip(img_phong / maximo, 0, 1)

        self.img_gouraud = img_gouraud
        self.img_phong = img_phong

        rgb_g = colorizar_intensidad(img_gouraud)
        rgb_p = colorizar_intensidad(img_phong)

        # pygame.surfarray usa orientación (ancho, alto, canales).
        self.surface_gouraud = pygame.surfarray.make_surface(np.transpose(rgb_g, (1, 0, 2)))
        self.surface_phong = pygame.surfarray.make_surface(np.transpose(rgb_p, (1, 0, 2)))

        self.dirty = False

    def obtener_intensidades_vertices(self):
        A, B, C = self.A, self.B, self.C
        NA, NB, NC = self.NA, self.NB, self.NC

        PA = np.array([A[0], A[1], 0.0])
        PB = np.array([B[0], B[1], 0.0])
        PC = np.array([C[0], C[1], 0.0])

        ia = modelo_phong(NA, self.luz - PA, self.vista - PA,
                          self.ka, self.kd, self.ks, self.brillo_n)
        ib = modelo_phong(NB, self.luz - PB, self.vista - PB,
                          self.ka, self.kd, self.ks, self.brillo_n)
        ic = modelo_phong(NC, self.luz - PC, self.vista - PC,
                          self.ka, self.kd, self.ks, self.brillo_n)
        return ia, ib, ic


def dibujar_sombreado_interactivo(superficie, estado, CONFIG, fuente=None):
    if estado.dirty or estado.surface_gouraud is None or estado.surface_phong is None:
        estado.recalcular()

    ancho = CONFIG['ANCHO_LIENZO']
    alto = CONFIG['ALTO_LIENZO']

    margen = 30
    espacio = 35
    alto_titulo = 70
    alto_instrucciones = 90

    tam = min(
        (ancho - 2 * margen - espacio) // 2,
        alto - alto_titulo - alto_instrucciones
    )
    tam = max(180, int(tam))

    x1 = margen
    y1 = alto_titulo
    x2 = margen + tam + espacio
    y2 = alto_titulo

    estado.rect_gouraud = pygame.Rect(x1, y1, tam, tam)
    estado.rect_phong = pygame.Rect(x2, y2, tam, tam)
    estado.escala_dibujo = tam / estado.resolucion

    surf_g = pygame.transform.smoothscale(estado.surface_gouraud, (tam, tam))
    surf_p = pygame.transform.smoothscale(estado.surface_phong, (tam, tam))

    superficie.blit(surf_g, estado.rect_gouraud)
    superficie.blit(surf_p, estado.rect_phong)

    # Marcos.
    pygame.draw.rect(superficie, (80, 80, 90), estado.rect_gouraud, 2)
    pygame.draw.rect(superficie, (80, 80, 90), estado.rect_phong, 2)

    fuente_titulo = fuente or pygame.font.SysFont("Consolas", 20, bold=True)
    fuente_txt = pygame.font.SysFont("Consolas", 16)
    fuente_peq = pygame.font.SysFont("Consolas", 14)

    titulo = fuente_titulo.render("Comparación interactiva: Gouraud vs Phong", True, (255, 220, 150))
    superficie.blit(titulo, (margen, 18))

    subtitulo = fuente_txt.render(
        "Mueve la luz y compara cómo cambia el sombreado en ambos modelos.",
        True,
        (210, 210, 210)
    )
    superficie.blit(subtitulo, (margen, 43))

    etiqueta_g = fuente_titulo.render("Gouraud", True, (255, 255, 255))
    etiqueta_p = fuente_titulo.render("Phong", True, (255, 255, 255))
    superficie.blit(etiqueta_g, (x1 + 10, y1 - 30))
    superficie.blit(etiqueta_p, (x2 + 10, y2 - 30))

    desc_g = fuente_peq.render("Luz calculada en vértices", True, (190, 190, 190))
    desc_p = fuente_peq.render("Luz calculada por píxel", True, (190, 190, 190))
    superficie.blit(desc_g, (x1 + 105, y1 - 25))
    superficie.blit(desc_p, (x2 + 85, y2 - 25))

    _dibujar_guias(superficie, estado, estado.rect_gouraud, fuente_peq)
    _dibujar_guias(superficie, estado, estado.rect_phong, fuente_peq)

    # Indicador de luz.
    _dibujar_luz(superficie, estado, estado.rect_gouraud)
    _dibujar_luz(superficie, estado, estado.rect_phong)

    # Instrucciones.
    base_y = y1 + tam + 22
    instrucciones = [
        "Mouse sobre los cuadros: mueve la luz.",
        "Arrastra A, B o C: cambia el triángulo.",
        f"Rueda del mouse: brillo especular n = {estado.brillo_n}.",
    ]

    for i, linea in enumerate(instrucciones):
        txt = fuente_txt.render(linea, True, (210, 210, 210))
        superficie.blit(txt, (margen, base_y + i * 24))

    ia, ib, ic = estado.obtener_intensidades_vertices()
    datos = f"Intensidad en vértices: A={ia:.2f}  B={ib:.2f}  C={ic:.2f}"
    txt_datos = fuente_txt.render(datos, True, (150, 255, 180))
    superficie.blit(txt_datos, (margen + 390, base_y + 24))


def _dibujar_guias(superficie, estado, rect, fuente):
    escala = estado.escala_dibujo
    puntos = []
    nombres = ["A", "B", "C"]

    for p in estado.puntos():
        puntos.append((
            int(rect.x + p[0] * escala),
            int(rect.y + p[1] * escala)
        ))

    if len(puntos) == 3:
        pygame.draw.lines(superficie, (240, 240, 240), True, puntos, 2)

    for i, p in enumerate(puntos):
        color = (255, 220, 100) if estado.vertice_arrastrando == i else (120, 255, 160)
        pygame.draw.circle(superficie, color, p, 7)
        pygame.draw.circle(superficie, (20, 20, 20), p, 7, 2)

        etiqueta = fuente.render(nombres[i], True, (255, 255, 255))
        superficie.blit(etiqueta, (p[0] + 9, p[1] - 8))


def _dibujar_luz(superficie, estado, rect):
    escala = estado.escala_dibujo
    lx = int(rect.x + estado.luz[0] * escala)
    ly = int(rect.y + estado.luz[1] * escala)

    for r in range(18, 4, -4):
        glow = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 255, 180, max(25, 120 - r * 4)), (r + 1, r + 1), r)
        superficie.blit(glow, (lx - r - 1, ly - r - 1))

    pygame.draw.circle(superficie, (255, 255, 190), (lx, ly), 6)
    pygame.draw.circle(superficie, (255, 255, 255), (lx, ly), 3)


def manejar_clic_sombreado(evento, estado, CONFIG):
    mouse_x, mouse_y = evento.pos
    local = (mouse_x - CONFIG['ANCHO_HERRAMIENTAS'], mouse_y)

    if evento.button == 1:
        estado.iniciar_arrastre_vertice(local)
        estado.mover_luz_desde_lienzo(local)

    elif evento.button == 4:
        estado.cambiar_brillo(4)

    elif evento.button == 5:
        estado.cambiar_brillo(-4)


def manejar_movimiento_sombreado(evento, estado, CONFIG):
    mouse_x, mouse_y = evento.pos
    local = (mouse_x - CONFIG['ANCHO_HERRAMIENTAS'], mouse_y)

    if estado.vertice_arrastrando is not None:
        estado.arrastrar_vertice(local)
    else:
        estado.mover_luz_desde_lienzo(local)


def manejar_soltar_sombreado(estado):
    estado.terminar_arrastre()


def explicacion_sombreado(estado):
    """Explicación simple para el panel lateral."""
    ia, ib, ic = estado.obtener_intensidades_vertices()
    lx, ly, lz = estado.luz

    return {
        "titulo": "▸ Gouraud vs Phong · Sombreado interactivo",
        "color": (255, 190, 120),
        "lineas": [
            {"texto": "▸ ¿QUÉ ESTÁS VIENDO?", "color": (255, 200, 100)},
            {"texto": "  El mismo triángulo se ilumina de dos maneras.", "color": (220, 220, 220)},
            {"texto": "  A la izquierda está Gouraud.", "color": (220, 220, 220)},
            {"texto": "  A la derecha está Phong.", "color": (220, 220, 220)},
            {"texto": "", "color": (220, 220, 220)},

            {"texto": "▸ IDEA SIMPLE", "color": (255, 200, 100)},
            {"texto": "  Imagina que una lámpara ilumina una cartulina.", "color": (220, 220, 220)},
            {"texto": "  Según dónde esté la lámpara, unas zonas se", "color": (220, 220, 220)},
            {"texto": "  ven más claras y otras más oscuras.", "color": (220, 220, 220)},
            {"texto": "", "color": (220, 220, 220)},

            {"texto": "▸ GOURAUD", "color": (150, 220, 255)},
            {"texto": "  Calcula la luz solo en las esquinas del", "color": (220, 220, 220)},
            {"texto": "  triángulo: A, B y C.", "color": (220, 220, 220)},
            {"texto": "  Luego mezcla esos valores hacia el centro.", "color": (220, 220, 220)},
            {"texto": "  Es más rápido, pero puede perder brillos finos.", "color": (220, 220, 220)},
            {"texto": "", "color": (220, 220, 220)},

            {"texto": "▸ PHONG", "color": (150, 255, 180)},
            {"texto": "  En vez de mezclar solo la luz, mezcla la", "color": (220, 220, 220)},
            {"texto": "  dirección de la superficie y calcula la", "color": (220, 220, 220)},
            {"texto": "  iluminación en cada píxel.", "color": (220, 220, 220)},
            {"texto": "  Es más preciso, pero requiere más cálculo.", "color": (220, 220, 220)},
            {"texto": "", "color": (220, 220, 220)},

            {"texto": "▸ FÓRMULA DE LUZ", "color": (255, 200, 100)},
            {"texto": "  I = ka + kd·max(0, N·L) + ks·max(0, R·V)^n", "color": (255, 255, 150)},
            {"texto": "  ka: luz mínima del ambiente.", "color": (220, 220, 220)},
            {"texto": "  kd: luz difusa, depende del ángulo.", "color": (220, 220, 220)},
            {"texto": "  ks: brillo especular o reflejo.", "color": (220, 220, 220)},
            {"texto": "", "color": (220, 220, 220)},

            {"texto": "▸ ESTADO ACTUAL", "color": (255, 200, 100)},
            {"texto": f"  Luz: x={lx:.0f}, y={ly:.0f}, z={lz:.0f}", "color": (150, 255, 150)},
            {"texto": f"  Brillo especular n = {estado.brillo_n}", "color": (150, 255, 150)},
            {"texto": f"  Intensidades: A={ia:.2f}, B={ib:.2f}, C={ic:.2f}", "color": (150, 255, 150)},
            {"texto": "", "color": (220, 220, 220)},

            {"texto": "▸ CÓMO JUGAR", "color": (255, 200, 100)},
            {"texto": "  Mueve el mouse: cambia la luz.", "color": (220, 220, 220)},
            {"texto": "  Arrastra A, B o C: cambia el triángulo.", "color": (220, 220, 220)},
            {"texto": "  Rueda del mouse: cambia el brillo.", "color": (220, 220, 220)},
        ]
    }
