import pygame
import pygame_gui

from algoritmos.dda import calcular as dda
from algoritmos.bresenham import calcular as bresenham
from algoritmos.bezier import calcular as bezier
from algoritmos.bspline import calcular as bspline

from modelos.iteracion import Iteracion

from graficos.camara import Camara
from graficos.cuadricula import dibujar as dibujar_cuadricula
from graficos.lienzo import Lienzo

from ui.barra_estado import BarraEstado
from ui.barra_herramientas import BarraHerramientas
from ui.panel_explicacion import PanelExplicacion
from algoritmos.explicaciones import ExplicadorAlgoritmos

# configuraciones

ANCHO = 1400
ALTO = 800

ANCHO_HERRAMIENTAS = 250
ANCHO_PANEL = 480
ALTO_ESTADO = 40

ANCHO_LIENZO = (
        ANCHO
        - ANCHO_HERRAMIENTAS
        - ANCHO_PANEL
)

ALTO_LIENZO = ALTO - ALTO_ESTADO

# inicializacion

pygame.init()

pantalla = pygame.display.set_mode(
    (
        ANCHO,
        ALTO
    )
)

pygame.display.set_caption(
    "Visualizador de Algoritmos de Graficacion"
)

reloj = pygame.time.Clock()

manager = pygame_gui.UIManager(
    (
        ANCHO,
        ALTO
    )
)

fuente = pygame.font.SysFont(
    "Consolas",
    18
)

# objetos

camara = Camara()

lienzo = Lienzo()

barra_estado = BarraEstado()

herramientas = BarraHerramientas(
    manager
)

# Nuevo panel de explicación
panel_explicacion = PanelExplicacion(
    ANCHO - ANCHO_PANEL,  # x
    0,  # y
    ANCHO_PANEL,  # ancho
    ALTO_LIENZO  # alto
)

explicador = ExplicadorAlgoritmos()

# variables globales

algoritmo_actual = "DDA"

puntos_control = []

iteraciones = []

ejecutando = False

indice_actual = 0

temporizador = 0

VELOCIDAD_MS = 200

# configuracion de acciones de interfaz

punto_arrastrando = None

arrastrando = False

mostrar_curva_completa = False


# func auxiliares

def actualizar_explicacion():
    """Actualiza el panel de explicación según el estado actual"""
    texto = ""

    if not iteraciones:
        # Mostrar explicación inicial del algoritmo
        if algoritmo_actual == "DDA":
            if len(puntos_control) >= 2:
                x1, y1 = puntos_control[0]
                x2, y2 = puntos_control[1]
                texto = explicador.dda(x1, y1, x2, y2, 0, 0)
            else:
                texto = r"""
                \textbf{Algoritmo DDA (Digital Differential Analyzer)}

                Selecciona al menos 2 puntos para comenzar.

                El DDA calcula puntos intermedios mediante
                interpolación lineal entre dos puntos.
                """
        elif algoritmo_actual == "Bresenham":
            if len(puntos_control) >= 2:
                x1, y1 = puntos_control[0]
                x2, y2 = puntos_control[1]
                texto = explicador.bresenham(x1, y1, x2, y2, 0, 0)
            else:
                texto = r"""
                \textbf{Algoritmo de Bresenham}

                Selecciona al menos 2 puntos para comenzar.

                Bresenham usa aritmética entera para rasterizar
                líneas de manera eficiente.
                """
        elif algoritmo_actual == "Bezier":
            if len(puntos_control) >= 3:
                texto = explicador.bezier(puntos_control, 0, 0)
            else:
                texto = r"""
                \textbf{Curva de Bézier}

                Selecciona al menos 3 puntos de control.

                La curva usa polinomios de Bernstein para
                generar una curva suave.
                """
        elif algoritmo_actual == "B-Spline":
            if len(puntos_control) >= 4:
                texto = explicador.bspline(puntos_control, 0, 0)
            else:
                texto = r"""
                \textbf{Curva B-Spline Cúbica}

                Selecciona al menos 4 puntos de control.

                Las B-Splines generan curvas suaves con
                control local.
                """
        elif algoritmo_actual == "Traslacion":
            if len(puntos_control) > 0:
                try:
                    tx = int(herramientas.input_tx.get_text())
                    ty = int(herramientas.input_ty.get_text())
                    texto = explicador.traslacion(puntos_control, tx, ty, 0, 0)
                except:
                    texto = r"""
                    \textbf{Transformación de Traslación}

                    Ingresa valores numéricos para Tx y Ty.

                    La traslación mueve todos los puntos
                    sumando un vector constante.
                    """
            else:
                texto = r"""
                \textbf{Transformación de Traslación}

                Agrega puntos para trasladar.

                La traslación es una transformación
                geométrica fundamental.
                """
    else:
        # Mostrar explicación del paso actual
        paso = min(indice_actual, len(iteraciones) - 1)
        if paso >= 0 and paso < len(iteraciones) and len(iteraciones) > 0:
            iteracion = iteraciones[paso]

            if algoritmo_actual == "DDA":
                if len(puntos_control) >= 2:
                    x1, y1 = puntos_control[0]
                    x2, y2 = puntos_control[1]
                    texto = explicador.dda(
                        x1, y1, x2, y2,
                        indice_actual,
                        len(iteraciones)
                    )
                else:
                    texto = "Error: puntos insuficientes"

            elif algoritmo_actual == "Bresenham":
                if len(puntos_control) >= 2:
                    x1, y1 = puntos_control[0]
                    x2, y2 = puntos_control[1]
                    texto = explicador.bresenham(
                        x1, y1, x2, y2,
                        indice_actual,
                        iteracion.error
                    )
                else:
                    texto = "Error: puntos insuficientes"

            elif algoritmo_actual == "Bezier":
                texto = explicador.bezier(
                    puntos_control,
                    indice_actual,
                    len(iteraciones),
                    indice_actual / len(iteraciones) if len(iteraciones) > 0 else 0
                )

            elif algoritmo_actual == "B-Spline":
                texto = explicador.bspline(
                    puntos_control,
                    indice_actual,
                    len(iteraciones),
                    indice_actual / len(iteraciones) if len(iteraciones) > 0 else 0
                )

            elif algoritmo_actual == "Traslacion":
                if len(puntos_control) > 0:
                    try:
                        tx = int(herramientas.input_tx.get_text())
                        ty = int(herramientas.input_ty.get_text())
                        texto = explicador.traslacion(
                            puntos_control,
                            tx, ty,
                            indice_actual,
                            len(puntos_control)
                        )
                    except:
                        texto = "Error en valores de traslación"
                else:
                    texto = "No hay puntos para trasladar"

    panel_explicacion.actualizar(texto, fuente)


def recalcular_curva():
    global iteraciones
    global indice_actual

    if algoritmo_actual == "Bezier":

        if len(puntos_control) >= 3:
            iteraciones = bezier(
                puntos_control
            )

            indice_actual = len(
                iteraciones
            )

            actualizar_explicacion()

    elif algoritmo_actual == "B-Spline":

        if len(puntos_control) >= 4:
            iteraciones = bspline(
                puntos_control
            )

            indice_actual = len(
                iteraciones
            )

            actualizar_explicacion()


def aplicar_traslacion():
    global puntos_control
    global iteraciones
    global indice_actual

    try:

        tx = int(
            herramientas.input_tx.get_text()
        )

        ty = int(
            herramientas.input_ty.get_text()
        )

    except:

        barra_estado.actualizar(
            "Tx y Ty deben ser numericos"
        )

        return

    nuevos = []

    iteraciones = []

    paso = 1

    for x, y in puntos_control:
        nx = x + tx
        ny = y + ty

        nuevos.append(
            (
                nx,
                ny
            )
        )

        iteraciones.append(
            Iteracion(
                paso,
                nx,
                ny,
                round(nx),
                round(ny)
            )
        )

        paso += 1

    puntos_control = nuevos

    indice_actual = len(
        iteraciones
    )

    barra_estado.actualizar(
        f"Traslacion aplicada ({tx},{ty})"
    )

    actualizar_explicacion()


def ejecutar_lineas():
    global iteraciones
    global ejecutando
    global indice_actual

    iteraciones = []

    for i in range(
            len(puntos_control) - 1
    ):

        p1 = puntos_control[i]

        p2 = puntos_control[i + 1]

        if algoritmo_actual == "DDA":

            segmento = dda(
                p1[0],
                p1[1],
                p2[0],
                p2[1]
            )

        else:

            segmento = bresenham(
                p1[0],
                p1[1],
                p2[0],
                p2[1]
            )

        if i > 0:
            segmento = segmento[1:]

        iteraciones.extend(
            segmento
        )

    indice_actual = 0

    ejecutando = True

    actualizar_explicacion()


# ciclo principal
running = True

while running:

    tiempo = reloj.tick(60)

    manager.update(
        tiempo / 1000.0
    )

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            running = False

        manager.process_events(
            evento
        )

        # cambios de algoritmo

        if evento.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:

            if evento.ui_element == herramientas.combo:
                algoritmo_actual = evento.text

                iteraciones.clear()

                indice_actual = 0

                barra_estado.actualizar(
                    f"Algoritmo seleccionado: {algoritmo_actual}"
                )

                recalcular_curva()

                # Actualizar explicación para el nuevo algoritmo
                actualizar_explicacion()

        # botoncitos

        if evento.type == pygame_gui.UI_BUTTON_PRESSED:

            # reiniciar

            if evento.ui_element == herramientas.btn_reiniciar:

                puntos_control.clear()

                iteraciones.clear()

                indice_actual = 0

                ejecutando = False

                punto_arrastrando = None

                barra_estado.actualizar(
                    "Proyecto reiniciado"
                )

                actualizar_explicacion()

            # cerrar la figura

            elif evento.ui_element == herramientas.btn_cerrar_figura:

                if len(puntos_control) >= 3:

                    if (
                            puntos_control[0]
                            !=
                            puntos_control[-1]
                    ):
                        puntos_control.append(
                            puntos_control[0]
                        )

                        barra_estado.actualizar(
                            "Figura cerrada"
                        )

                        recalcular_curva()

            # ejecutar

            elif evento.ui_element == herramientas.btn_ejecutar:

                if algoritmo_actual == "Traslacion":

                    aplicar_traslacion()

                elif algoritmo_actual == "Bezier":

                    if len(puntos_control) < 3:

                        barra_estado.actualizar(
                            "Bezier requiere minimo 3 puntos"
                        )

                    else:

                        iteraciones = bezier(
                            puntos_control
                        )

                        indice_actual = 0

                        ejecutando = True

                        barra_estado.actualizar(
                            f"Ejecutando {algoritmo_actual}"
                        )

                        actualizar_explicacion()

                elif algoritmo_actual == "B-Spline":

                    if len(puntos_control) < 4:

                        barra_estado.actualizar(
                            "B-Spline requiere minimo 4 puntos"
                        )

                    else:

                        iteraciones = bspline(
                            puntos_control
                        )

                        indice_actual = 0

                        ejecutando = True

                        barra_estado.actualizar(
                            f"Ejecutando {algoritmo_actual}"
                        )

                        actualizar_explicacion()

                else:

                    if len(puntos_control) < 2:

                        barra_estado.actualizar(
                            "Seleccione al menos 2 puntos"
                        )

                    else:

                        ejecutar_lineas()

                        barra_estado.actualizar(
                            f"Ejecutando {algoritmo_actual}"
                        )

        # clics de mouse

        if evento.type == pygame.MOUSEBUTTONDOWN:

            mouse_x, mouse_y = evento.pos

            dentro_lienzo = (
                    ANCHO_HERRAMIENTAS
                    <= mouse_x
                    <= ANCHO_HERRAMIENTAS + ANCHO_LIENZO
                    and
                    mouse_y <= ALTO_LIENZO
            )

            if dentro_lienzo:

                # izquiero

                if evento.button == 1:

                    encontrado = False

                    for i, punto in enumerate(
                            puntos_control
                    ):

                        px, py = camara.mundo_a_pantalla(
                            punto[0],
                            punto[1]
                        )

                        px += ANCHO_HERRAMIENTAS

                        if (
                                abs(px - mouse_x) < 10
                                and
                                abs(py - mouse_y) < 10
                        ):
                            punto_arrastrando = i

                            arrastrando = True

                            encontrado = True

                            break

                    if not encontrado:
                        gx, gy = camara.pantalla_a_mundo(
                            mouse_x - ANCHO_HERRAMIENTAS,
                            mouse_y
                        )

                        puntos_control.append(
                            (
                                gx,
                                gy
                            )
                        )

                        barra_estado.actualizar(
                            f"Punto agregado ({gx},{gy})"
                        )

                        recalcular_curva()

                        actualizar_explicacion()

                # aumentar zoom

                elif evento.button == 4:

                    camara.zoom += 2

                    if camara.zoom > 100:
                        camara.zoom = 100

                # disminuir zomm

                elif evento.button == 5:

                    camara.zoom -= 2

                    if camara.zoom < 5:
                        camara.zoom = 5

        # arrastrar puntos

        if evento.type == pygame.MOUSEMOTION:

            if (
                    arrastrando
                    and
                    punto_arrastrando is not None
            ):
                mouse_x, mouse_y = evento.pos

                gx, gy = camara.pantalla_a_mundo(
                    mouse_x - ANCHO_HERRAMIENTAS,
                    mouse_y
                )

                puntos_control[
                    punto_arrastrando
                ] = (
                    gx,
                    gy
                )

                recalcular_curva()

                # Actualizar explicación si hay iteraciones
                if iteraciones:
                    actualizar_explicacion()

        # soltvar el mause

        if evento.type == pygame.MOUSEBUTTONUP:

            if evento.button == 1:
                arrastrando = False

                punto_arrastrando = None

    # animacion de iteraciones

    if ejecutando:

        temporizador += tiempo

        if temporizador >= VELOCIDAD_MS:

            temporizador = 0

            if indice_actual < len(iteraciones):

                indice_actual += 1

                # Actualizar explicación en cada paso
                actualizar_explicacion()

            else:

                ejecutando = False

                barra_estado.actualizar(
                    "Simulacion finalizada"
                )

    # limpiar la pantalla

    pantalla.fill(
        (22, 22, 22)
    )

    # panel izquierdo

    pygame.draw.rect(
        pantalla,
        (30, 30, 30),
        (
            0,
            0,
            ANCHO_HERRAMIENTAS,
            ALTO_LIENZO
        )
    )

    # zona para el dibujo

    pygame.draw.rect(
        pantalla,
        (20, 20, 20),
        (
            ANCHO_HERRAMIENTAS,
            0,
            ANCHO_LIENZO,
            ALTO_LIENZO
        )
    )

    superficie_lienzo = pantalla.subsurface(
        (
            ANCHO_HERRAMIENTAS,
            0,
            ANCHO_LIENZO,
            ALTO_LIENZO
        )
    )

    dibujar_cuadricula(
        superficie_lienzo,
        camara,
        ANCHO_LIENZO,
        ALTO_LIENZO
    )

    # polilineas

    for i in range(
            len(puntos_control) - 1
    ):
        x1, y1 = puntos_control[i]
        x2, y2 = puntos_control[i + 1]

        px1, py1 = camara.mundo_a_pantalla(
            x1,
            y1
        )

        px2, py2 = camara.mundo_a_pantalla(
            x2,
            y2
        )

        pygame.draw.line(
            superficie_lienzo,
            (100, 150, 255),
            (
                px1 + camara.zoom // 2,
                py1 + camara.zoom // 2
            ),
            (
                px2 + camara.zoom // 2,
                py2 + camara.zoom // 2
            ),
            2
        )

    # manejo de puntos de ciontrol

    for i, punto in enumerate(
            puntos_control
    ):

        color = (0, 255, 0)

        if punto_arrastrando == i:
            color = (255, 0, 0)

        lienzo.dibujar_pixel(
            superficie_lienzo,
            camara,
            punto[0],
            punto[1],
            color
        )

    # curvas dinamicas

    if algoritmo_actual in [
        "Bezier",
        "B-Spline"
    ]:

        for punto in iteraciones:
            lienzo.dibujar_pixel(
                superficie_lienzo,
                camara,
                punto.x_redondeado,
                punto.y_redondeado,
                (255, 255, 0)
            )

    else:

        for i in range(indice_actual):

            if i >= len(iteraciones):
                break

            punto = iteraciones[i]

            lienzo.dibujar_pixel(
                superficie_lienzo,
                camara,
                punto.x_redondeado,
                punto.y_redondeado,
                (255, 255, 0)
            )

    # mostrar panel de explicación (reemplaza la tabla)
    panel_explicacion.dibujar(
        pantalla
    )

    # info lateral

    txt = fuente.render(
        f"Algoritmo: {algoritmo_actual}",
        True,
        (255, 255, 255)
    )

    pantalla.blit(
        txt,
        (20, 380)
    )

    txt = fuente.render(
        f"Puntos: {len(puntos_control)}",
        True,
        (255, 255, 255)
    )

    pantalla.blit(
        txt,
        (20, 410)
    )

    txt = fuente.render(
        f"Zoom: {camara.zoom}",
        True,
        (255, 255, 255)
    )

    pantalla.blit(
        txt,
        (20, 440)
    )

    txt = fuente.render(
        f"Paso: {indice_actual}/{len(iteraciones)}",
        True,
        (255, 255, 255)
    )

    pantalla.blit(
        txt,
        (20, 470)
    )

    # modificacion de los puntos

    try:

        tx = herramientas.input_tx.get_text()
        ty = herramientas.input_ty.get_text()

        txt = fuente.render(
            f"Tx={tx} Ty={ty}",
            True,
            (255, 255, 255)
        )

        pantalla.blit(
            txt,
            (20, 500)
        )

    except:
        pass

    # lista de puntos

    y_lista = 550

    for i, punto in enumerate(
            puntos_control[:8]
    ):
        texto = fuente.render(
            f"P{i}: {punto}",
            True,
            (255, 255, 255)
        )

        pantalla.blit(
            texto,
            (
                20,
                y_lista
            )
        )

        y_lista += 25

    # estado

    barra_estado.dibujar(
        pantalla,
        fuente
    )

    # interfaz

    manager.draw_ui(
        pantalla
    )

    pygame.display.update()

pygame.quit()