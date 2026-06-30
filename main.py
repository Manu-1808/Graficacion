import numpy as np
import pygame
import pygame_gui
import matplotlib.cm as cm

from algoritmos.dda import calcular as dda
from algoritmos.bresenham import calcular as bresenham
from algoritmos.bezier import calcular as bezier
from algoritmos.bspline import calcular as bspline
from algoritmos.grafica3d import generar_esfera
from modelos.iteracion import Iteracion
from graficos.camara import Camara
from graficos.cuadricula import dibujar as dibujar_cuadricula
from graficos.lienzo import Lienzo
from ui.barra_estado import BarraEstado
from ui.barra_herramientas import BarraHerramientas
from ui.panel_explicacion import PanelExplicacion
from algoritmos.explicaciones import ExplicadorAlgoritmos

# ============ CONFIGURACIÓN ============
CONFIG = {
    'ANCHO': 1400,
    'ALTO': 800,
    'ANCHO_HERRAMIENTAS': 250,
    'ANCHO_PANEL': 480,
    'ALTO_ESTADO': 40,
    'VELOCIDAD_MS': 200,
    'ZOOM_MIN': 5,
    'ZOOM_MAX': 100,
    'RADIO_ESFERA': 4,
    'RESOLUCION_ESFERA': 80,
    'COLOR_FONDO': (22, 22, 22),
    'COLOR_PANEL': (30, 30, 30),
    'COLOR_LIENZO': (20, 20, 20),
}

CONFIG['ANCHO_LIENZO'] = CONFIG['ANCHO'] - CONFIG['ANCHO_HERRAMIENTAS'] - CONFIG['ANCHO_PANEL']
CONFIG['ALTO_LIENZO'] = CONFIG['ALTO'] - CONFIG['ALTO_ESTADO']

# ============ INICIALIZACIÓN ============
pygame.init()
pantalla = pygame.display.set_mode((CONFIG['ANCHO'], CONFIG['ALTO']))
pygame.display.set_caption("Visualizador de Algoritmos de Graficacion")
reloj = pygame.time.Clock()
manager = pygame_gui.UIManager((CONFIG['ANCHO'], CONFIG['ALTO']))
fuente = pygame.font.SysFont("Consolas", 18)

# ============ OBJETOS GLOBALES ============
camara = Camara()
lienzo = Lienzo()
barra_estado = BarraEstado()
herramientas = BarraHerramientas(manager)
panel_explicacion = PanelExplicacion(
    CONFIG['ANCHO'] - CONFIG['ANCHO_PANEL'], 0,
    CONFIG['ANCHO_PANEL'], CONFIG['ALTO_LIENZO']
)
explicador = ExplicadorAlgoritmos()

# ============ ESTADO GLOBAL ============
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

estado = EstadoGlobal()

# ============ FUNCIONES DE TRANSFORMACIÓN ============
def matriz_rotacion_centro(angulo, cx, cy):
    r = np.radians(angulo)
    R = np.array([
        [np.cos(r), -np.sin(r), 0],
        [np.sin(r), np.cos(r), 0],
        [0, 0, 1]
    ])
    T1 = np.array([[1, 0, cx], [0, 1, cy], [0, 0, 1]])
    T2 = np.array([[1, 0, -cx], [0, 1, -cy], [0, 0, 1]])
    return T1 @ R @ T2

def aplicar_transformacion(puntos, matriz):
    if not puntos:
        return []
    arr = np.array(puntos, dtype=float)
    homog = np.hstack((arr, np.ones((len(arr), 1))))
    resultado = (matriz @ homog.T).T
    return [tuple(p[:2]) for p in resultado]

# ============ FUNCIONES 3D ============
def generar_datos_esfera():
    if estado.esfera_datos is None:
        estado.esfera_datos = generar_esfera(
            radio=CONFIG['RADIO_ESFERA'],
            resolucion=CONFIG['RESOLUCION_ESFERA']
        )
    return estado.esfera_datos

def proyectar_punto_3d(x, y, z):
    angulo_x, angulo_y = np.radians(35), np.radians(25)
    cos_x, sin_x = np.cos(angulo_x), np.sin(angulo_x)
    cos_y, sin_y = np.cos(angulo_y), np.sin(angulo_y)
    
    x1 = x * cos_y + z * sin_y
    z1 = -x * sin_y + z * cos_y
    y1 = y * cos_x - z1 * sin_x
    z2 = y * sin_x + z1 * cos_x
    
    factor = 4.5 / (4.5 + z2)
    return x1 * factor, y1 * factor, z2

def color_esfera_por_profundidad(z, radio=4):
    t = (z + radio) / (2 * radio)
    t = max(0, min(1, t))
    
    # Curva de contraste cúbica
    if t < 0.5:
        t_contrastado = 2 * t * t
    else:
        t_contrastado = 1 - 2 * (1 - t) * (1 - t)
    t_contrastado = max(0, min(1, t_contrastado))
    
    viridis = cm.get_cmap('viridis')
    rgba = viridis(t_contrastado)
    
    brillo = 0.75 + 0.25 * t
    r = int(rgba[0] * 255 * brillo)
    g = int(rgba[1] * 255 * brillo)
    b = int(rgba[2] * 255 * brillo)
    
    return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))

def dibujar_esfera(superficie):
    if estado.esfera_datos is None:
        generar_datos_esfera()
    
    x_malla, y_malla, z_malla = estado.esfera_datos
    offset_x, offset_y = CONFIG['ANCHO_LIENZO'] // 2, CONFIG['ALTO_LIENZO'] // 2
    
    caras = []
    for i in range(x_malla.shape[0] - 1):
        for j in range(x_malla.shape[1] - 1):
            celda = [
                (x_malla[i, j], y_malla[i, j], z_malla[i, j]),
                (x_malla[i+1, j], y_malla[i+1, j], z_malla[i+1, j]),
                (x_malla[i+1, j+1], y_malla[i+1, j+1], z_malla[i+1, j+1]),
                (x_malla[i, j+1], y_malla[i, j+1], z_malla[i, j+1])
            ]
            
            proyecciones = [proyectar_punto_3d(*p) for p in celda]
            puntos = []
            profundidad = 0
            for sx, sy, depth in proyecciones:
                px, py = camara.mundo_a_pantalla(sx, sy)
                puntos.append((int(px + offset_x), int(py + offset_y)))
                profundidad += depth
            
            caras.append((profundidad / 4.0, puntos, celda))
    
    caras.sort(key=lambda item: item[0], reverse=True)
    
    for _, puntos, celda in caras:
        if len(puntos) != 4:
            continue
        z_promedio = sum(p[2] for p in celda) / 4.0
        color = color_esfera_por_profundidad(z_promedio, CONFIG['RADIO_ESFERA'])
        pygame.draw.polygon(superficie, color, puntos)
        pygame.draw.aalines(superficie, (180, 220, 255), True, puntos)

# ============ FUNCIONES DE ALGORITMOS ============
def recalcular_curva():
    if estado.algoritmo_actual == "Graficas 3D":
        generar_datos_esfera()
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
        tx = int(herramientas.input_tx.get_text())
        ty = int(herramientas.input_ty.get_text())
    except ValueError:
        barra_estado.actualizar("Tx y Ty deben ser numericos")
        return
    
    nuevos_puntos = []
    estado.iteraciones = []
    
    for paso, (x, y) in enumerate(estado.puntos_control, 1):
        nx, ny = x + tx, y + ty
        nuevos_puntos.append((nx, ny))
        estado.iteraciones.append(Iteracion(paso, nx, ny, round(nx), round(ny)))
    
    estado.puntos_control = nuevos_puntos
    estado.indice_actual = len(estado.iteraciones)
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
    
    arr = np.array(estado.puntos_control, dtype=float)
    if len(estado.puntos_control) > 1 and estado.puntos_control[0] == estado.puntos_control[-1]:
        centro_arr = arr[:-1]
    else:
        centro_arr = arr
    
    cx, cy = centro_arr.mean(axis=0)
    matriz = matriz_rotacion_centro(theta, cx, cy)
    estado.puntos_control = aplicar_transformacion(estado.puntos_control, matriz)
    estado.iteraciones = []
    estado.indice_actual = 0
    barra_estado.actualizar(f"Rotación aplicada ({theta}°)")
    actualizar_explicacion()

def ejecutar_lineas():
    estado.iteraciones = []
    for i in range(len(estado.puntos_control) - 1):
        p1, p2 = estado.puntos_control[i], estado.puntos_control[i+1]
        if estado.algoritmo_actual == "DDA":
            segmento = dda(p1[0], p1[1], p2[0], p2[1])
        else:
            segmento = bresenham(p1[0], p1[1], p2[0], p2[1])
        if i > 0:
            segmento = segmento[1:]
        estado.iteraciones.extend(segmento)
    
    estado.indice_actual = 0
    estado.ejecutando = True
    actualizar_explicacion()

# ============ FUNCIONES DE UI ============
def actualizar_explicacion():
    texto = ""
    
    if not estado.iteraciones:
        # Texto inicial según algoritmo
        textos_iniciales = {
            "DDA": r"\textbf{Algoritmo DDA (Digital Differential Analyzer)}\n\nSelecciona al menos 2 puntos para comenzar.\n\nEl DDA calcula puntos intermedios mediante\ninterpolación lineal entre dos puntos.",
            "Bresenham": r"\textbf{Algoritmo de Bresenham}\n\nSelecciona al menos 2 puntos para comenzar.\n\nBresenham usa aritmética entera para rasterizar\nlíneas de manera eficiente.",
            "Bezier": r"\textbf{Curva de Bézier}\n\nSelecciona al menos 3 puntos de control.\n\nLa curva usa polinomios de Bernstein para\ngenerar una curva suave.",
            "B-Spline": r"\textbf{Curva B-Spline Cúbica}\n\nSelecciona al menos 4 puntos de control.\n\nLas B-Splines generan curvas suaves con\ncontrol local.",
            "Graficas 3D": r"\textbf{Gráficas 3D: Esfera Paramétrica}\n\nEsta vista genera una esfera usando coordenadas\nparamétricas en (u,v) y la proyecta en 2D."
        }
        
        if estado.algoritmo_actual in ["Traslacion", "Rotacion"]:
            if estado.puntos_control:
                try:
                    if estado.algoritmo_actual == "Traslacion":
                        tx = int(herramientas.input_tx.get_text())
                        ty = int(herramientas.input_ty.get_text())
                        texto = explicador.traslacion(estado.puntos_control, tx, ty, 0, 0)
                    else:
                        theta = float(herramientas.input_theta.get_text())
                        texto = explicador.rotacion(estado.puntos_control, theta, 0, 0)
                except:
                    texto = textos_iniciales.get(estado.algoritmo_actual, "")
            else:
                texto = textos_iniciales.get(estado.algoritmo_actual, "")
        else:
            texto = textos_iniciales.get(estado.algoritmo_actual, "")
    else:
        # Texto por pasos
        paso = min(estado.indice_actual, len(estado.iteraciones) - 1)
        if paso >= 0 and len(estado.iteraciones) > 0:
            iteracion = estado.iteraciones[paso]
            
            if estado.algoritmo_actual == "DDA" and len(estado.puntos_control) >= 2:
                x1, y1 = estado.puntos_control[0]
                x2, y2 = estado.puntos_control[1]
                texto = explicador.dda(x1, y1, x2, y2, estado.indice_actual, len(estado.iteraciones))
            elif estado.algoritmo_actual == "Bresenham" and len(estado.puntos_control) >= 2:
                x1, y1 = estado.puntos_control[0]
                x2, y2 = estado.puntos_control[1]
                texto = explicador.bresenham(x1, y1, x2, y2, estado.indice_actual, iteracion.error)
            elif estado.algoritmo_actual == "Bezier":
                total = len(estado.iteraciones)
                texto = explicador.bezier(estado.puntos_control, estado.indice_actual, total, 
                                         estado.indice_actual / total if total > 0 else 0)
            elif estado.algoritmo_actual == "B-Spline":
                total = len(estado.iteraciones)
                texto = explicador.bspline(estado.puntos_control, estado.indice_actual, total,
                                          estado.indice_actual / total if total > 0 else 0)
    
    panel_explicacion.actualizar(texto, fuente)

# ============ FUNCIONES DE DIBUJO ============
def dibujar_info_lateral(pantalla):
    y = 380
    info = [
        f"Algoritmo: {estado.algoritmo_actual}",
        f"Puntos: {len(estado.puntos_control)}",
        f"Zoom: {camara.zoom}",
        f"Paso: {estado.indice_actual}/{len(estado.iteraciones)}"
    ]
    
    try:
        tx = herramientas.input_tx.get_text()
        ty = herramientas.input_ty.get_text()
        theta = herramientas.input_theta.get_text()
        info.append(f"Tx={tx} Ty={ty} Theta={theta}")
    except:
        pass
    
    for texto in info:
        txt = fuente.render(texto, True, (255, 255, 255))
        pantalla.blit(txt, (20, y))
        y += 30
    
    # Lista de puntos
    y = 550
    for i, punto in enumerate(estado.puntos_control[:8]):
        txt = fuente.render(f"P{i}: {punto}", True, (255, 255, 255))
        pantalla.blit(txt, (20, y))
        y += 25

def dibujar_curvas(superficie):
    # Dibujar polílineas de control
    for i in range(len(estado.puntos_control) - 1):
        x1, y1 = estado.puntos_control[i]
        x2, y2 = estado.puntos_control[i + 1]
        px1, py1 = camara.mundo_a_pantalla(x1, y1)
        px2, py2 = camara.mundo_a_pantalla(x2, y2)
        pygame.draw.line(superficie, (100, 150, 255),
                        (px1 + camara.zoom // 2, py1 + camara.zoom // 2),
                        (px2 + camara.zoom // 2, py2 + camara.zoom // 2), 2)
    
    # Dibujar puntos de control
    for i, punto in enumerate(estado.puntos_control):
        color = (255, 0, 0) if estado.punto_arrastrando == i else (0, 255, 0)
        lienzo.dibujar_pixel(superficie, camara, punto[0], punto[1], color)
    
    # Dibujar iteraciones
    iteraciones_a_dibujar = estado.iteraciones if estado.algoritmo_actual in ["Bezier", "B-Spline"] else estado.iteraciones[:estado.indice_actual]
    for punto in iteraciones_a_dibujar:
        lienzo.dibujar_pixel(superficie, camara, punto.x_redondeado, punto.y_redondeado, (255, 255, 0))

# ============ MANEJADORES DE EVENTOS ============
def manejar_eventos(evento):
    if evento.type == pygame.QUIT:
        return False
    
    manager.process_events(evento)
    
    if evento.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
        if evento.ui_element == herramientas.combo:
            estado.algoritmo_actual = evento.text
            estado.iteraciones.clear()
            estado.indice_actual = 0
            
            if estado.algoritmo_actual == "Graficas 3D":
                generar_datos_esfera()
                barra_estado.actualizar("Mostrando esfera 3D")
            else:
                barra_estado.actualizar(f"Algoritmo seleccionado: {estado.algoritmo_actual}")
            
            recalcular_curva()
    
    if evento.type == pygame_gui.UI_BUTTON_PRESSED:
        if evento.ui_element == herramientas.btn_reiniciar:
            estado.puntos_control.clear()
            estado.iteraciones.clear()
            estado.indice_actual = 0
            estado.ejecutando = False
            estado.punto_arrastrando = None
            barra_estado.actualizar("Proyecto reiniciado")
            actualizar_explicacion()
        
        elif evento.ui_element == herramientas.btn_cerrar_figura:
            if len(estado.puntos_control) >= 3 and estado.puntos_control[0] != estado.puntos_control[-1]:
                estado.puntos_control.append(estado.puntos_control[0])
                barra_estado.actualizar("Figura cerrada")
                recalcular_curva()
        
        elif evento.ui_element == herramientas.btn_ejecutar:
            manejar_ejecucion()
    
    if evento.type == pygame.MOUSEBUTTONDOWN:
        manejar_clic_mouse(evento)
    
    if evento.type == pygame.MOUSEMOTION:
        manejar_movimiento_mouse(evento)
    
    if evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
        estado.arrastrando = False
        estado.punto_arrastrando = None
    
    return True

def manejar_ejecucion():
    if estado.algoritmo_actual == "Traslacion":
        aplicar_traslacion()
    elif estado.algoritmo_actual == "Rotacion":
        aplicar_rotacion()
    elif estado.algoritmo_actual == "Bezier":
        if len(estado.puntos_control) < 3:
            barra_estado.actualizar("Bezier requiere minimo 3 puntos")
        else:
            estado.iteraciones = bezier(estado.puntos_control)
            estado.indice_actual = 0
            estado.ejecutando = True
            barra_estado.actualizar(f"Ejecutando {estado.algoritmo_actual}")
            actualizar_explicacion()
    elif estado.algoritmo_actual == "B-Spline":
        if len(estado.puntos_control) < 4:
            barra_estado.actualizar("B-Spline requiere minimo 4 puntos")
        else:
            estado.iteraciones = bspline(estado.puntos_control)
            estado.indice_actual = 0
            estado.ejecutando = True
            barra_estado.actualizar(f"Ejecutando {estado.algoritmo_actual}")
            actualizar_explicacion()
    elif estado.algoritmo_actual == "Graficas 3D":
        generar_datos_esfera()
        barra_estado.actualizar("Mostrando esfera 3D")
        actualizar_explicacion()
    else:
        if len(estado.puntos_control) < 2:
            barra_estado.actualizar("Seleccione al menos 2 puntos")
        else:
            ejecutar_lineas()
            barra_estado.actualizar(f"Ejecutando {estado.algoritmo_actual}")

def manejar_clic_mouse(evento):
    mouse_x, mouse_y = evento.pos
    dentro_lienzo = (CONFIG['ANCHO_HERRAMIENTAS'] <= mouse_x <= CONFIG['ANCHO_HERRAMIENTAS'] + CONFIG['ANCHO_LIENZO'] and
                    mouse_y <= CONFIG['ALTO_LIENZO'])
    
    if not dentro_lienzo:
        return
    
    if evento.button == 1:  # Click izquierdo
        for i, punto in enumerate(estado.puntos_control):
            px, py = camara.mundo_a_pantalla(punto[0], punto[1])
            px += CONFIG['ANCHO_HERRAMIENTAS']
            if abs(px - mouse_x) < 10 and abs(py - mouse_y) < 10:
                estado.punto_arrastrando = i
                estado.arrastrando = True
                return
        
        # Agregar nuevo punto
        gx, gy = camara.pantalla_a_mundo(mouse_x - CONFIG['ANCHO_HERRAMIENTAS'], mouse_y)
        estado.puntos_control.append((gx, gy))
        barra_estado.actualizar(f"Punto agregado ({gx},{gy})")
        recalcular_curva()
    
    elif evento.button == 4:  # Zoom +
        camara.zoom = min(camara.zoom + 2, CONFIG['ZOOM_MAX'])
    elif evento.button == 5:  # Zoom -
        camara.zoom = max(camara.zoom - 2, CONFIG['ZOOM_MIN'])

def manejar_movimiento_mouse(evento):
    if estado.arrastrando and estado.punto_arrastrando is not None:
        mouse_x, mouse_y = evento.pos
        gx, gy = camara.pantalla_a_mundo(mouse_x - CONFIG['ANCHO_HERRAMIENTAS'], mouse_y)
        estado.puntos_control[estado.punto_arrastrando] = (gx, gy)
        recalcular_curva()
        if estado.iteraciones:
            actualizar_explicacion()

# ============ CICLO PRINCIPAL ============
def main():
    running = True
    
    while running:
        tiempo = reloj.tick(60)
        manager.update(tiempo / 1000.0)
        
        # Procesar eventos
        for evento in pygame.event.get():
            if not manejar_eventos(evento):
                running = False
        
        # Actualizar animación
        if estado.ejecutando:
            estado.temporizador += tiempo
            if estado.temporizador >= CONFIG['VELOCIDAD_MS']:
                estado.temporizador = 0
                if estado.indice_actual < len(estado.iteraciones):
                    estado.indice_actual += 1
                    actualizar_explicacion()
                else:
                    estado.ejecutando = False
                    barra_estado.actualizar("Simulacion finalizada")
        
        # Dibujar
        pantalla.fill(CONFIG['COLOR_FONDO'])
        
        # Panel izquierdo
        pygame.draw.rect(pantalla, CONFIG['COLOR_PANEL'], (0, 0, CONFIG['ANCHO_HERRAMIENTAS'], CONFIG['ALTO_LIENZO']))
        
        # Lienzo
        pygame.draw.rect(pantalla, CONFIG['COLOR_LIENZO'], 
                        (CONFIG['ANCHO_HERRAMIENTAS'], 0, CONFIG['ANCHO_LIENZO'], CONFIG['ALTO_LIENZO']))
        
        superficie_lienzo = pantalla.subsurface(
            (CONFIG['ANCHO_HERRAMIENTAS'], 0, CONFIG['ANCHO_LIENZO'], CONFIG['ALTO_LIENZO'])
        )
        
        dibujar_cuadricula(superficie_lienzo, camara, CONFIG['ANCHO_LIENZO'], CONFIG['ALTO_LIENZO'])
        
        if estado.algoritmo_actual == "Graficas 3D":
            dibujar_esfera(superficie_lienzo)
        else:
            dibujar_curvas(superficie_lienzo)
        
        panel_explicacion.dibujar(pantalla)
        dibujar_info_lateral(pantalla)
        barra_estado.dibujar(pantalla, fuente)
        manager.draw_ui(pantalla)
        
        pygame.display.update()
    
    pygame.quit()

if __name__ == "__main__":
    main()