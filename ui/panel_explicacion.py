import pygame
import textwrap


class PanelExplicacion:
    """Panel lateral que muestra la explicación matemática del algoritmo activo.

    Soporta contenido más largo que el alto visible mediante scroll
    (rueda del mouse sobre el panel, o arrastrando la barra lateral).
    """

    def __init__(self, x, y, ancho, alto):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.datos = None
        self.fuente = None
        self.fuente_titulo = None
        self.fuente_pequena = None
        self.lineas_procesadas = []  # Lista de (texto, color)
        self.titulo = ""
        self.color_titulo = (255, 255, 255)
        self.color_borde = (100, 200, 255)
        self.margen = 16
        self.espaciado_linea = 24
        self.ancho_texto = ancho - (self.margen * 2) - 12  # deja espacio a la barra de scroll
        self.alto_titulo = 46

        # --- scroll ---
        self.scroll_y = 0
        self.alto_contenido = 0
        self.arrastrando_barra = False
        self.ancho_barra = 8

    # ------------------------------------------------------------------
    # Actualización de contenido
    # ------------------------------------------------------------------
    def actualizar(self, datos, fuente=None, reiniciar_scroll=True):
        """Actualiza el panel con los datos de explicación (dict o string)."""
        self.datos = datos
        self.lineas_procesadas = []
        self.titulo = ""
        self.color_titulo = (255, 200, 100)

        if fuente:
            self.fuente = fuente
            self.fuente_titulo = pygame.font.SysFont("Consolas", 20, bold=True)
            self.fuente_pequena = pygame.font.SysFont("Consolas", 15)

        if isinstance(datos, str):
            self._procesar_texto_str(datos)
        elif isinstance(datos, dict):
            self._procesar_texto_dict(datos)
        else:
            self.lineas_procesadas = [
                ("Selecciona un algoritmo", (150, 150, 150)),
                ("y ejecuta para ver la explicación", (120, 120, 120)),
            ]

        if reiniciar_scroll:
            self.scroll_y = 0

    def _procesar_texto_str(self, texto):
        lineas = texto.split('\n')
        for linea in lineas:
            if linea.strip():
                texto_limpio = self._limpiar_latex(linea)
                if 'textbf' in linea or (not self.titulo and len(linea) < 50):
                    self.titulo = texto_limpio
                    self.color_titulo = (255, 200, 100)
                else:
                    for sublinea in self._dividir_texto(texto_limpio):
                        self.lineas_procesadas.append((sublinea, (200, 200, 200)))

    def _procesar_texto_dict(self, datos):
        self.titulo = datos.get('titulo', '')
        self.color_titulo = (255, 200, 100)
        self.color_borde = datos.get('color', (100, 200, 255))

        for linea in datos.get('lineas', []):
            texto = linea.get('texto', '')
            color = linea.get('color', (220, 220, 220))

            if texto == '':
                self.lineas_procesadas.append(('', color))
                continue

            texto_limpio = self._limpiar_latex(texto)
            for sublinea in self._dividir_texto(texto_limpio):
                self.lineas_procesadas.append((sublinea, color))

    def _limpiar_latex(self, texto):
        """Convierte comandos tipo LaTeX a caracteres Unicode equivalentes."""
        import re

        reemplazos = {
            r'\Delta': 'Δ', r'\theta': 'θ', r'\Theta': 'Θ', r'\pi': 'π',
            r'\alpha': 'α', r'\beta': 'β', r'\gamma': 'γ',
            r'\cdot': '·', r'\times': '×',
            r'\leq': '≤', r'\geq': '≥', r'\neq': '≠',
            r'\rightarrow': '→', r'\leftarrow': '←',
            r'\in': '∈', r'\sum': 'Σ',
            r'\mathbf': '', r'\textbf': '', r'\textit': ''
        }
        for latex, uni in reemplazos.items():
            texto = texto.replace(latex, uni)

        subs = {
            '_0': '₀', '_1': '₁', '_2': '₂', '_3': '₃', '_4': '₄',
            '_5': '₅', '_6': '₆', '_7': '₇', '_8': '₈', '_9': '₉',
            '_x': 'ₓ', '_y': 'ᵧ'
        }
        for k, v in subs.items():
            texto = texto.replace(k, v)

        supers = {'^2': '²', '^3': '³'}
        for k, v in supers.items():
            texto = texto.replace(k, v)

        texto = texto.replace('$', '').replace('{', '').replace('}', '')
        texto = re.sub(r'\\[a-zA-Z]+', '', texto)
        return texto.strip()

    def _dividir_texto(self, texto):
        if not texto:
            return ['']
        if self.fuente and self.fuente.size(texto)[0] <= self.ancho_texto:
            return [texto]

        if self.fuente:
            ancho_promedio = self.fuente.size(' ')[0] * 1.2
            max_caracteres = max(10, int(self.ancho_texto / ancho_promedio))
        else:
            max_caracteres = 40

        return textwrap.wrap(texto, width=max_caracteres, break_long_words=False) or ['']

    # ------------------------------------------------------------------
    # Scroll
    # ------------------------------------------------------------------
    def _alto_visible(self):
        return self.rect.height - self.alto_titulo - 20

    def _max_scroll(self):
        return max(0, self.alto_contenido - self._alto_visible())

    def desplazar(self, delta_lineas):
        self.scroll_y -= delta_lineas * self.espaciado_linea * 3
        self.scroll_y = max(0, min(self.scroll_y, self._max_scroll()))

    def manejar_evento(self, evento):
        """Procesa eventos de mouse relacionados con el scroll. Devuelve True si los consumió."""
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if not self.rect.collidepoint(evento.pos):
                return False
            if evento.button == 4:
                self.desplazar(1)
                return True
            if evento.button == 5:
                self.desplazar(-1)
                return True
            if evento.button == 1 and self._max_scroll() > 0:
                barra_rect = self._rect_barra()
                if barra_rect and barra_rect.collidepoint(evento.pos):
                    self.arrastrando_barra = True
                    return True

        elif evento.type == pygame.MOUSEWHEEL:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                self.desplazar(evento.y)
                return True

        elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            self.arrastrando_barra = False

        elif evento.type == pygame.MOUSEMOTION and self.arrastrando_barra:
            alto_visible = self._alto_visible()
            proporcion = evento.rel[1] / max(1, alto_visible)
            self.scroll_y += proporcion * self.alto_contenido
            self.scroll_y = max(0, min(self.scroll_y, self._max_scroll()))
            return True

        return False

    def _rect_barra(self):
        max_scroll = self._max_scroll()
        alto_visible = self._alto_visible()
        if max_scroll <= 0 or self.alto_contenido <= 0:
            return None

        alto_barra = max(30, alto_visible * alto_visible / self.alto_contenido)
        y_top = self.rect.y + self.alto_titulo + 10
        y_barra = y_top + (self.scroll_y / max_scroll) * (alto_visible - alto_barra)

        return pygame.Rect(
            self.rect.right - self.ancho_barra - 4,
            int(y_barra),
            self.ancho_barra,
            int(alto_barra)
        )

    # ------------------------------------------------------------------
    # Dibujo
    # ------------------------------------------------------------------
    def dibujar(self, screen):
        pygame.draw.rect(screen, (30, 30, 35), self.rect)
        pygame.draw.rect(screen, (60, 60, 70), self.rect, 2)

        pygame.draw.line(
            screen, self.color_borde,
            (self.rect.x, self.rect.y),
            (self.rect.x + self.rect.width, self.rect.y),
            3
        )

        if not self.datos or (isinstance(self.datos, dict) and not self.datos.get('lineas')):
            if self.fuente:
                texto = self.fuente.render("Selecciona un algoritmo", True, (150, 150, 150))
                x = self.rect.x + (self.rect.width - texto.get_width()) // 2
                screen.blit(texto, (x, self.rect.y + 20))

                texto2 = self.fuente_pequena.render("y ejecuta para ver la explicación", True, (120, 120, 120))
                x = self.rect.x + (self.rect.width - texto2.get_width()) // 2
                screen.blit(texto2, (x, self.rect.y + 50))
            return

        # Área de recorte para que el scroll no dibuje fuera del panel
        area_clip = pygame.Rect(
            self.rect.x, self.rect.y + self.alto_titulo,
            self.rect.width, self.rect.height - self.alto_titulo
        )
        clip_anterior = screen.get_clip()
        screen.set_clip(area_clip)

        y_actual = self.rect.y + self.alto_titulo + 10 - self.scroll_y

        for texto, color in self.lineas_procesadas:
            if not texto:
                y_actual += 8
                continue
            if self.fuente:
                render = self.fuente.render(texto, True, color)
                screen.blit(render, (self.rect.x + self.margen, y_actual))
            y_actual += self.espaciado_linea

        self.alto_contenido = (y_actual + self.scroll_y) - (self.rect.y + self.alto_titulo + 10)

        screen.set_clip(clip_anterior)

        # Título (siempre fijo, encima del contenido con scroll)
        if self.titulo and self.fuente_titulo:
            titulo_limpio = self._limpiar_latex(self.titulo)
            titulo_render = self.fuente_titulo.render(titulo_limpio, True, self.color_titulo)
            screen.blit(titulo_render, (self.rect.x + self.margen, self.rect.y + 10))

            y_titulo = self.rect.y + 40
            pygame.draw.line(
                screen, (60, 60, 70),
                (self.rect.x + self.margen, y_titulo),
                (self.rect.x + self.rect.width - self.margen, y_titulo), 1
            )

        # Barra de scroll
        barra_rect = self._rect_barra()
        if barra_rect:
            pygame.draw.rect(screen, (70, 70, 80), barra_rect, border_radius=4)