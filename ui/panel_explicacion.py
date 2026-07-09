import pygame
import textwrap

try:
    from graficos.render_latex import renderizar_latex_a_surface
except Exception:
    renderizar_latex_a_surface = None


class PanelExplicacion:
    def __init__(self, x, y, ancho, alto):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.datos = None

        self.fuente = None
        self.fuente_titulo = None
        self.fuente_pequena = None
        self.fuente_seccion = None

        self.titulo = ""
        self.color_titulo = (255, 200, 100)
        self.color_borde = (100, 200, 255)

        self.margen = 16
        self.espaciado_linea = 24
        self.alto_titulo = 52
        self.ancho_barra = 8
        self.ancho_texto = ancho - (self.margen * 2) - 18

        self.scroll_y = 0
        self.alto_contenido = 0
        self.arrastrando_barra = False

        self.elementos = []

    def actualizar(self, datos, fuente=None, reiniciar_scroll=True):
        self.datos = datos
        self.elementos = []
        self.titulo = ""
        self.color_titulo = (255, 200, 100)
        self.color_borde = (100, 200, 255)

        if fuente:
            self.fuente = fuente
            self.fuente_titulo = pygame.font.SysFont("Consolas", 20, bold=True)
            self.fuente_seccion = pygame.font.SysFont("Consolas", 17, bold=True)
            self.fuente_pequena = pygame.font.SysFont("Consolas", 15)

        if isinstance(datos, str):
            self._procesar_texto_str(datos)
        elif isinstance(datos, dict):
            if "bloques" in datos:
                self._procesar_bloques(datos)
            else:
                self._procesar_formato_anterior(datos)
        else:
            self.titulo = "Explicación"
            self._agregar_texto("Selecciona un algoritmo para ver la explicación.", (150, 150, 150))

        if reiniciar_scroll:
            self.scroll_y = 0

    def _procesar_texto_str(self, texto):
        lineas = texto.split("\n")
        primera = True
        for linea in lineas:
            linea = linea.strip()
            if not linea:
                self._agregar_espacio(8)
                continue
            limpio = self._limpiar_latex(linea)
            if primera:
                self.titulo = limpio
                primera = False
            else:
                self._agregar_texto(limpio, (210, 210, 210))

    def _procesar_formato_anterior(self, datos):
        self.titulo = datos.get("titulo", "Explicación")
        self.color_borde = datos.get("color", (100, 200, 255))

        for linea in datos.get("lineas", []):
            texto = linea.get("texto", "")
            color = linea.get("color", (220, 220, 220))
            if not texto:
                self._agregar_espacio(8)
            else:
                self._agregar_texto(self._limpiar_latex(texto), color)

    def _procesar_bloques(self, datos):
        self.titulo = datos.get("titulo", "Explicación")
        self.color_borde = datos.get("color", (100, 200, 255))

        for bloque in datos.get("bloques", []):
            tipo = bloque.get("tipo", "texto")

            if tipo == "seccion":
                self._agregar_espacio(8)
                self._agregar_texto(
                    bloque.get("texto", ""),
                    bloque.get("color", (255, 200, 100)),
                    fuente_tipo="seccion",
                )

            elif tipo == "texto":
                self._agregar_texto(
                    bloque.get("texto", ""),
                    bloque.get("color", (215, 215, 215)),
                )

            elif tipo == "formula":
                self._agregar_formula(
                    bloque.get("latex", ""),
                    bloque.get("color", (255, 255, 210)),
                    bloque.get("fontsize", 18),
                )

            elif tipo == "matriz":
                self._agregar_matriz(
                    bloque.get("nombre", "M"),
                    bloque.get("filas", []),
                    bloque.get("color", (255, 255, 210)),
                )

            elif tipo == "resultado":
                self._agregar_texto(
                    bloque.get("texto", ""),
                    bloque.get("color", (150, 255, 150)),
                    fuente_tipo="seccion",
                )

            elif tipo == "alerta":
                self._agregar_texto(
                    bloque.get("texto", ""),
                    bloque.get("color", (255, 150, 150)),
                    fuente_tipo="seccion",
                )

            elif tipo == "espacio":
                self._agregar_espacio(bloque.get("alto", 10))

    def _agregar_texto(self, texto, color, fuente_tipo="normal"):
        if not texto:
            self._agregar_espacio(8)
            return

        for sublinea in self._dividir_texto(texto):
            self.elementos.append(("texto", sublinea, color, fuente_tipo))

    def _agregar_formula(self, latex, color=(255, 255, 210), fontsize=18):
        if not latex:
            return

        if renderizar_latex_a_surface is None:
            self._agregar_texto(latex, color)
            return

        fondo = (30, 30, 35)
        surface = renderizar_latex_a_surface(
            latex,
            color=color,
            fondo=fondo,
            fontsize=fontsize,
        )

        # Si la fórmula es más ancha que el panel, se escala proporcionalmente.
        max_ancho = self.ancho_texto
        if surface.get_width() > max_ancho:
            escala = max_ancho / surface.get_width()
            nuevo_tamano = (
                max(1, int(surface.get_width() * escala)),
                max(1, int(surface.get_height() * escala)),
            )
            surface = pygame.transform.smoothscale(surface, nuevo_tamano)

        self.elementos.append(("formula", surface))
        self._agregar_espacio(6)

    def _agregar_matriz(self, nombre, filas, color=(255, 255, 210)):
        if not filas:
            return

        filas_texto = []
        for fila in filas:
            filas_texto.append("   ".join(str(c) for c in fila))

        ancho_max = max(len(f) for f in filas_texto)
        lineas = []
        for i, fila in enumerate(filas_texto):
            contenido = fila.ljust(ancho_max)
            if len(filas_texto) == 1:
                linea = f"{nombre} = [ {contenido} ]"
            elif i == 0:
                linea = f"{nombre} = [ {contenido} ]"
            elif i == len(filas_texto) - 1:
                linea = f"    [ {contenido} ]"
            else:
                linea = f"    | {contenido} |"
            lineas.append(linea)

        self._agregar_espacio(4)
        for linea in lineas:
            self.elementos.append(("texto", linea, color, "seccion"))
        self._agregar_espacio(8)

    def _agregar_espacio(self, alto=8):
        self.elementos.append(("espacio", alto))

    def _fuente_por_tipo(self, fuente_tipo):
        if fuente_tipo == "seccion" and self.fuente_seccion:
            return self.fuente_seccion
        if fuente_tipo == "pequena" and self.fuente_pequena:
            return self.fuente_pequena
        return self.fuente

    def _dividir_texto(self, texto):
        if not texto:
            return [""]

        fuente = self.fuente or pygame.font.SysFont("Consolas", 18)
        if fuente.size(texto)[0] <= self.ancho_texto:
            return [texto]

        ancho_promedio = max(1, fuente.size("x")[0])
        max_caracteres = max(18, int(self.ancho_texto / ancho_promedio))
        return textwrap.wrap(texto, width=max_caracteres, break_long_words=False) or [texto]

    def _limpiar_latex(self, texto):
        """Mantiene compatibilidad con textos antiguos tipo LaTeX plano."""
        import re

        reemplazos = {
            r"\Delta": "Δ", r"\theta": "θ", r"\Theta": "Θ", r"\pi": "π",
            r"\alpha": "α", r"\beta": "β", r"\gamma": "γ",
            r"\cdot": "·", r"\times": "×",
            r"\leq": "≤", r"\geq": "≥", r"\neq": "≠",
            r"\rightarrow": "→", r"\leftarrow": "←",
            r"\sum": "Σ", r"\textbf": "", r"\textit": "",
        }
        for latex, uni in reemplazos.items():
            texto = texto.replace(latex, uni)

        texto = texto.replace("$", "").replace("{", "").replace("}", "")
        texto = re.sub(r"\\[a-zA-Z]+", "", texto)
        return texto.strip()


    def _alto_visible(self):
        return self.rect.height - self.alto_titulo - 20

    def _max_scroll(self):
        return max(0, self.alto_contenido - self._alto_visible())

    def desplazar(self, delta_lineas):
        self.scroll_y -= delta_lineas * self.espaciado_linea * 3
        self.scroll_y = max(0, min(self.scroll_y, self._max_scroll()))

    def manejar_evento(self, evento):
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
            int(alto_barra),
        )

    def dibujar(self, screen):
        pygame.draw.rect(screen, (30, 30, 35), self.rect)
        pygame.draw.rect(screen, (60, 60, 70), self.rect, 2)

        pygame.draw.line(
            screen,
            self.color_borde,
            (self.rect.x, self.rect.y),
            (self.rect.x + self.rect.width, self.rect.y),
            3,
        )

        if not self.datos:
            self._dibujar_vacio(screen)
            return

        self._dibujar_titulo(screen)

        area_clip = pygame.Rect(
            self.rect.x,
            self.rect.y + self.alto_titulo,
            self.rect.width,
            self.rect.height - self.alto_titulo,
        )

        clip_anterior = screen.get_clip()
        screen.set_clip(area_clip)

        y_actual = self.rect.y + self.alto_titulo + 10 - self.scroll_y
        x_base = self.rect.x + self.margen

        for elemento in self.elementos:
            tipo = elemento[0]

            if tipo == "espacio":
                y_actual += elemento[1]
                continue

            if tipo == "texto":
                _, texto, color, fuente_tipo = elemento
                fuente = self._fuente_por_tipo(fuente_tipo)
                if fuente:
                    render = fuente.render(texto, True, color)
                    screen.blit(render, (x_base, y_actual))
                    y_actual += max(self.espaciado_linea, render.get_height() + 5)
                continue

            if tipo == "formula":
                _, surface = elemento
                screen.blit(surface, (x_base, y_actual))
                y_actual += surface.get_height() + 8
                continue

        self.alto_contenido = (y_actual + self.scroll_y) - (self.rect.y + self.alto_titulo + 10)

        screen.set_clip(clip_anterior)
        self._dibujar_scroll(screen)

    def _dibujar_titulo(self, screen):
        if not self.titulo or not self.fuente_titulo:
            return

        titulo_render = self.fuente_titulo.render(self.titulo, True, self.color_titulo)
        screen.blit(titulo_render, (self.rect.x + self.margen, self.rect.y + 12))

        pygame.draw.line(
            screen,
            (60, 60, 70),
            (self.rect.x + self.margen, self.rect.y + 44),
            (self.rect.right - self.margen, self.rect.y + 44),
            1,
        )

    def _dibujar_vacio(self, screen):
        if not self.fuente:
            return

        texto = self.fuente.render("Selecciona un algoritmo", True, (150, 150, 150))
        x = self.rect.x + (self.rect.width - texto.get_width()) // 2
        screen.blit(texto, (x, self.rect.y + 24))

        texto2 = self.fuente_pequena.render("y ejecuta para ver la explicación", True, (120, 120, 120))
        x = self.rect.x + (self.rect.width - texto2.get_width()) // 2
        screen.blit(texto2, (x, self.rect.y + 54))

    def _dibujar_scroll(self, screen):
        barra_rect = self._rect_barra()
        if not barra_rect:
            return

        carril = pygame.Rect(
            self.rect.right - self.ancho_barra - 4,
            self.rect.y + self.alto_titulo + 10,
            self.ancho_barra,
            self._alto_visible(),
        )
        pygame.draw.rect(screen, (45, 45, 52), carril, border_radius=4)
        pygame.draw.rect(screen, self.color_borde, barra_rect, border_radius=4)
