import math
import numpy as np

# Paleta del panel
C_AZUL = (100, 200, 255)
C_NARANJA = (255, 150, 100)
C_MORADO = (200, 150, 255)
C_VERDE = (100, 255, 200)
C_AMARILLO = (255, 220, 120)
C_TEXTO = (215, 215, 215)
C_SUAVE = (180, 180, 180)
C_FORMULA = (255, 255, 210)
C_RESULTADO = (150, 255, 150)
C_ALERTA = (255, 150, 150)


def _doc(titulo, color, bloques):
    return {
        "titulo": titulo,
        "color": color,
        "bloques": bloques,
    }


def _seccion(texto):
    return {"tipo": "seccion", "texto": texto, "color": C_AMARILLO}


def _txt(texto, color=C_TEXTO):
    return {"tipo": "texto", "texto": texto, "color": color}


def _formula(latex, fontsize=18):
    return {
        "tipo": "formula",
        "latex": latex,
        "color": C_FORMULA,
        "fontsize": fontsize,
    }


def _matriz(nombre, filas):
    return {
        "tipo": "matriz",
        "nombre": nombre,
        "filas": filas,
        "color": C_FORMULA,
    }


def _res(texto):
    return {"tipo": "resultado", "texto": texto, "color": C_RESULTADO}


def _alerta(texto):
    return {"tipo": "alerta", "texto": texto, "color": C_ALERTA}


def _espacio(alto=8):
    return {"tipo": "espacio", "alto": alto}


class ExplicadorAlgoritmos:
    @staticmethod
    def intro(nombre_algoritmo, puntos=None):
        puntos = puntos or []

        if nombre_algoritmo == "DDA":
            return _doc("DDA · Línea paso a paso", C_AZUL, [
                _seccion("¿Qué hace?"),
                _txt("Dibuja una línea recta avanzando poco a poco desde un punto inicial hasta un punto final."),
                _txt("Piensa en una persona caminando de A hacia B dando pasos del mismo tamaño."),
                _seccion("¿Qué necesitas hacer?"),
                _txt("Coloca al menos 2 puntos en el lienzo y presiona Ejecutar."),
                _formula(r"x_{nuevo}=x_{actual}+x_{inc}"),
                _formula(r"y_{nuevo}=y_{actual}+y_{inc}"),
                _txt("La pantalla solo puede pintar píxeles enteros, por eso las posiciones decimales se redondean."),
            ])

        if nombre_algoritmo == "Bresenham":
            return _doc("Bresenham · Línea con enteros", C_NARANJA, [
                _seccion("¿Qué hace?"),
                _txt("También dibuja líneas, pero toma decisiones usando números enteros."),
                _txt("Eso lo hace más eficiente que DDA, porque evita trabajar con muchos decimales."),
                _seccion("Idea principal"),
                _txt("En cada paso decide si el siguiente píxel debe avanzar solo en X o también en Y."),
                _txt("Para decidirlo usa una variable llamada error."),
                _formula(r"e_2=2\cdot error"),
                _txt("Si el error crece demasiado, el algoritmo corrige el camino del píxel."),
            ])

        if nombre_algoritmo == "Bezier":
            return _doc("Bézier · Curva flexible", C_AZUL, [
                _seccion("¿Qué hace?"),
                _txt("Crea una curva suave usando puntos de control."),
                _txt("El primer punto indica dónde empieza la curva y el último dónde termina."),
                _txt("Los puntos intermedios funcionan como imanes: jalan la curva, aunque normalmente la curva no pasa exactamente por ellos."),
                _seccion("Fórmula principal"),
                _formula(r"B(t)=\sum_{i=0}^{n}\binom{n}{i}(1-t)^{n-i}t^iP_i", fontsize=16),
                _txt("El valor t avanza de 0 a 1. Cuando t cambia, se calcula un nuevo punto de la curva."),
            ])

        if nombre_algoritmo == "B-Spline":
            return _doc("B-Spline · Curva por tramos", C_MORADO, [
                _seccion("¿Qué hace?"),
                _txt("Crea curvas suaves, pero con más control local que Bézier."),
                _txt("Mover un punto no cambia toda la curva, solo afecta una parte cercana."),
                _seccion("Requisito"),
                _txt("Necesitas al menos 4 puntos de control."),
                _seccion("Matriz usada"),
                _formula(r"Q(t)=[t^3\ t^2\ t\ 1]\cdot rac{1}{6}\cdot M\cdot P", fontsize=16),
                _matriz("M", [["-1", "3", "-3", "1"], ["3", "-6", "3", "0"], ["-3", "0", "3", "0"], ["1", "4", "1", "0"]]),
            ])

        if nombre_algoritmo == "Traslacion":
            return _doc("Traslación · Mover una figura", C_VERDE, [
                _seccion("¿Qué hace?"),
                _txt("Mueve todos los puntos de una figura la misma distancia."),
                _txt("La figura no cambia de tamaño ni se deforma: solo cambia de lugar."),
                _seccion("Matriz de traslación"),
                _matriz("T", [["1", "0", "tx"], ["0", "1", "ty"], ["0", "0", "1"]]),
                _txt("tx mueve la figura en horizontal. ty la mueve en vertical."),
            ])

        if nombre_algoritmo == "Rotacion":
            return _doc("Rotación · Girar una figura", C_MORADO, [
                _seccion("¿Qué hace?"),
                _txt("Gira una figura alrededor de un punto central."),
                _txt("La figura conserva su tamaño, pero cambia su orientación."),
                _seccion("Matriz de rotación"),
                _matriz("R", [["cosθ", "-sinθ", "0"], ["sinθ", "cosθ", "0"], ["0", "0", "1"]]),
                _txt("El ángulo θ indica cuánto se gira la figura."),
            ])

        if nombre_algoritmo == "Esfera 3D con rejillas":
            return ExplicadorAlgoritmos.esfera_3d(0, 0)

        if nombre_algoritmo == "Cubo 3D":
            return ExplicadorAlgoritmos.cubo_3d(0, 0, 2)

        if nombre_algoritmo == "Esfera 3D Interactiva":
            return _doc("Esfera interactiva · Luz y sombra", C_AZUL, [
                _seccion("¿Qué hace?"),
                _txt("Muestra una esfera iluminada en tiempo real."),
                _txt("Cuando mueves la luz, cambian las zonas claras, oscuras y brillantes."),
                _seccion("Idea principal"),
                _txt("Cada punto de la esfera tiene una dirección llamada normal."),
                _txt("Si la normal mira hacia la luz, esa zona se ve más iluminada."),
                _formula(r"I=I_a+I_d+I_s"),
            ])

        return _doc("Explicación", C_AZUL, [
            _txt("Selecciona un algoritmo para ver una explicación."),
        ])

    @staticmethod
    def dda(x1, y1, x2, y2, paso_actual, total_pasos):
        dx = x2 - x1
        dy = y2 - y1
        pasos = max(abs(dx), abs(dy)) if max(abs(dx), abs(dy)) != 0 else 1

        if paso_actual <= 0:
            x_inc = dx / pasos
            y_inc = dy / pasos
            return _doc("DDA · Línea paso a paso", C_AZUL, [
                _seccion("¿Qué hace?"),
                _txt("DDA dibuja una línea calculando muchos puntos pequeños entre el inicio y el final."),
                _txt("Es como dividir el camino completo en pasos iguales."),
                _seccion("Datos de la línea"),
                _txt(f"Punto inicial: ({x1:.0f}, {y1:.0f})"),
                _txt(f"Punto final: ({x2:.0f}, {y2:.0f})"),
                _formula(r"\Delta x=x_2-x_1"),
                _formula(r"\Delta y=y_2-y_1"),
                _txt(f"En este caso: Δx = {dx:.0f}, Δy = {dy:.0f}"),
                _seccion("¿Cuánto avanza en cada paso?"),
                _formula(r"pasos=\max(|\Delta x|,|\Delta y|)"),
                _txt(f"Pasos calculados: {pasos:.0f}"),
                _formula(r"x_{inc}=\frac{\Delta x}{pasos}\qquad y_{inc}=\frac{\Delta y}{pasos}"),
                _res(f"Incremento: x_inc = {x_inc:.3f}, y_inc = {y_inc:.3f}"),
            ])

        total_pasos = max(1, total_pasos)
        t = min(1, max(0, paso_actual / total_pasos))
        x_actual = x1 + dx * t
        y_actual = y1 + dy * t

        return _doc(f"DDA · Paso {paso_actual}/{total_pasos}", C_AZUL, [
            _seccion("¿Qué está pasando?"),
            _txt("El algoritmo calcula una posición intermedia dentro de la línea."),
            _txt("Esa posición puede tener decimales, pero el píxel final debe ser entero."),
            _seccion("Fórmula del punto actual"),
            _formula(r"x(t)=x_1+t\Delta x"),
            _formula(r"y(t)=y_1+t\Delta y"),
            _txt(f"Valor de avance: t = {t:.3f}"),
            _txt(f"x = {x1:.0f} + {t:.3f}·{dx:.0f} = {x_actual:.3f}"),
            _txt(f"y = {y1:.0f} + {t:.3f}·{dy:.0f} = {y_actual:.3f}"),
            _res(f"Píxel dibujado: ({round(x_actual)}, {round(y_actual)})"),
        ])

    @staticmethod
    def bresenham(x1, y1, x2, y2, paso_actual, error_actual):
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1

        if paso_actual <= 0:
            return _doc("Bresenham · Decidir el siguiente píxel", C_NARANJA, [
                _seccion("¿Qué hace?"),
                _txt("Bresenham dibuja una línea eligiendo el píxel que mejor sigue el camino ideal."),
                _txt("A diferencia de DDA, evita trabajar con muchos decimales."),
                _seccion("Datos iniciales"),
                _txt(f"Punto inicial: ({x1:.0f}, {y1:.0f})"),
                _txt(f"Punto final: ({x2:.0f}, {y2:.0f})"),
                _formula(r"\Delta x=|x_2-x_1|\qquad \Delta y=|y_2-y_1|"),
                _txt(f"Δx = {dx:.0f}, Δy = {dy:.0f}"),
                _formula(r"error=\Delta x-\Delta y"),
                _res(f"Error inicial: {dx - dy:.0f}"),
                _txt(f"Dirección de avance: sx = {sx}, sy = {sy}"),
            ])

        e2 = error_actual * 2
        mover_x = e2 > -dy
        mover_y = e2 < dx

        return _doc(f"Bresenham · Paso {paso_actual}", C_NARANJA, [
            _seccion("¿Qué está decidiendo?"),
            _txt("El algoritmo revisa el error para saber hacia dónde debe moverse el siguiente píxel."),
            _formula(r"e_2=2\cdot error"),
            _txt(f"error = {error_actual}"),
            _txt(f"e₂ = 2 · {error_actual} = {e2}"),
            _seccion("Reglas de decisión"),
            _formula(r"e_2>-\Delta y\quad \Rightarrow\quad avanzar\ en\ X"),
            _txt(f"¿{e2} > -{dy}? {'Sí' if mover_x else 'No'}"),
            _formula(r"e_2<\Delta x\quad \Rightarrow\quad avanzar\ en\ Y"),
            _txt(f"¿{e2} < {dx}? {'Sí' if mover_y else 'No'}"),
            _res(f"Decisión: {'mover X' if mover_x else 'no mover X'} y {'mover Y' if mover_y else 'no mover Y'}."),
        ])

    @staticmethod
    def bezier(puntos, paso_actual, total_pasos, t_actual=0):
        n = len(puntos) - 1

        if len(puntos) < 2:
            return _doc("Bézier · Faltan puntos", C_AZUL, [
                _alerta("Agrega al menos 2 puntos de control."),
            ])

        if paso_actual <= 0:
            return _doc("Bézier · Curva flexible", C_AZUL, [
                _seccion("¿Qué hace?"),
                _txt("Una curva de Bézier crea una línea suave controlada por puntos."),
                _txt("El primer punto es el inicio. El último punto es el final."),
                _txt("Los puntos intermedios jalan la curva, como si fueran imanes."),
                _seccion("Fórmula"),
                _formula(r"B(t)=\sum_{i=0}^{n}\binom{n}{i}(1-t)^{n-i}t^iP_i", fontsize=16),
                _txt(f"Número de puntos de control: {len(puntos)}"),
                _txt(f"Grado de la curva: n = {n}"),
                _txt("t va de 0 a 1. Conforme t avanza, aparece la curva."),
            ])

        total_pasos = max(1, total_pasos)
        t = t_actual if t_actual > 0 else paso_actual / total_pasos
        t = min(1, max(0, t))

        x = 0
        y = 0
        pesos = []

        for i, p in enumerate(puntos):
            peso = math.comb(n, i) * ((1 - t) ** (n - i)) * (t ** i)
            x += peso * p[0]
            y += peso * p[1]
            pesos.append((i, peso))

        bloques = [
            _seccion("¿Qué está pasando?"),
            _txt("Cada punto de control recibe un peso."),
            _txt("Los pesos indican qué tanto influye cada punto en la posición actual de la curva."),
            _formula(r"B(t)=w_0P_0+w_1P_1+\cdots+w_nP_n", fontsize=16),
            _txt(f"Valor actual: t = {t:.3f}"),
            _seccion("Pesos en este paso"),
        ]

        for i, peso in pesos[:8]:
            bloques.append(_txt(f"w{i} = {peso:.4f}"))
        if len(pesos) > 8:
            bloques.append(_txt("..."))

        bloques.extend([
            _res(f"Punto calculado: B({t:.3f}) = ({x:.3f}, {y:.3f})"),
            _res(f"Píxel dibujado: ({round(x)}, {round(y)})"),
        ])

        return _doc(f"Bézier · Paso {paso_actual}/{total_pasos}", C_AZUL, bloques)

    @staticmethod
    def bspline(puntos, paso_actual, total_pasos, t_actual=0):
        if len(puntos) < 4:
            return _doc("B-Spline · Faltan puntos", C_MORADO, [
                _alerta(f"Tienes {len(puntos)} punto(s). Necesitas al menos 4."),
                _txt("Una B-Spline cúbica trabaja por tramos de 4 puntos cercanos."),
            ])

        if paso_actual <= 0:
            return _doc("B-Spline · Curva por tramos", C_MORADO, [
                _seccion("¿Qué hace?"),
                _txt("Crea una curva suave formada por varios tramos."),
                _txt("Cada tramo usa 4 puntos cercanos, por eso mover un punto solo afecta una zona de la curva."),
                _seccion("Fórmula matricial"),
                _formula(r"Q(t)=[t^3\ t^2\ t\ 1]\cdot rac{1}{6}\cdot M\cdot P", fontsize=16),
                _matriz("M", [["-1", "3", "-3", "1"], ["3", "-6", "3", "0"], ["-3", "0", "3", "0"], ["1", "4", "1", "0"]]),
                _txt(f"Puntos de control: {len(puntos)}"),
                _txt(f"Tramos generados: {len(puntos) - 3}"),
            ])

        total_pasos = max(1, total_pasos)
        t = t_actual if t_actual > 0 else paso_actual / total_pasos
        t = min(1, max(0, t))
        segmento = min(max(0, paso_actual // 50), len(puntos) - 4)

        return _doc(f"B-Spline · Paso {paso_actual}/{total_pasos}", C_MORADO, [
            _seccion("¿Qué tramo se está calculando?"),
            _txt(f"Segmento aproximado: {segmento + 1} de {len(puntos) - 3}"),
            _txt("Este tramo depende principalmente de estos 4 puntos cercanos:"),
            _txt(f"P0 = {puntos[segmento]}"),
            _txt(f"P1 = {puntos[segmento + 1]}"),
            _txt(f"P2 = {puntos[segmento + 2]}"),
            _txt(f"P3 = {puntos[segmento + 3]}"),
            _seccion("Vector de avance"),
            _formula(r"[t^3\quad t^2\quad t\quad 1]"),
            _txt(f"t = {t:.3f}"),
            _txt(f"[t³, t², t, 1] = [{t**3:.3f}, {t**2:.3f}, {t:.3f}, 1]"),
        ])

    @staticmethod
    def traslacion(puntos, tx, ty, paso_actual, total_pasos):
        if not puntos:
            return _doc("Traslación · Sin puntos", C_VERDE, [
                _alerta("Primero coloca puntos en el lienzo."),
            ])

        if paso_actual <= 0:
            return _doc("Traslación · Mover una figura", C_VERDE, [
                _seccion("¿Qué hace?"),
                _txt("Trasladar significa mover una figura completa sin cambiar su forma."),
                _txt("Todos los puntos se desplazan la misma cantidad."),
                _seccion("Matriz de traslación"),
                _matriz("T", [["1", "0", "tx"], ["0", "1", "ty"], ["0", "0", "1"]]),
                _txt(f"tx = {tx:.0f}: movimiento horizontal."),
                _txt(f"ty = {ty:.0f}: movimiento vertical."),
                _formula(r"x'=x+t_x\qquad y'=y+t_y"),
                _res(f"Se moverán {len(puntos)} punto(s)."),
            ])

        idx = min(max(0, paso_actual - 1), len(puntos) - 1)
        x, y = puntos[idx]
        return _doc(f"Traslación · Punto {idx + 1}/{len(puntos)}", C_VERDE, [
            _seccion("Punto original"),
            _txt(f"P = ({x:.0f}, {y:.0f})"),
            _seccion("Aplicando el movimiento"),
            _formula(r"x'=x+t_x"),
            _formula(r"y'=y+t_y"),
            _txt(f"x' = {x:.0f} + {tx:.0f} = {x + tx:.0f}"),
            _txt(f"y' = {y:.0f} + {ty:.0f} = {y + ty:.0f}"),
            _res(f"Nuevo punto: ({x + tx:.0f}, {y + ty:.0f})"),
        ])

    @staticmethod
    def rotacion(puntos, theta, paso_actual, total_pasos):
        if not puntos:
            return _doc("Rotación · Sin puntos", C_MORADO, [
                _alerta("Primero coloca puntos en el lienzo."),
            ])

        theta_rad = np.radians(theta)
        cos_t = np.cos(theta_rad)
        sin_t = np.sin(theta_rad)

        if paso_actual <= 0:
            return _doc("Rotación · Girar una figura", C_MORADO, [
                _seccion("¿Qué hace?"),
                _txt("Rotar significa girar una figura alrededor de un punto central."),
                _txt("La forma no cambia; solo cambia su orientación."),
                _seccion("Matriz de rotación"),
                _matriz("R", [["cosθ", "-sinθ", "0"], ["sinθ", "cosθ", "0"], ["0", "0", "1"]]),
                _txt(f"Ángulo: θ = {theta:.2f}°"),
                _txt(f"En radianes: {theta_rad:.3f}"),
                _txt(f"cos(θ) = {cos_t:.4f}, sin(θ) = {sin_t:.4f}"),
            ])

        idx = min(max(0, paso_actual - 1), len(puntos) - 1)
        x, y = puntos[idx]
        x_new = x * cos_t - y * sin_t
        y_new = x * sin_t + y * cos_t

        return _doc(f"Rotación · Punto {idx + 1}/{len(puntos)}", C_MORADO, [
            _seccion("Punto original"),
            _txt(f"P = ({x:.0f}, {y:.0f})"),
            _seccion("Fórmulas"),
            _formula(r"x'=x\cos\theta-y\sin\theta"),
            _formula(r"y'=x\sin\theta+y\cos\theta"),
            _txt(f"x' = {x:.0f}·{cos_t:.3f} - {y:.0f}·{sin_t:.3f} = {x_new:.3f}"),
            _txt(f"y' = {x:.0f}·{sin_t:.3f} + {y:.0f}·{cos_t:.3f} = {y_new:.3f}"),
            _res(f"Nuevo punto: ({x_new:.3f}, {y_new:.3f})"),
        ])

    @staticmethod
    def esfera_3d(angulo_x, angulo_y):
        return _doc("Esfera 3D · Malla paramétrica", C_AZUL, [
            _seccion("¿Qué hace?"),
            _txt("Construye una esfera usando muchos puntos organizados como una red."),
            _txt("Después esos puntos se conectan para formar pequeños polígonos."),
            _seccion("Idea visual"),
            _txt("Es parecido a envolver una pelota con una cuadrícula de líneas horizontales y verticales."),
            _seccion("Ecuaciones de la esfera"),
            _formula(r"x=R\cos(u)\sin(v)"),
            _formula(r"y=R\sin(u)\sin(v)"),
            _formula(r"z=R\cos(v)"),
            _txt("u y v funcionan como ángulos que recorren toda la superficie."),
            _seccion("Rotación actual"),
            _txt(f"Ángulo X: {angulo_x:.1f}°"),
            _txt(f"Ángulo Y: {angulo_y:.1f}°"),
        ])

    @staticmethod
    def cubo_3d(angulo_x, angulo_y, distancia_vista):
        return _doc("Cubo 3D · Rotación y perspectiva", C_NARANJA, [
            _seccion("¿Qué hace?"),
            _txt("Muestra un cubo en 3D usando vértices, aristas y caras."),
            _txt("Cada vértice se rota y luego se proyecta a la pantalla 2D."),
            _seccion("Idea principal"),
            _txt("Aunque la pantalla es plana, usamos fórmulas para simular profundidad."),
            _seccion("Rotación"),
            _formula(r"P_{rotado}=R_y\cdot R_x\cdot P"),
            _txt(f"Ángulo X: {angulo_x:.3f} rad"),
            _txt(f"Ángulo Y: {angulo_y:.3f} rad"),
            _seccion("Perspectiva"),
            _formula(r"x_{2D}=\frac{x}{w}\qquad y_{2D}=\frac{y}{w}"),
            _txt(f"Distancia de vista: {distancia_vista:.2f}"),
        ])

    @staticmethod
    def explicacion(esfera):
        try:
            luz = esfera.luz_pos
            ka = esfera.ka
            kd = esfera.kd
            ks = esfera.ks
            brillo = esfera.brillo_n
        except Exception:
            return ExplicadorAlgoritmos.intro("Esfera 3D Interactiva")

        return _doc("Esfera interactiva · Iluminación", C_AZUL, [
            _seccion("¿Qué hace?"),
            _txt("Calcula cómo se ilumina cada punto visible de una esfera."),
            _txt("Si una zona mira hacia la luz, se ve clara. Si mira en dirección contraria, se ve oscura."),
            _seccion("Tres partes de la luz"),
            _txt("1. Ambiental: luz mínima que llega a toda la esfera."),
            _txt("2. Difusa: depende de qué tan de frente llega la luz."),
            _txt("3. Especular: produce el brillo fuerte o reflejo."),
            _formula(r"I= k_a + k_d\max(N\cdot L,0)+k_s\max(R\cdot V,0)^n", fontsize=15),
            _seccion("¿Qué significan las letras?"),
            _txt("N es la normal: hacia dónde mira la superficie."),
            _txt("L es la dirección hacia la luz."),
            _txt("V es la dirección hacia la cámara."),
            _txt("R es la dirección del reflejo."),
            _seccion("Valores actuales"),
            _txt(f"Posición de la luz: ({luz[0]:.2f}, {luz[1]:.2f}, {luz[2]:.2f})"),
            _txt(f"ka = {ka:.2f}, kd = {kd:.2f}, ks = {ks:.2f}"),
            _txt(f"Brillo especular n = {brillo}"),
        ])

    