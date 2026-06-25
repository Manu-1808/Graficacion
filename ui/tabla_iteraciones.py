import pygame


class TablaIteraciones:

    def __init__(self):

        self.iteraciones = []

    def actualizar(self, datos):

        self.iteraciones = datos

    def dibujar(
            self,
            screen,
            fuente,
            paso_actual):

        pygame.draw.rect(
            screen,
            (40,40,40),
            (1050,0,350,760)
        )

        titulo = fuente.render(
            "Iteraciones",
            True,
            (255,255,255)
        )

        screen.blit(titulo,(1130,20))

        y = 60

        for i, item in enumerate(self.iteraciones[:25]):

            color = (
                255,
                255,
                0
            ) if i < paso_actual else (
                255,
                255,
                255
            )

            texto = fuente.render(
                f"{item.paso} | {item.x_redondeado} | {item.y_redondeado}",
                True,
                color
            )

            screen.blit(
                texto,
                (1070,y)
            )

            y += 25