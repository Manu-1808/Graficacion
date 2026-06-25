import pygame


class PanelExplicacion:
    def __init__(self, x, y, ancho, alto):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.datos = None
        self.fuente = None
        self.fuente_titulo = None
        self.fuente_pequena = None

    def actualizar(self, datos, fuente=None):
        """Actualiza el panel con los datos de explicación"""
        self.datos = datos
        if fuente:
            self.fuente = fuente
            self.fuente_titulo = pygame.font.SysFont("Consolas", 20, bold=True)
            self.fuente_pequena = pygame.font.SysFont("Consolas", 15)

    def dibujar(self, screen):
        """Dibuja el panel con estilo mejorado"""
        # Fondo con gradiente simulado
        pygame.draw.rect(screen, (30, 30, 35), self.rect)
        pygame.draw.rect(screen, (60, 60, 70), self.rect, 2)

        # Borde superior con color del algoritmo
        if self.datos and 'color' in self.datos:
            color_borde = self.datos['color']
            pygame.draw.line(
                screen,
                color_borde,
                (self.rect.x, self.rect.y),
                (self.rect.x + self.rect.width, self.rect.y),
                3
            )

        if not self.datos or 'lineas' not in self.datos:
            # Mensaje por defecto
            if self.fuente:
                texto = self.fuente.render(
                    "Selecciona un algoritmo",
                    True,
                    (150, 150, 150)
                )
                x = self.rect.x + (self.rect.width - texto.get_width()) // 2
                y = self.rect.y + 20
                screen.blit(texto, (x, y))

                texto2 = self.fuente_pequena.render(
                    "y ejecuta para ver explicación",
                    True,
                    (120, 120, 120)
                )
                x = self.rect.x + (self.rect.width - texto2.get_width()) // 2
                y = self.rect.y + 50
                screen.blit(texto2, (x, y))
            return

        # Dibujar título
        if 'titulo' in self.datos and self.fuente_titulo:
            titulo = self.fuente_titulo.render(
                self.datos['titulo'],
                True,
                (255, 255, 255)
            )
            screen.blit(titulo, (self.rect.x + 15, self.rect.y + 10))

        # Dibujar líneas
        y = self.rect.y + 50
        for linea in self.datos['lineas']:
            if y > self.rect.y + self.rect.height - 20:
                break

            texto = linea['texto']
            color = linea['color']

            if texto == '':
                y += 8
                continue

            # Renderizar con la fuente apropiada
            if self.fuente:
                render = self.fuente.render(texto, True, color)
                x = self.rect.x + 20
                screen.blit(render, (x, y))
                y += 28

        # Indicador de progreso (si está en ejecución)
        if 'progreso' in self.datos:
            progreso = self.datos['progreso']
            ancho_barra = self.rect.width - 40
            pygame.draw.rect(
                screen,
                (50, 50, 50),
                (self.rect.x + 20, self.rect.y + self.rect.height - 30, ancho_barra, 8)
            )
            pygame.draw.rect(
                screen,
                self.datos.get('color', (100, 200, 255)),
                (self.rect.x + 20, self.rect.y + self.rect.height - 30, int(ancho_barra * progreso), 8)
            )