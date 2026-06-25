import pygame


class Lienzo:

    def dibujar_pixel(
            self,
            screen,
            camara,
            x,
            y,
            color):

        px, py = camara.mundo_a_pantalla(x, y)

        pygame.draw.rect(
            screen,
            color,
            (
                px,
                py,
                camara.zoom,
                camara.zoom
            )
        )