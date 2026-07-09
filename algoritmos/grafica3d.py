import numpy as np

# este archivo crea una esfera usando una malla de puntos.
# se hacen muchas coordenadas y luego se unen para formar la figura.

def generar_esfera(radio, resolucion):
    u = np.linspace(0, 2 * np.pi, resolucion)
    v = np.linspace(0, np.pi, resolucion)

    #creacion de la regill
    u,v = np.meshgrid(u, v)
    #aplicamos ecuaciones parametricas
    x = radio * np.cos(u) * np.sin(v)
    y = radio * np.sin(u) * np.sin(v)
    z = radio * np.cos(v)

    return x, y, z