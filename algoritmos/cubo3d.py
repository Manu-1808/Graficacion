# algoritmos/cubo3d.py
import numpy as np
import pygame

# estos son los puntos del cubo en tres dimensiones.
# cada punto sirve para formar las caras y las aristas.
VERTICES_CUBO = np.array([
    [-1, -1, -1, 1],
    [1, -1, -1, 1],
    [1, 1, -1, 1],
    [-1, 1, -1, 1],
    
    [-1, -1, 1, 1],
    [1, -1, 1, 1],
    [1, 1, 1, 1],
    [-1, 1, 1, 1]
])

# Aristas del cubo
ARISTAS_CUBO = [
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7)
]

# Caras del cubo
CARAS_CUBO = [
    [0, 1, 2, 3],
    [4, 5, 6, 7],
    [0, 1, 5, 4],
    [2, 3, 7, 6],
    [0, 3, 7, 4],
    [1, 2, 6, 5]
]

class EstadoCubo3D:
    def __init__(self):
        self.angulo_x = 0
        self.angulo_y = 0
        self.distancia_vista = 2
        self.arrastrando = False
        self.ultimo_mouse = None
        self.proyecciones = None

def matriz_rotacion_x(theta):
    cos_t, sin_t = np.cos(theta), np.sin(theta)
    return np.array([
        [1, 0, 0, 0],
        [0, cos_t, -sin_t, 0],
        [0, sin_t, cos_t, 0],
        [0, 0, 0, 1]
    ])

def matriz_rotacion_y(theta):
    cos_t, sin_t = np.cos(theta), np.sin(theta)
    return np.array([
        [cos_t, 0, sin_t, 0],
        [0, 1, 0, 0],
        [-sin_t, 0, cos_t, 0],
        [0, 0, 0, 1]
    ])

def generar_matriz_vista(z_dist):
    return np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, -z_dist],
        [0, 0, 0, 1]
    ])

def renderizar_cubo(ang_x, ang_y, z_dist):
    # aqui se rota el cubo para verlo desde otro lado.
    m_rot = np.dot(matriz_rotacion_y(ang_y), matriz_rotacion_x(ang_x))
    v_transformado = np.dot(VERTICES_CUBO, m_rot.T)
    v_view = np.dot(v_transformado, generar_matriz_vista(z_dist).T)
    
    m_proyeccion = np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0.5, 0]
    ])
    
    v_proyeccion = np.dot(v_view, m_proyeccion.T)
    final_2d = v_proyeccion[:, :2] / v_proyeccion[:, 3:].reshape((-1, 1))
    return final_2d

def actualizar_cubo(estado_cubo):
    estado_cubo.proyecciones = renderizar_cubo(
        estado_cubo.angulo_x,
        estado_cubo.angulo_y,
        estado_cubo.distancia_vista
    )

def dibujar_cubo(superficie, estado_cubo, camara, CONFIG):
    if estado_cubo.proyecciones is None:
        actualizar_cubo(estado_cubo)
    
    offset_x, offset_y = CONFIG['ANCHO_LIENZO'] // 2, CONFIG['ALTO_LIENZO'] // 2
    puntos = estado_cubo.proyecciones
    
    # Dibujar caras semi-transparentes
    profundidades = []
    for cara in CARAS_CUBO:
        z_prom = sum(VERTICES_CUBO[i, 2] for i in cara) / 4.0
        profundidades.append((z_prom, cara))
    profundidades.sort(key=lambda x: x[0], reverse=True)
    
    for _, cara in profundidades:
        puntos_cara = []
        for idx in cara:
            px = puntos[idx, 0] * camara.zoom + offset_x
            py = puntos[idx, 1] * camara.zoom + offset_y
            puntos_cara.append((int(px), int(py)))
        
        z_prom = sum(VERTICES_CUBO[i, 2] for i in cara) / 4.0
        t = (z_prom + 1) / 2
        color = (int(50 + 100 * t), int(50 + 100 * (1-t)), 200)
        
        if len(puntos_cara) == 4:
            s = pygame.Surface((CONFIG['ANCHO_LIENZO'], CONFIG['ALTO_LIENZO']), pygame.SRCALPHA)
            pygame.draw.polygon(s, (*color, 50), puntos_cara)
            superficie.blit(s, (0, 0))
    
    # Dibujar aristas
    for i, j in ARISTAS_CUBO:
        x1 = puntos[i, 0] * camara.zoom + offset_x
        y1 = puntos[i, 1] * camara.zoom + offset_y
        x2 = puntos[j, 0] * camara.zoom + offset_x
        y2 = puntos[j, 1] * camara.zoom + offset_y
        pygame.draw.line(superficie, (100, 200, 255), 
                        (int(x1), int(y1)), (int(x2), int(y2)), 2)
    
    # Dibujar vértices
    for punto in puntos:
        px = punto[0] * camara.zoom + offset_x
        py = punto[1] * camara.zoom + offset_y
        pygame.draw.circle(superficie, (255, 200, 100), 
                          (int(px), int(py)), 4)

def manejar_clic_cubo(evento, estado_cubo):
    if evento.button == 1:
        estado_cubo.arrastrando = True
        estado_cubo.ultimo_mouse = evento.pos
    elif evento.button == 4:
        estado_cubo.distancia_vista = max(1, estado_cubo.distancia_vista - 0.5)
        actualizar_cubo(estado_cubo)
    elif evento.button == 5:
        estado_cubo.distancia_vista = min(10, estado_cubo.distancia_vista + 0.5)
        actualizar_cubo(estado_cubo)

def manejar_movimiento_cubo(evento, estado_cubo):
    if estado_cubo.arrastrando and estado_cubo.ultimo_mouse:
        dx = evento.pos[0] - estado_cubo.ultimo_mouse[0]
        dy = evento.pos[1] - estado_cubo.ultimo_mouse[1]
        estado_cubo.angulo_x += dx * 0.01
        estado_cubo.angulo_y -= dy * 0.01
        estado_cubo.ultimo_mouse = evento.pos
        actualizar_cubo(estado_cubo)

def manejar_soltar_cubo(estado_cubo):
    estado_cubo.arrastrando = False
    estado_cubo.ultimo_mouse = None