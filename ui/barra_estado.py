import pygame


class BarraEstado:

    def __init__(self):

        self.texto = "Listo"

    def actualizar(self, texto):

        self.texto = texto

    def dibujar(self, screen, fuente):

        pygame.draw.rect(
            screen,
            (35,35,35),
            (0, 760, 1400, 40)
        )

        txt = fuente.render(
            self.texto,
            True,
            (255,255,255)
        )

        screen.blit(txt, (10,770))