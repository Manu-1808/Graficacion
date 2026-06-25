from modelos.iteracion import Iteracion


def calcular(x1, y1, x2, y2):

    resultado = []

    dx = x2 - x1
    dy = y2 - y1

    pasos = max(abs(dx), abs(dy))

    if pasos == 0:
        return [
            Iteracion(
                1,
                x1,
                y1,
                x1,
                y1
            )
        ]

    x_inc = dx / pasos
    y_inc = dy / pasos

    x = x1
    y = y1

    for paso in range(pasos + 1):

        resultado.append(
            Iteracion(
                paso + 1,
                x,
                y,
                round(x),
                round(y)
            )
        )

        x += x_inc
        y += y_inc

    return resultado