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
from algoritmos.cubo3d import EstadoCubo3D, dibujar_cubo, actualizar_cubo, manejar_clic_cubo, manejar_movimiento_cubo, manejar_soltar_cubo

# ============ CONFIGURACIÓN ============
CONFIG = {
    'ANCHO': 1600,
    'ALTO': 800,
    'ANCHO_HERRAMIENTAS': 280,
    'ANCHO_PANEL': 480,
    'ALTO_ESTADO': 40,
    'VELOCIDAD_MS': 180,
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
        self.angulo_3d_x = 90
        self.angulo_3d_y = 0
        self.arrastrando_3d = False
        self.ultimo_mouse_3d = None

estado = EstadoGlobal()
estado_cubo = EstadoCubo3D()  # Estado del cubo 3D

# ============ FUNCIONES DE TRANSFORMACIÓN ============
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

# ============ FUNCIONES 3D ============
def generar_datos_esfera():
    """Genera o devuelve datos de la esfera."""
    if estado.esfera_datos is None:
        estado.esfera_datos = generar_esfera(CONFIG['RADIO_ESFERA'], CONFIG['RESOLUCION_ESFERA'])
    return estado.esfera_datos

def proyectar_punto_3d(x, y, z):
    """Proyecta punto 3D a 2D con rotación."""
    ang_x, ang_y = np.radians(estado.angulo_3d_x), np.radians(estado.angulo_3d_y)
    cos_x, sin_x = np.cos(ang_x), np.sin(ang_x)
    cos_y, sin_y = np.cos(ang_y), np.sin(ang_y)
    
    # Rotación en Y
    x1, z1 = x * cos_y + z * sin_y, -x * sin_y + z * cos_y
    # Rotación en X
    y1, z2 = y * cos_x - z1 * sin_x, y * sin_x + z1 * cos_x
    
    factor = 4.5 / (4.5 + z2)
    return x1 * factor, y1 * factor, z2

def color_esfera_por_profundidad(z):
    """Calcula color basado en profundidad."""
    t = np.clip((z + CONFIG['RADIO_ESFERA']) / (2 * CONFIG['RADIO_ESFERA']), 0, 1)
    # Contraste cúbico
    t_contrastado = 2 * t * t if t < 0.5 else 1 - 2 * (1 - t) * (1 - t)
    rgba = cm.get_cmap('plasma')(np.clip(t_contrastado, 0, 1))
    brillo = 0.75 + 0.25 * t
    return tuple(int(c * 255 * brillo) for c in rgba[:3])

def dibujar_esfera(superficie):
    """Dibuja la esfera 3D."""
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

# ============ FUNCIONES DE ALGORITMOS ============
def recalcular_curva():
    """Recalcula la curva según el algoritmo actual."""
    if estado.algoritmo_actual == "Esfera 3D con rejillas":
        generar_datos_esfera()
        actualizar_explicacion()
        return
    
    if estado.algoritmo_actual == "Cubo 3D":
        actualizar_cubo(estado_cubo)
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
    """Aplica traslación a los puntos de control."""
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
    """Aplica rotación a los puntos de control."""
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
    """Ejecuta el algoritmo de línea (DDA o Bresenham)."""
    estado.iteraciones.clear()
    for i in range(len(estado.puntos_control) - 1):
        p1, p2 = estado.puntos_control[i], estado.puntos_control[i+1]
        segmento = (dda if estado.algoritmo_actual == "DDA" else bresenham)(p1[0], p1[1], p2[0], p2[1])
        estado.iteraciones.extend(segmento if i == 0 else segmento[1:])
    
    estado.indice_actual = 0
    estado.ejecutando = True
    actualizar_explicacion()

# ============ FUNCIONES DE UI ============
def actualizar_explicacion():
    """Actualiza el panel de explicación."""
    if estado.algoritmo_actual == "Cubo 3D":
        texto = explicador.cubo_3d(estado_cubo.angulo_x, estado_cubo.angulo_y, 
                                   estado_cubo.distancia_vista)
        panel_explicacion.actualizar(texto, fuente)
        return
    
    if not estado.iteraciones:
        texto = obtener_texto_inicial()
    else:
        texto = obtener_texto_por_paso()
    
    panel_explicacion.actualizar(texto, fuente)

def obtener_texto_inicial():
    """Obtiene texto inicial según el algoritmo."""
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
        
        "Cubo 3D": r"\textbf{Cubo 3D}" + "\n" +
                   r"Arrastra con el mouse para rotar." + "\n" +
                   r"Cubo renderizado en 3D con perspectiva." + "\n" +
                   r"Caras semi-transparentes para visibilidad."
    }
    
    if estado.algoritmo_actual in ["Traslacion", "Rotacion"] and estado.puntos_control:
        try:
            if estado.algoritmo_actual == "Traslacion":
                tx, ty = int(herramientas.input_tx.get_text()), int(herramientas.input_ty.get_text())
                datos = explicador.traslacion(estado.puntos_control, tx, ty, 0, 0)
            else:
                theta = float(herramientas.input_theta.get_text())
                datos = explicador.rotacion(estado.puntos_control, theta, 0, 0)
            return _dict_a_string(datos)
        except:
            pass
    if estado.algoritmo_actual == "Esfera 3D con rejillas":
        return explicador.esfera_3d(estado.angulo_3d_x, estado.angulo_3d_y)
    
    return textos.get(estado.algoritmo_actual, "")

def obtener_texto_por_paso():
    """Obtiene texto explicativo del paso actual."""
    paso = min(estado.indice_actual, len(estado.iteraciones) - 1)
    if paso < 0 or not estado.iteraciones:
        return ""
    
    if estado.algoritmo_actual == "Esfera 3D con rejillas":
        return explicador.esfera_3d(estado.angulo_3d_x, estado.angulo_3d_y)
    
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
    
    return _dict_a_string(datos.get(estado.algoritmo_actual, lambda: {})())

def _dict_a_string(datos):
    """Convierte diccionario a string formateado."""
    if isinstance(datos, str):
        return datos
    lineas = [r"\textbf{" + datos.get('titulo', '') + "}\n"] if 'titulo' in datos else []
    lineas.extend(linea['texto'] for linea in datos.get('lineas', []))
    return "\n".join(lineas)

# ============ FUNCIONES DE DIBUJO ============
def dibujar_info_lateral(pantalla):
    """Dibuja información lateral en pantalla."""
    # Colores para mejor legibilidad
    COLOR_TITULO = (255, 255, 100)  # Amarillo
    COLOR_TEXTO = (255, 255, 255)   # Blanco
    COLOR_SECCION = (100, 200, 255) # Celeste
    COLOR_VALOR = (200, 255, 200)   # Verde claro
    
    # Separadores visuales
    SEPARADOR = "-" * 20
    
    y = 380
    margen_izquierdo = 10
    espacio_entre_lineas = 30
    
    # --- SECCIÓN 1: Información general ---
    titulo = f"=== {estado.algoritmo_actual.upper()} ==="
    pantalla.blit(fuente.render(titulo, True, COLOR_TITULO), (margen_izquierdo, y))
    y += espacio_entre_lineas + 5
    
    info_general = [
        f"Puntos: {len(estado.puntos_control)}",
        f"Zoom: {camara.zoom:.1f}x",
        f"Paso: {estado.indice_actual}/{len(estado.iteraciones)}"
    ]
    
    for texto in info_general:
        pantalla.blit(fuente.render(texto, True, COLOR_TEXTO), (margen_izquierdo, y))
        y += espacio_entre_lineas
    
    # Separador
    y += 5
    pantalla.blit(fuente.render(SEPARADOR, True, (100, 100, 100)), (margen_izquierdo, y))
    y += espacio_entre_lineas
    
    # --- SECCIÓN 2: Controles 3D (si aplica) ---
    if estado.algoritmo_actual == "Esfera 3D con rejillas":
        pantalla.blit(fuente.render("CONTROLES 3D", True, COLOR_SECCION), (margen_izquierdo, y))
        y += espacio_entre_lineas
        
        info_3d = [
            f"Rotación X: {estado.angulo_3d_x}°",
            f"Rotación Y: {estado.angulo_3d_y}°",
            "[Arrastra para rotar]"
        ]
        for texto in info_3d:
            pantalla.blit(fuente.render(texto, True, COLOR_TEXTO), (margen_izquierdo + 10, y))
            y += espacio_entre_lineas
        
    elif estado.algoritmo_actual == "Cubo 3D":
        pantalla.blit(fuente.render("CONTROLES 3D", True, COLOR_SECCION), (margen_izquierdo, y))
        y += espacio_entre_lineas
        
        info_3d = [
            f"Rotación X: {np.degrees(estado_cubo.angulo_x):.1f}°",
            f"Rotación Y: {np.degrees(estado_cubo.angulo_y):.1f}°",
            f"Distancia vista: {estado_cubo.distancia_vista:.1f}",
            "[Arrastra para rotar]"
        ]
        for texto in info_3d:
            pantalla.blit(fuente.render(texto, True, COLOR_TEXTO), (margen_izquierdo + 10, y))
            y += espacio_entre_lineas
    
    # Separador (si hay sección 3D)
    if estado.algoritmo_actual in ["Esfera 3D con rejillas", "Cubo 3D"]:
        y += 5
        pantalla.blit(fuente.render(SEPARADOR, True, (100, 100, 100)), (margen_izquierdo, y))
        y += espacio_entre_lineas
    
    # --- SECCIÓN 3: Transformaciones (si aplica) ---
    try:
        tx = herramientas.input_tx.get_text()
        ty = herramientas.input_ty.get_text()
        theta = herramientas.input_theta.get_text()
        
        if tx or ty or theta:
            pantalla.blit(fuente.render("TRANSFORMACIONES", True, COLOR_SECCION), (margen_izquierdo, y))
            y += espacio_entre_lineas
            
            if tx and ty:
                pantalla.blit(fuente.render(f"Traslación: Tx={tx}, Ty={ty}", True, COLOR_TEXTO), (margen_izquierdo + 10, y))
                y += espacio_entre_lineas
            if theta:
                pantalla.blit(fuente.render(f"Rotación: θ={theta}°", True, COLOR_TEXTO), (margen_izquierdo + 10, y))
                y += espacio_entre_lineas
            
            y += 5
            pantalla.blit(fuente.render(SEPARADOR, True, (100, 100, 100)), (margen_izquierdo, y))
            y += espacio_entre_lineas
    except:
        pass
    
    # --- SECCIÓN 4: Puntos de control ---
    if estado.puntos_control:
        pantalla.blit(fuente.render("PUNTOS DE CONTROL", True, COLOR_SECCION), (margen_izquierdo, y))
        y += espacio_entre_lineas
        
        # Mostrar puntos en columnas si son muchos
        puntos_mostrar = estado.puntos_control[:12]  # Limitar a 12 puntos
        for i, punto in enumerate(puntos_mostrar):
            # Formato más compacto
            texto_punto = f"P{i}: ({punto[0]:.1f}, {punto[1]:.1f})" if isinstance(punto, (list, tuple)) and len(punto) >= 2 else f"P{i}: {punto}"
            
            # Colores alternados para legibilidad
            color = COLOR_VALOR if i % 2 == 0 else COLOR_TEXTO
            pantalla.blit(fuente.render(texto_punto, True, color), (margen_izquierdo + 10, y))
            y += espacio_entre_lineas
            
            # Si hay demasiados puntos, mostrar indicador
            if i == 11 and len(estado.puntos_control) > 12:
                pantalla.blit(fuente.render(f"... y {len(estado.puntos_control) - 12} más", True, (150, 150, 150)), (margen_izquierdo + 10, y))
                break

def dibujar_curvas(superficie):
    """Dibuja curvas y puntos de control."""
    # Polilíneas de control
    for i in range(len(estado.puntos_control) - 1):
        x1, y1 = estado.puntos_control[i]
        x2, y2 = estado.puntos_control[i + 1]
        px1, py1 = camara.mundo_a_pantalla(x1, y1)
        px2, py2 = camara.mundo_a_pantalla(x2, y2)
        offset = camara.zoom // 2
        pygame.draw.line(superficie, (100, 150, 255),
                        (px1 + offset, py1 + offset),
                        (px2 + offset, py2 + offset), 2)
    
    # Puntos de control
    for i, punto in enumerate(estado.puntos_control):
        color = (255, 0, 0) if estado.punto_arrastrando == i else (0, 255, 0)
        lienzo.dibujar_pixel(superficie, camara, punto[0], punto[1], color)
    
    # Iteraciones
    if estado.algoritmo_actual in ["Bezier", "B-Spline"]:
        iteraciones_a_dibujar = estado.iteraciones
    else:
        iteraciones_a_dibujar = estado.iteraciones[:estado.indice_actual]
    
    for punto in iteraciones_a_dibujar:
        lienzo.dibujar_pixel(superficie, camara, punto.x_redondeado, punto.y_redondeado, (255, 255, 0))

# ============ MANEJADORES DE EVENTOS ============
def manejar_eventos(evento):
    """Maneja eventos de pygame."""
    if evento.type == pygame.QUIT:
        return False
    
    manager.process_events(evento)
    
    if evento.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED and evento.ui_element == herramientas.combo:
        estado.algoritmo_actual = evento.text
        estado.iteraciones.clear()
        estado.indice_actual = 0
        
        if estado.algoritmo_actual == "Esfera 3D con rejillas":
            generar_datos_esfera()
            barra_estado.actualizar("Mostrando esfera 3D - Arrastra para rotar")
        elif estado.algoritmo_actual == "Cubo 3D":
            actualizar_cubo(estado_cubo)
            barra_estado.actualizar("Mostrando cubo 3D - Arrastra para rotar")
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
        manejar_soltar_cubo(estado_cubo)
    
    return True

def manejar_boton(evento):
    """Maneja eventos de botones."""
    if evento.ui_element == herramientas.btn_reiniciar:
        estado.puntos_control.clear()
        estado.iteraciones.clear()
        estado.indice_actual = 0
        estado.ejecutando = False
        estado.punto_arrastrando = None
        estado.angulo_3d_x, estado.angulo_3d_y = 35, 25
        # Resetear cubo
        estado_cubo.angulo_x = 0
        estado_cubo.angulo_y = 0
        estado_cubo.distancia_vista = 5
        estado_cubo.proyecciones = None
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
    """Maneja la ejecución del algoritmo seleccionado."""
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
    """Maneja clicks del mouse en el lienzo."""
    mouse_x, mouse_y = evento.pos
    dentro_lienzo = (CONFIG['ANCHO_HERRAMIENTAS'] <= mouse_x <= CONFIG['ANCHO_HERRAMIENTAS'] + CONFIG['ANCHO_LIENZO'] and
                    mouse_y <= CONFIG['ALTO_LIENZO'])
    
    if not dentro_lienzo:
        return
    
    # Modo cubo 3D
    if estado.algoritmo_actual == "Cubo 3D":
        manejar_clic_cubo(evento, estado_cubo)
        return
    
    # Modo esfera 3D
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
        # Buscar punto para arrastrar
        for i, punto in enumerate(estado.puntos_control):
            px, py = camara.mundo_a_pantalla(punto[0], punto[1])
            if abs(px + CONFIG['ANCHO_HERRAMIENTAS'] - mouse_x) < 10 and abs(py - mouse_y) < 10:
                estado.punto_arrastrando = i
                estado.arrastrando = True
                return
        
        # Agregar nuevo punto
        gx, gy = camara.pantalla_a_mundo(mouse_x - CONFIG['ANCHO_HERRAMIENTAS'], mouse_y)
        estado.puntos_control.append((gx, gy))
        barra_estado.actualizar(f"Punto agregado ({gx},{gy})")
        recalcular_curva()
    
    elif evento.button == 4:
        camara.zoom = min(camara.zoom + 2, CONFIG['ZOOM_MAX'])
    elif evento.button == 5:
        camara.zoom = max(camara.zoom - 2, CONFIG['ZOOM_MIN'])

def manejar_movimiento_mouse(evento):
    """Maneja movimiento del mouse."""
    # Rotación 3D de la esfera
    if estado.arrastrando_3d and estado.ultimo_mouse_3d:
        dx = evento.pos[0] - estado.ultimo_mouse_3d[0]
        dy = evento.pos[1] - estado.ultimo_mouse_3d[1]
        estado.angulo_3d_y = (estado.angulo_3d_y + dx * 0.5) % 360
        estado.angulo_3d_x = np.clip(estado.angulo_3d_x + dy * 0.5, -90, 90)
        estado.ultimo_mouse_3d = evento.pos
        actualizar_explicacion()
        return
    
    # Rotación del cubo 3D
    if estado.algoritmo_actual == "Cubo 3D":
        manejar_movimiento_cubo(evento, estado_cubo)
        actualizar_explicacion()
        return
    
    # Arrastre de puntos
    if estado.arrastrando and estado.punto_arrastrando is not None:
        gx, gy = camara.pantalla_a_mundo(evento.pos[0] - CONFIG['ANCHO_HERRAMIENTAS'], evento.pos[1])
        estado.puntos_control[estado.punto_arrastrando] = (gx, gy)
        recalcular_curva()
        if estado.iteraciones:
            actualizar_explicacion()

# ============ CICLO PRINCIPAL ============
def main():
    """Bucle principal del programa."""
    running = True
    
    while running:
        tiempo = reloj.tick(60)
        manager.update(tiempo / 1000.0)
        
        # Procesar eventos
        for evento in pygame.event.get():
            if not manejar_eventos(evento):
                running = False
        
        # Actualizar animación
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
        
        # Dibujar
        pantalla.fill(CONFIG['COLOR_FONDO'])
        pygame.draw.rect(pantalla, CONFIG['COLOR_PANEL'], (0, 0, CONFIG['ANCHO_HERRAMIENTAS'], CONFIG['ALTO_LIENZO']))
        pygame.draw.rect(pantalla, CONFIG['COLOR_LIENZO'], 
                        (CONFIG['ANCHO_HERRAMIENTAS'], 0, CONFIG['ANCHO_LIENZO'], CONFIG['ALTO_LIENZO']))
        
        superficie_lienzo = pantalla.subsurface(
            (CONFIG['ANCHO_HERRAMIENTAS'], 0, CONFIG['ANCHO_LIENZO'], CONFIG['ALTO_LIENZO'])
        )
        
        dibujar_cuadricula(superficie_lienzo, camara, CONFIG['ANCHO_LIENZO'], CONFIG['ALTO_LIENZO'])
        
        # Dibujar según el algoritmo
        if estado.algoritmo_actual == "Esfera 3D con rejillas":
            dibujar_esfera(superficie_lienzo)
        elif estado.algoritmo_actual == "Cubo 3D":
            dibujar_cubo(superficie_lienzo, estado_cubo, camara, CONFIG)
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