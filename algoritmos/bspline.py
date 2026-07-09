from modelos.iteracion import Iteracion

# este archivo hace curvas mas suaves con b-spline.
# junta varios puntos para formar una linea mas redondeada.


def calcular(puntos):

    resultado = []

    if len(puntos) < 4:
        return resultado

    paso = 1

    # este ciclo toma grupos de cuatro puntos para crear la curva.
    for i in range(len(puntos) - 3):

        p0 = puntos[i]
        p1 = puntos[i + 1]
        p2 = puntos[i + 2]
        p3 = puntos[i + 3]

        t = 0.0

        while t <= 1:

            x = (
                (
                    (-t**3 + 3*t**2 - 3*t + 1) * p0[0]
                    +
                    (3*t**3 - 6*t**2 + 4) * p1[0]
                    +
                    (-3*t**3 + 3*t**2 + 3*t + 1) * p2[0]
                    +
                    (t**3) * p3[0]
                ) / 6
            )

            y = (
                (
                    (-t**3 + 3*t**2 - 3*t + 1) * p0[1]
                    +
                    (3*t**3 - 6*t**2 + 4) * p1[1]
                    +
                    (-3*t**3 + 3*t**2 + 3*t + 1) * p2[1]
                    +
                    (t**3) * p3[1]
                ) / 6
            )

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

            t += 0.02

    return resultado