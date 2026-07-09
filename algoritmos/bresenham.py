from modelos.iteracion import Iteracion

# este archivo hace una linea con una idea mas inteligente.
# usa un error para decidir cuando bajar o mover a la derecha.


def calcular(x1, y1, x2, y2):

    resultado = []

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1

    err = dx - dy

    paso = 1

    # este ciclo sigue hasta llegar al punto final.
    while True:

        resultado.append(
            Iteracion(
                paso,
                x1,
                y1,
                x1,
                y1,
                err
            )
        )

        if x1 == x2 and y1 == y2:
            break

        e2 = err * 2

        if e2 > -dy:
            err -= dy
            x1 += sx

        if e2 < dx:
            err += dx
            y1 += sy

        paso += 1

    return resultado