from modelos.iteracion import Iteracion
import math

def calcular(puntos_control):

    resultado = []

    n = len(puntos_control) - 1

    paso = 1

    t = 0.0

    while t <= 1.0:

        x = 0
        y = 0

        for i, p in enumerate(puntos_control):

            combinacion = math.comb(n, i)

            bernstein = (
                combinacion
                * ((1 - t) ** (n - i))
                * (t ** i)
            )

            x += bernstein * p[0]
            y += bernstein * p[1]

        resultado.append(
            Iteracion(
                paso,
                x,
                y,
                round(x),
                round(y)
            )
        )

        paso += 1

        t += 0.01

    return resultado