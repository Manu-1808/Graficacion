import numpy as np
import pygame
import pygame_gui
import matplotlib.cm as cm

from algoritmos.dda import calcular as dda
from algoritmos.bresenham import calcular as bresenham
from algoritmos.bezier import calcular as bezier
from algoritmos.bspline import calcular as bspline
from algoritmos.grafica3d import generar_esfera
from algoritmos.cubo3d import EstadoCubo3D, dibujar_cubo, actualizar_cubo, manejar_clic_cubo, manejar_movimiento_cubo, manejar_soltar_cubo
from algoritmos.esfera_interactiva import EsferaInteractiva
from algoritmos.sombreado_interactivo import (
    EstadoSombreadoInteractivo,
    dibujar_sombreado_interactivo,
    manejar_clic_sombreado,
    manejar_movimiento_sombreado,
    manejar_soltar_sombreado,
    explicacion_sombreado,
)
from modelos.iteracion import Iteracion
from graficos.camara import Camara
from graficos.cuadricula import dibujar as dibujar_cuadricula
from graficos.lienzo import Lienzo
from ui.barra_estado import BarraEstado
from ui.barra_herramientas import BarraHerramientas
from ui.panel_explicacion import PanelExplicacion
from algoritmos.explicaciones import ExplicadorAlgoritmos

# se guardan los tamaños y colores generales del programa.
# estos valores ayudan a mantener todo ordenado y en su sitio.
CONFIG = {
    'ANCHO': 1600,
    'ALTO': 800,
    'ANCHO_HERRAMIENTAS': 280,
    'ANCHO_PANEL': 590,
    'ALTO_ESTADO': 40,
    'VELOCIDAD_MS': 200,
    'ZOOM_MIN': 5,
    'ZOOM_MAX': 100,
    'RADIO_ESFERA': 3,
    'RESOLUCION_ESFERA': 25,
    'COLOR_FONDO': (22, 22, 22),
    'COLOR_PANEL': (15, 15, 15),
    'COLOR_LIENZO': (30, 30, 30),
}

CONFIG['ANCHO_LIENZO'] = CONFIG['ANCHO'] - CONFIG['ANCHO_HERRAMIENTAS'] - CONFIG['ANCHO_PANEL']
CONFIG['ALTO_LIENZO'] = CONFIG['ALTO'] - CONFIG['ALTO_ESTADO']

# inicial
# aqui se inicia pygame para dibujar en pantalla.
pygame.init()
pantalla = pygame.display.set_mode((CONFIG['ANCHO'], CONFIG['ALTO']))
pygame.display.set_caption("Visualizador de Algoritmos de Graficacion")
reloj = pygame.time.Clock()
manager = pygame_gui.UIManager((CONFIG['ANCHO'], CONFIG['ALTO']))
fuente = pygame.font.SysFont("Consolas", 18)

# variables globales
# estos objetos se usan en varias partes del programa.
# guardan la camara, el lienzo y los paneles de la interfaz.
camara = Camara()
lienzo = Lienzo()
barra_estado = BarraEstado()
herramientas = BarraHerramientas(manager)
panel_explicacion = PanelExplicacion(
    CONFIG['ANCHO'] - CONFIG['ANCHO_PANEL'], 0,
    CONFIG['ANCHO_PANEL'], CONFIG['ALTO_LIENZO']
)
explicador = ExplicadorAlgoritmos()

# estado global
# esta clase guarda el estado actual del programa.
# sirve para recordar puntos, modos y si algo se está moviendo.
class EstadoGlobal:
    def __init__(self):
        self.algoritmo_actual = "DDA"
        self.puntos_control = []
        self.iteraciones = []
        self.ejecutando = False
        self.indice_actual = 0
        self.temporizador = 0
        self.punto_arrastrando = None
        self.arrastrando = False
        self.esfera_datos = None
        self.angulo_3d_x = 90
        self.angulo_3d_y = 0
        self.arrastrando_3d = False
        self.ultimo_mouse_3d = None
        # nueva esfera interactiva
        self.esfera_interactiva = EsferaInteractiva(radio=0.8, resolucion=100)
        self.modo_interactivo = False
        self.mostrar_sombra = True
        self.angulo_x = 35
        self.angulo_y = 25
        self.arrastrando_esfera = False

estado = EstadoGlobal()
estado_cubo = EstadoCubo3D()
estado_sombreado = EstadoSombreadoInteractivo()

# transformacion
# estas funciones cambian la posicion de los puntos.
# rotan y trasladan las figuras para moverlas en la pantalla.
def matriz_rotacion_centro(angulo, cx, cy):
    """Crea matriz de rotación alrededor de un punto centro."""
    rad = np.radians(angulo)
    cos_a, sin_a = np.cos(rad), np.sin(rad)
    return np.array([
        [cos_a, -sin_a, cx * (1 - cos_a) + cy * sin_a],
        [sin_a, cos_a, cy * (1 - cos_a) - cx * sin_a],
        [0, 0, 1]
    ])

def aplicar_transformacion(puntos, matriz):
    """Aplica transformación matricial a puntos."""
    if not puntos:
        return []
    homog = np.column_stack((np.array(puntos), np.ones(len(puntos))))
    return [tuple(p[:2]) for p in (matriz @ homog.T).T]

# 3d
# estas funciones crean y dibujan objetos en tres dimensiones.
# ayudan a ver formas como la esfera desde distintos angulos.
def generar_datos_esfera():
    if estado.esfera_datos is None:
        estado.esfera_datos = generar_esfera(CONFIG['RADIO_ESFERA'], CONFIG['RESOLUCION_ESFERA'])
    return estado.esfera_datos

def proyectar_punto_3d(x, y, z):
    ang_x, ang_y = np.radians(estado.angulo_3d_x), np.radians(estado.angulo_3d_y)
    cos_x, sin_x = np.cos(ang_x), np.sin(ang_x)
    cos_y, sin_y = np.cos(ang_y), np.sin(ang_y)
    
    # rotacion en y
    x1, z1 = x * cos_y + z * sin_y, -x * sin_y + z * cos_y
    # rotacion en x
    y1, z2 = y * cos_x - z1 * sin_x, y * sin_x + z1 * cos_x
    
    factor = 4.5 / (4.5 + z2)
    return x1 * factor, y1 * factor, z2

def color_esfera_por_profundidad(z):
    t = np.clip((z + CONFIG['RADIO_ESFERA']) / (2 * CONFIG['RADIO_ESFERA']), 0, 1)
    # contraste cubico
    t_contrastado = 2 * t * t if t < 0.5 else 1 - 2 * (1 - t) * (1 - t)
    rgba = cm.get_cmap('rainbow')(np.clip(t_contrastado, 0, 1))
    brillo = 0.75 + 0.25 * t
    return tuple(int(c * 255 * brillo) for c in rgba[:3])

def dibujar_esfera(superficie):
    if estado.esfera_datos is None:
        generar_datos_esfera()
    
    x_malla, y_malla, z_malla = estado.esfera_datos
    offset_x, offset_y = CONFIG['ANCHO_LIENZO'] // 2, CONFIG['ALTO_LIENZO'] // 2
    
    caras = []
    for i in range(x_malla.shape[0] - 1):
        for j in range(x_malla.shape[1] - 1):
            celda = [(x_malla[i, j], y_malla[i, j], z_malla[i, j]),
                     (x_malla[i+1, j], y_malla[i+1, j], z_malla[i+1, j]),
                     (x_malla[i+1, j+1], y_malla[i+1, j+1], z_malla[i+1, j+1]),
                     (x_malla[i, j+1], y_malla[i, j+1], z_malla[i, j+1])]
            
            proyecciones = [proyectar_punto_3d(*p) for p in celda]
            puntos, profundidad = [], 0
            for sx, sy, depth in proyecciones:
                px, py = camara.mundo_a_pantalla(sx, sy)
                puntos.append((int(px + offset_x), int(py + offset_y)))
                profundidad += depth
            
            caras.append((profundidad / 4.0, puntos, celda))
    
    caras.sort(key=lambda x: x[0], reverse=True)
    
    for _, puntos, celda in caras:
        if len(puntos) == 4:
            z_prom = sum(p[2] for p in celda) / 4.0
            color = color_esfera_por_profundidad(z_prom)
            pygame.draw.polygon(superficie, color, puntos)
            pygame.draw.aalines(superficie, (180, 220, 255), True, puntos)

# dibujo de esfera
# se dibuja la esfera interactiva con su luz y su efecto visual.
def dibujar_esfera_interactiva(superficie):
    if not hasattr(estado, 'esfera_interactiva') or estado.esfera_interactiva is None:
        estado.esfera_interactiva = EsferaInteractiva(radio=0.8, resolucion=350)
    
    esfera = estado.esfera_interactiva
    
    # se obtiene la superficie renderizada de la esfera
    tamano = min(CONFIG['ANCHO_LIENZO'], CONFIG['ALTO_LIENZO']) - 40
    esfera_surf = esfera.obtener_superficie(tamano=tamano)
    
    # se centra la esfera en el lienzo
    x_centro = (CONFIG['ANCHO_LIENZO'] - esfera_surf.get_width()) // 2
    y_centro = (CONFIG['ALTO_LIENZO'] - esfera_surf.get_height()) // 2
    
    # se dibuja la esfera
    superficie.blit(esfera_surf, (x_centro, y_centro))
    
    # se dibuja el indicador de luz
    dibujar_indicador_luz(superficie, esfera, x_centro, y_centro, tamano)

def dibujar_indicador_luz(superficie, esfera, offset_x, offset_y, tamano):
    # la luz está en coordenadas 3d, se proyecta a 2d
    luz_x, luz_y, luz_z = esfera.luz_pos
    
    # escala para convertir coordenadas 3d a pixeles
    escala = tamano / 2.2
    
    # se proyecta la luz a 2d
    luz_px = int(luz_x * escala + tamano // 2 + offset_x)
    luz_py = int(luz_y * escala + tamano // 2 + offset_y)
    
    # brillo de la luz
    for radius in range(25, 5, -5):
        alpha = max(0, min(255, 200 - radius * 6))
        color_luz = (255, 255, 200, alpha)
        glow = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.circle(glow, color_luz, (25, 25), radius)
        superficie.blit(glow, (luz_px - 25, luz_py - 25))
    
    # punto central de la luz
    pygame.draw.circle(superficie, (255, 255, 200), (luz_px, luz_py), 6)
    pygame.draw.circle(superficie, (255, 255, 255), (luz_px, luz_py), 3)
    
    # linea que une la luz con la esfera
    centro_x = tamano // 2 + offset_x
    centro_y = tamano // 2 + offset_y
    pygame.draw.line(superficie, (255, 255, 200, 50), 
                    (luz_px, luz_py), (centro_x, centro_y), 1)

# algoritmos
# aqui se decide que hacer cuando cambia el algoritmo.
# se recalculan los puntos y se actualiza la explicacion.
def recalcular_curva():
    if estado.algoritmo_actual == "Esfera 3D con rejillas":
        generar_datos_esfera()
        actualizar_explicacion()
        return
    
    if estado.algoritmo_actual == "Gouraud vs Phong":
        estado.iteraciones = [Iteracion(1, 0, 0, 0, 0)]
        estado.indice_actual = 1
        estado_sombreado.marcar_dirty()
        barra_estado.actualizar("Gouraud vs Phong - Interactúa con la luz y el triángulo")
        actualizar_explicacion()
        return

    if estado.algoritmo_actual == "Cubo 3D":
        actualizar_cubo(estado_cubo)
        actualizar_explicacion()
        return
    
    if estado.algoritmo_actual == "Esfera 3D Interactiva":
        # la esfera interactiva se actualiza en tiempo real
        actualizar_explicacion()
        return

    if estado.algoritmo_actual == "Gouraud vs Phong":
        estado_sombreado.marcar_dirty()
        actualizar_explicacion()
        return
    
    if estado.algoritmo_actual == "Bezier" and len(estado.puntos_control) >= 3:
        estado.iteraciones = bezier(estado.puntos_control)
        estado.indice_actual = len(estado.iteraciones)
    elif estado.algoritmo_actual == "B-Spline" and len(estado.puntos_control) >= 4:
        estado.iteraciones = bspline(estado.puntos_control)
        estado.indice_actual = len(estado.iteraciones)
    
    actualizar_explicacion()

def aplicar_traslacion():
    try:
        tx, ty = int(herramientas.input_tx.get_text()), int(herramientas.input_ty.get_text())
    except ValueError:
        barra_estado.actualizar("Tx y Ty deben ser numericos")
        return
    
    estado.puntos_control = [(x + tx, y + ty) for x, y in estado.puntos_control]
    estado.iteraciones.clear()
    estado.indice_actual = 0
    barra_estado.actualizar(f"Traslacion aplicada ({tx},{ty})")
    actualizar_explicacion()

def aplicar_rotacion():
    if not estado.puntos_control:
        barra_estado.actualizar("No hay puntos para rotar")
        return
    
    try:
        theta = float(herramientas.input_theta.get_text())
    except ValueError:
        barra_estado.actualizar("Theta debe ser numerico")
        return
    
    arr = np.array(estado.puntos_control)
    centro_arr = arr[:-1] if len(estado.puntos_control) > 1 and estado.puntos_control[0] == estado.puntos_control[-1] else arr
    cx, cy = centro_arr.mean(axis=0)
    
    estado.puntos_control = aplicar_transformacion(estado.puntos_control, matriz_rotacion_centro(theta, cx, cy))
    estado.iteraciones.clear()
    estado.indice_actual = 0
    barra_estado.actualizar(f"Rotación aplicada ({theta}°)")
    actualizar_explicacion()

def ejecutar_lineas():
    estado.iteraciones.clear()
    for i in range(len(estado.puntos_control) - 1):
        p1, p2 = estado.puntos_control[i], estado.puntos_control[i+1]
        segmento = (dda if estado.algoritmo_actual == "DDA" else bresenham)(p1[0], p1[1], p2[0], p2[1])
        estado.iteraciones.extend(segmento if i == 0 else segmento[1:])
    
    estado.indice_actual = 0
    estado.ejecutando = True
    actualizar_explicacion()

# interfaz de usuario
# estas funciones cambian lo que se ve en el panel de explicacion.
# sirven para mostrar texto simple sobre lo que ocurre.
def actualizar_explicacion():
    """Actualiza el panel de explicación."""
    if estado.algoritmo_actual == "Esfera 3D Interactiva":
        explicacion = explicador.explicacion(estado.esfera_interactiva)
        panel_explicacion.actualizar(explicacion, fuente, reiniciar_scroll=False)
        return

    if estado.algoritmo_actual == "Gouraud vs Phong":
        panel_explicacion.actualizar(
            explicacion_sombreado(estado_sombreado),
            fuente,
            reiniciar_scroll=False
        )
        return
    
    if estado.algoritmo_actual == "Cubo 3D":
        texto = explicador.cubo_3d(estado_cubo.angulo_x, estado_cubo.angulo_y, 
                                   estado_cubo.distancia_vista)
        panel_explicacion.actualizar(texto, fuente, reiniciar_scroll=False)
        return
    
    if not estado.iteraciones:
        texto = obtener_texto_inicial()
    else:
        texto = obtener_texto_por_paso()
    
    panel_explicacion.actualizar(texto, fuente, reiniciar_scroll=False)

def obtener_texto_inicial():
    textos = {
        "DDA": r"\textbf{Algoritmo DDA}" + "\n" +
               r"Selecciona al menos 2 puntos." + "\n" +
               r"Interpolación lineal entre puntos." + "\n" +
               r"Ideal para líneas rectas rasterizadas.",
        
        "Bresenham": r"\textbf{Algoritmo de Bresenham}" + "\n" +
                     r"Selecciona al menos 2 puntos." + "\n" +
                     r"Usa aritmética entera para rasterizar." + "\n" +
                     r"Mayor eficiencia que DDA.",
        
        "Bezier": r"\textbf{Curva de Bézier}" + "\n" +
                  r"Selecciona al menos 3 puntos." + "\n" +
                  r"Usa polinomios de Bernstein." + "\n" +
                  r"Curvas suaves controladas por puntos.",
        
        "B-Spline": r"\textbf{Curva B-Spline}" + "\n" +
                    r"Selecciona al menos 4 puntos." + "\n" +
                    r"Control local con curvas suaves." + "\n" +
                    r"Mayor flexibilidad que Bézier.",
        
        "Esfera 3D con rejillas": r"\textbf{Esfera 3D con Rejillas}" + "\n" +
                                  r"Arrastra con el mouse para rotar." + "\n" +
                                  r"Cada polígono se colorea por profundidad." + "\n" +
                                  r"Malla de triángulos que aproxima la esfera.",
        
        "Esfera 3D Interactiva": r"\textbf{Esfera 3D Interactiva}" + "\n" +
                                 r"Mueve el mouse para iluminar la esfera." + "\n" +
                                 r"La luz sigue el cursor en tiempo real." + "\n" +
                                 r"Arrastra para rotar la vista." + "\n" +
                                 r"Renderizado con iluminación Blinn-Phong.",

        "Gouraud vs Phong": r"\textbf{Gouraud vs Phong}" + "\n" +
                             r"Compara dos técnicas de sombreado." + "\n" +
                             r"Mueve la luz con el mouse." + "\n" +
                             r"Arrastra vértices para cambiar el triángulo.",
        
        "Cubo 3D": r"\textbf{Cubo 3D}" + "\n" +
                   r"Arrastra con el mouse para rotar." + "\n" +
                   r"Cubo renderizado en 3D con perspectiva." + "\n" +
                   r"Caras semi-transparentes para visibilidad."
    }
    
    if estado.algoritmo_actual in ["Traslacion", "Rotacion"] and estado.puntos_control:
        try:
            if estado.algoritmo_actual == "Traslacion":
                tx, ty = int(herramientas.input_tx.get_text()), int(herramientas.input_ty.get_text())
                return explicador.traslacion(estado.puntos_control, tx, ty, 0, 0)
            else:
                theta = float(herramientas.input_theta.get_text())
                return explicador.rotacion(estado.puntos_control, theta, 0, 0)
        except (ValueError, TypeError):
            pass
    if estado.algoritmo_actual == "Esfera 3D con rejillas":
        return explicador.esfera_3d(estado.angulo_3d_x, estado.angulo_3d_y)

    if estado.algoritmo_actual == "Gouraud vs Phong":
        return explicacion_sombreado(estado_sombreado)
    
    return textos.get(estado.algoritmo_actual, "")

def obtener_texto_por_paso():
    paso = min(estado.indice_actual, len(estado.iteraciones) - 1)
    if paso < 0 or not estado.iteraciones:
        return ""
    
    if estado.algoritmo_actual == "Esfera 3D con rejillas":
        return explicador.esfera_3d(estado.angulo_3d_x, estado.angulo_3d_y)

    if estado.algoritmo_actual == "Gouraud vs Phong":
        return explicacion_sombreado(estado_sombreado)
    
    iteracion = estado.iteraciones[paso]
    datos = {
        "DDA": lambda: explicador.dda(*estado.puntos_control[0], *estado.puntos_control[1], 
                                    estado.indice_actual, len(estado.iteraciones)),
        "Bresenham": lambda: explicador.bresenham(*estado.puntos_control[0], *estado.puntos_control[1],
                                                estado.indice_actual, getattr(iteracion, 'error', 0)),
        "Bezier": lambda: explicador.bezier(estado.puntos_control, estado.indice_actual, 
                                          len(estado.iteraciones), estado.indice_actual / len(estado.iteraciones)),
        "B-Spline": lambda: explicador.bspline(estado.puntos_control, estado.indice_actual,
                                              len(estado.iteraciones), estado.indice_actual / len(estado.iteraciones))
    }
    
    return datos.get(estado.algoritmo_actual, lambda: {})()

# dibujo
# aqui se dibujan las curvas, los puntos y las iteraciones.
# esta es la parte visual del programa, la que se ve en pantalla.
def dibujar_curvas(superficie):
    # polilineas de control
    for i in range(len(estado.puntos_control) - 1):
        x1, y1 = estado.puntos_control[i]
        x2, y2 = estado.puntos_control[i + 1]
        px1, py1 = camara.mundo_a_pantalla(x1, y1)
        px2, py2 = camara.mundo_a_pantalla(x2, y2)
        offset = camara.zoom // 2
        pygame.draw.line(superficie, (100, 150, 255),
                        (px1 + offset, py1 + offset),
                        (px2 + offset, py2 + offset), 2)
    
    # puntos de control
    for i, punto in enumerate(estado.puntos_control):
        color = (255, 0, 0) if estado.punto_arrastrando == i else (0, 255, 0)
        lienzo.dibujar_pixel(superficie, camara, punto[0], punto[1], color)
    
    # iteraciones
    if estado.algoritmo_actual in ["Bezier", "B-Spline"]:
        iteraciones_a_dibujar = estado.iteraciones
    else:
        iteraciones_a_dibujar = estado.iteraciones[:estado.indice_actual]
    
    for punto in iteraciones_a_dibujar:
        lienzo.dibujar_pixel(superficie, camara, punto.x_redondeado, punto.y_redondeado, (255, 255, 0))

# eventos
# aqui se responden los clics, el mouse y los botones.
# todo lo que hace el usuario termina llegando a estas funciones.
def manejar_eventos(evento):
    if evento.type == pygame.QUIT:
        return False
    
    manager.process_events(evento)

    if panel_explicacion.manejar_evento(evento):
        return True

    if evento.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED and evento.ui_element == herramientas.combo:
        estado.algoritmo_actual = evento.text
        estado.iteraciones.clear()
        estado.indice_actual = 0
        panel_explicacion.scroll_y = 0
        
        if estado.algoritmo_actual == "Esfera 3D con rejillas":
            generar_datos_esfera()
            barra_estado.actualizar("Mostrando esfera 3D - Arrastra para rotar")
        elif estado.algoritmo_actual == "Cubo 3D":
            actualizar_cubo(estado_cubo)
            barra_estado.actualizar("Mostrando cubo 3D - Arrastra para rotar")
        elif estado.algoritmo_actual == "Esfera 3D Interactiva":
            if estado.esfera_interactiva is None:
                estado.esfera_interactiva = EsferaInteractiva(radio=0.8, resolucion=350)
            barra_estado.actualizar("Esfera interactiva - Mueve el mouse para iluminar")
        elif estado.algoritmo_actual == "Gouraud vs Phong":
            estado_sombreado.marcar_dirty()
            barra_estado.actualizar("Gouraud vs Phong - Mueve luz y arrastra vértices")
        else:
            barra_estado.actualizar(f"Algoritmo seleccionado: {estado.algoritmo_actual}")
        
        recalcular_curva()
    
    if evento.type == pygame_gui.UI_BUTTON_PRESSED:
        manejar_boton(evento)
    
    if evento.type == pygame.MOUSEBUTTONDOWN:
        manejar_clic_mouse(evento)
    
    if evento.type == pygame.MOUSEMOTION:
        manejar_movimiento_mouse(evento)
    
    if evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
        estado.arrastrando = estado.punto_arrastrando = False
        estado.arrastrando_3d = False
        estado.ultimo_mouse_3d = None
        estado.arrastrando_esfera = False
        manejar_soltar_sombreado(estado_sombreado)
        manejar_soltar_cubo(estado_cubo)

    
    return True

def manejar_boton(evento):
    if evento.ui_element == herramientas.btn_reiniciar:
        estado.puntos_control.clear()
        estado.iteraciones.clear()
        estado.indice_actual = 0
        estado.ejecutando = False
        estado.punto_arrastrando = None
        estado.angulo_3d_x, estado.angulo_3d_y = 35, 25
        # reiniciar cubo
        estado_cubo.angulo_x = 0
        estado_cubo.angulo_y = 0
        estado_cubo.distancia_vista = 5
        estado_cubo.proyecciones = None
        # reiniciar sombreado interactivo
        estado_sombreado.reiniciar()
        # reiniciar esfera interactiva
        if estado.esfera_interactiva:
            estado.esfera_interactiva = EsferaInteractiva(radio=0.8, resolucion=350)
        barra_estado.actualizar("Proyecto reiniciado")
        actualizar_explicacion()
    
    elif evento.ui_element == herramientas.btn_cerrar_figura:
        if len(estado.puntos_control) >= 3 and estado.puntos_control[0] != estado.puntos_control[-1]:
            estado.puntos_control.append(estado.puntos_control[0])
            barra_estado.actualizar("Figura cerrada")
            recalcular_curva()
    
    elif evento.ui_element == herramientas.btn_ejecutar:
        manejar_ejecucion()

def manejar_ejecucion():
    if estado.algoritmo_actual == "Esfera 3D Interactiva":
        if estado.esfera_interactiva is None:
            estado.esfera_interactiva = EsferaInteractiva(radio=0.8, resolucion=100)
        estado.iteraciones = [Iteracion(1, 0, 0, 0, 0)]
        estado.indice_actual = 1
        barra_estado.actualizar("Esfera interactiva - Mueve el mouse para iluminar")
        actualizar_explicacion()
        return
    
    if estado.algoritmo_actual == "Gouraud vs Phong":
        estado.iteraciones = [Iteracion(1, 0, 0, 0, 0)]
        estado.indice_actual = 1
        estado_sombreado.marcar_dirty()
        barra_estado.actualizar("Gouraud vs Phong - Interactúa con la luz y el triángulo")
        actualizar_explicacion()
        return

    if estado.algoritmo_actual == "Cubo 3D":
        actualizar_cubo(estado_cubo)
        estado.iteraciones = [Iteracion(1, 0, 0, 0, 0)]
        estado.indice_actual = 1
        barra_estado.actualizar("Mostrando cubo 3D - Arrastra para rotar")
        actualizar_explicacion()
        return
    
    if estado.algoritmo_actual == "Traslacion":
        aplicar_traslacion()
    elif estado.algoritmo_actual == "Rotacion":
        aplicar_rotacion()
    elif estado.algoritmo_actual == "Bezier" and len(estado.puntos_control) >= 3:
        estado.iteraciones = bezier(estado.puntos_control)
        estado.indice_actual = 0
        estado.ejecutando = True
        barra_estado.actualizar(f"Ejecutando {estado.algoritmo_actual}")
        actualizar_explicacion()
    elif estado.algoritmo_actual == "B-Spline" and len(estado.puntos_control) >= 4:
        estado.iteraciones = bspline(estado.puntos_control)
        estado.indice_actual = 0
        estado.ejecutando = True
        barra_estado.actualizar(f"Ejecutando {estado.algoritmo_actual}")
        actualizar_explicacion()
    elif estado.algoritmo_actual == "Esfera 3D con rejillas":
        generar_datos_esfera()
        estado.iteraciones = [Iteracion(1, 0, 0, 0, 0)]
        estado.indice_actual = 1
        barra_estado.actualizar("Mostrando esfera 3D - Arrastra para rotar")
        actualizar_explicacion()
    elif len(estado.puntos_control) >= 2:
        ejecutar_lineas()
        barra_estado.actualizar(f"Ejecutando {estado.algoritmo_actual}")
    else:
        barra_estado.actualizar(f"{estado.algoritmo_actual} requiere más puntos")

def manejar_clic_mouse(evento):
    mouse_x, mouse_y = evento.pos
    dentro_lienzo = (CONFIG['ANCHO_HERRAMIENTAS'] <= mouse_x <= CONFIG['ANCHO_HERRAMIENTAS'] + CONFIG['ANCHO_LIENZO'] and
                    mouse_y <= CONFIG['ALTO_LIENZO'])
    
    if not dentro_lienzo:
        return

    # modo gouraud vs phong
    if estado.algoritmo_actual == "Gouraud vs Phong":
        manejar_clic_sombreado(evento, estado_sombreado, CONFIG)
        actualizar_explicacion()
        return
    
    # modo esfera interactiva
    if estado.algoritmo_actual == "Esfera 3D Interactiva":
        if estado.esfera_interactiva is None:
            estado.esfera_interactiva = EsferaInteractiva(radio=0.8, resolucion=350)
        
        if evento.button == 1:
            estado.arrastrando_esfera = True
            estado.ultimo_mouse = (mouse_x, mouse_y)
        return
    
    # modo cubo 3d
    if estado.algoritmo_actual == "Cubo 3D":
        manejar_clic_cubo(evento, estado_cubo)
        return
    
    # modo esfera 3d con rejillas
    if estado.algoritmo_actual == "Esfera 3D con rejillas":
        if evento.button == 1:
            estado.arrastrando_3d = True
            estado.ultimo_mouse_3d = (mouse_x, mouse_y)
        elif evento.button == 4:
            camara.zoom = min(camara.zoom + 2, CONFIG['ZOOM_MAX'])
        elif evento.button == 5:
            camara.zoom = max(camara.zoom - 2, CONFIG['ZOOM_MIN'])
        return
    
    if evento.button == 1:
        # buscar punto para arrastrar
        for i, punto in enumerate(estado.puntos_control):
            px, py = camara.mundo_a_pantalla(punto[0], punto[1])
            if abs(px + CONFIG['ANCHO_HERRAMIENTAS'] - mouse_x) < 10 and abs(py - mouse_y) < 10:
                estado.punto_arrastrando = i
                estado.arrastrando = True
                return
        
        # agregar nuevo punto
        gx, gy = camara.pantalla_a_mundo(mouse_x - CONFIG['ANCHO_HERRAMIENTAS'], mouse_y)
        estado.puntos_control.append((gx, gy))
        barra_estado.actualizar(f"Punto agregado ({gx},{gy})")
        recalcular_curva()
    
    elif evento.button == 4:
        camara.zoom = min(camara.zoom + 2, CONFIG['ZOOM_MAX'])
    elif evento.button == 5:
        camara.zoom = max(camara.zoom - 2, CONFIG['ZOOM_MIN'])

def manejar_movimiento_mouse(evento):
    # modo gouraud vs phong
    if estado.algoritmo_actual == "Gouraud vs Phong":
        mouse_x, mouse_y = evento.pos
        dentro_lienzo = (
            CONFIG['ANCHO_HERRAMIENTAS'] <= mouse_x <= CONFIG['ANCHO_HERRAMIENTAS'] + CONFIG['ANCHO_LIENZO']
            and mouse_y <= CONFIG['ALTO_LIENZO']
        )
        if dentro_lienzo:
            manejar_movimiento_sombreado(evento, estado_sombreado, CONFIG)
            actualizar_explicacion()
        return

    # se actualiza la posicion de la luz para la esfera interactiva
    if estado.algoritmo_actual == "Esfera 3D Interactiva":
        if estado.esfera_interactiva is None:
            return
        
        mouse_x, mouse_y = evento.pos
        if (CONFIG['ANCHO_HERRAMIENTAS'] <= mouse_x <= CONFIG['ANCHO_HERRAMIENTAS'] + CONFIG['ANCHO_LIENZO'] and
            mouse_y <= CONFIG['ALTO_LIENZO']):
            # calcular posicion relativa al lienzo
            rel_x = mouse_x - CONFIG['ANCHO_HERRAMIENTAS']
            rel_y = mouse_y
            estado.esfera_interactiva.actualizar_luz(rel_x, rel_y, CONFIG['ANCHO_LIENZO'], CONFIG['ALTO_LIENZO'])
            actualizar_explicacion()
        return
    
    # rotacion 3d de la esfera con rejillas
    if estado.arrastrando_3d and estado.ultimo_mouse_3d:
        dx = evento.pos[0] - estado.ultimo_mouse_3d[0]
        dy = evento.pos[1] - estado.ultimo_mouse_3d[1]
        estado.angulo_3d_y = (estado.angulo_3d_y + dx * 0.5) % 360
        estado.angulo_3d_x = np.clip(estado.angulo_3d_x + dy * 0.5, -90, 90)
        estado.ultimo_mouse_3d = evento.pos
        actualizar_explicacion()
        return
    
    # rotacion del cubo 3d
    if estado.algoritmo_actual == "Cubo 3D":
        manejar_movimiento_cubo(evento, estado_cubo)
        actualizar_explicacion()
        return
    
    # arrastre de puntos
    if estado.arrastrando and estado.punto_arrastrando is not None:
        gx, gy = camara.pantalla_a_mundo(evento.pos[0] - CONFIG['ANCHO_HERRAMIENTAS'], evento.pos[1])
        estado.puntos_control[estado.punto_arrastrando] = (gx, gy)
        recalcular_curva()
        if estado.iteraciones:
            actualizar_explicacion()

# programa principal
def main():
    running = True
    
    while running:
        tiempo = reloj.tick(60)
        manager.update(tiempo / 1000.0)
        
        # procesar eventos
        for evento in pygame.event.get():
            if not manejar_eventos(evento):
                running = False
        
        # actualizar animacion
        if estado.ejecutando and estado.iteraciones:
            estado.temporizador += tiempo
            if estado.temporizador >= CONFIG['VELOCIDAD_MS']:
                estado.temporizador = 0
                if estado.indice_actual < len(estado.iteraciones):
                    estado.indice_actual += 1
                    actualizar_explicacion()
                else:
                    estado.ejecutando = False
                    barra_estado.actualizar("Simulacion finalizada")
        
        # dibujar
        pantalla.fill(CONFIG['COLOR_FONDO'])
        pygame.draw.rect(pantalla, CONFIG['COLOR_PANEL'], (0, 0, CONFIG['ANCHO_HERRAMIENTAS'], CONFIG['ALTO_LIENZO']))
        pygame.draw.rect(pantalla, CONFIG['COLOR_LIENZO'], 
                        (CONFIG['ANCHO_HERRAMIENTAS'], 0, CONFIG['ANCHO_LIENZO'], CONFIG['ALTO_LIENZO']))
        
        superficie_lienzo = pantalla.subsurface(
            (CONFIG['ANCHO_HERRAMIENTAS'], 0, CONFIG['ANCHO_LIENZO'], CONFIG['ALTO_LIENZO'])
        )
        
        dibujar_cuadricula(superficie_lienzo, camara, CONFIG['ANCHO_LIENZO'], CONFIG['ALTO_LIENZO'])
        
        # dibujar segun el algoritmo
        if estado.algoritmo_actual == "Gouraud vs Phong":
            dibujar_sombreado_interactivo(superficie_lienzo, estado_sombreado, CONFIG, fuente)
        elif estado.algoritmo_actual == "Esfera 3D Interactiva":
            dibujar_esfera_interactiva(superficie_lienzo)
        elif estado.algoritmo_actual == "Esfera 3D con rejillas":
            dibujar_esfera(superficie_lienzo)
        elif estado.algoritmo_actual == "Cubo 3D":
            dibujar_cubo(superficie_lienzo, estado_cubo, camara, CONFIG)
        else:
            dibujar_curvas(superficie_lienzo)
        
        panel_explicacion.dibujar(pantalla)
        barra_estado.dibujar(pantalla, fuente)
        manager.draw_ui(pantalla)
        pygame.display.update()
    
    pygame.quit()

if __name__ == "__main__":
    main()