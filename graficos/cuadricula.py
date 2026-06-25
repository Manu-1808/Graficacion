import pygame


def dibujar(screen, camara, ancho, alto):

    color = (70, 70, 70)

    zoom = camara.zoom

    for x in range(0, ancho, zoom):

        pygame.draw.line(
            screen,
            color,
            (x, 0),
            (x, alto)
        )

    for y in range(0, alto, zoom):

        pygame.draw.line(
            screen,
            color,
            (0, y),
            (ancho, y)
        )