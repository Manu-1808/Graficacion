import math
import numpy as np


# Colores reutilizados en todas las explicaciones (consistencia visual)
C_ENCABEZADO = (255, 200, 100)
C_FORMULA = (255, 255, 150)
C_TEXTO = (200, 200, 200)
C_DATO = (150, 255, 150)
C_RESULTADO = (255, 255, 150)
C_ALERTA = (255, 150, 150)


def _bloque(titulo, color, secciones):
    """Arma el dict estándar {titulo, color, lineas} a partir de secciones.

    secciones: lista de tuplas (encabezado, [items]) donde cada item es
    'texto' (usa color por defecto C_TEXTO) o ('texto', color).
    """
    lineas = [{'texto': '─' * 39, 'color': C_ENCABEZADO}]

    for i, (encabezado, items) in enumerate(secciones):
        if encabezado:
            lineas.append({'texto': f'▸ {encabezado}', 'color': C_ENCABEZADO})
        for it in items:
            if isinstance(it, tuple):
                texto, color_linea = it
            else:
                texto, color_linea = it, C_TEXTO
            lineas.append({'texto': f'  {texto}' if texto else '', 'color': color_linea})
        if i < len(secciones) - 1:
            lineas.append({'texto': '', 'color': C_TEXTO})

    return {'titulo': titulo, 'color': color, 'lineas': lineas}


class ExplicadorAlgoritmos:
    """Genera explicaciones matemáticas paso a paso, en español, con un
    formato consistente: ¿QUÉ HACE? → FÓRMULA → CÁLCULO ACTUAL → RESULTADO.
    """

    # ------------------------------------------------------------------
    # DDA
    # ------------------------------------------------------------------
    @staticmethod
    def dda(x1, y1, x2, y2, paso_actual, total_pasos):
        dx, dy = x2 - x1, y2 - y1

        if paso_actual <= 0:
            m = dy / dx if dx != 0 else float('inf')
            pasos = max(abs(dx), abs(dy))

            return _bloque(
                '▸ DDA · Diferencias Digitales', (100, 200, 255),
                [
                    ("¿QUÉ HACE?", [
                        "Traza una línea recta calculando puntos",
                        "intermedios con incrementos constantes.",
                    ]),
                    ("FÓRMULA DE LA RECTA", [
                        ("y = m·x + b", C_FORMULA),
                        f"m = Δy/Δx = {dy:.1f}/{dx:.1f} = {m:.3f}",
                    ]),
                    ("PARÁMETROS", [
                        f"P₁ = ({x1:.0f}, {y1:.0f})    P₂ = ({x2:.0f}, {y2:.0f})",
                        f"Δx = {dx:.0f}   Δy = {dy:.0f}",
                    ]),
                    ("PASOS DEL ALGORITMO", [
                        ("pasos = max(|Δx|, |Δy|)", C_DATO),
                        f"pasos = max({abs(dx):.0f}, {abs(dy):.0f}) = {pasos:.0f}",
                        ("x_inc = Δx/pasos,  y_inc = Δy/pasos", C_DATO),
                        f"x_inc = {dx/pasos:.3f}   y_inc = {dy/pasos:.3f}",
                    ]),
                ]
            )

        t = paso_actual / total_pasos
        x_actual, y_actual = x1 + dx * t, y1 + dy * t

        return _bloque(
            f'▸ DDA · Iteración {paso_actual}/{total_pasos}', (100, 200, 255),
            [
                ("ECUACIÓN PARAMÉTRICA", [
                    ("x(t) = x₁ + t·Δx        y(t) = y₁ + t·Δy", C_FORMULA),
                    f"t = {t:.3f}",
                ]),
                ("CÁLCULO EN ESTE PASO", [
                    f"x({t:.3f}) = {x1:.0f} + {t:.3f}·{dx:.0f} = {x_actual:.3f}",
                    f"y({t:.3f}) = {y1:.0f} + {t:.3f}·{dy:.0f} = {y_actual:.3f}",
                ]),
                ("RESULTADO", [
                    (f"Posición real: ({x_actual:.3f}, {y_actual:.3f})", C_TEXTO),
                    (f"Píxel dibujado: ({round(x_actual)}, {round(y_actual)})", C_RESULTADO),
                    f"Progreso: {paso_actual*100//total_pasos}%",
                ]),
            ]
        )

    # ------------------------------------------------------------------
    # Bresenham
    # ------------------------------------------------------------------
    @staticmethod
    def bresenham(x1, y1, x2, y2, paso_actual, error_actual):
        dx, dy = abs(x2 - x1), abs(y2 - y1)

        if paso_actual <= 0:
            sx = 1 if x1 < x2 else -1
            sy = 1 if y1 < y2 else -1

            return _bloque(
                '▸ Bresenham · Aritmética Entera', (255, 150, 100),
                [
                    ("¿QUÉ HACE?", [
                        "Traza la misma recta que DDA, pero usando",
                        "solo sumas y restas de enteros: es más rápido",
                        "porque evita divisiones y decimales.",
                    ]),
                    ("PARÁMETROS", [
                        f"Δx = |x₂−x₁| = {dx}    Δy = |y₂−y₁| = {dy}",
                        f"s_x = {sx}    s_y = {sy}   (dirección de avance)",
                    ]),
                    ("ERROR INICIAL", [
                        (f"error = Δx − Δy = {dx} − {dy} = {dx - dy}", C_FORMULA),
                    ]),
                    ("REGLA DE DECISIÓN EN CADA PASO", [
                        ("e₂ = 2·error", C_DATO),
                        ("si e₂ > −Δy  →  avanza en X", C_DATO),
                        ("si e₂ <  Δx  →  avanza en Y", C_DATO),
                    ]),
                ]
            )

        e2 = error_actual * 2
        mover_x = e2 > -dy
        mover_y = e2 < dx

        return _bloque(
            f'▸ Bresenham · Paso {paso_actual}', (255, 150, 100),
            [
                ("VALORES ACTUALES", [
                    f"error = {error_actual}    e₂ = 2·({error_actual}) = {e2}",
                ]),
                ("COMPARACIONES", [
                    (f"e₂ > −{dy}  →  {'✓ verdadero' if mover_x else '✗ falso'}",
                     C_DATO if mover_x else C_ALERTA),
                    (f"e₂ <  {dx}  →  {'✓ verdadero' if mover_y else '✗ falso'}",
                     C_DATO if mover_y else C_ALERTA),
                ]),
                ("DECISIÓN", [
                    "Mover en X" if mover_x else "No mover en X",
                    "Mover en Y" if mover_y else "No mover en Y",
                ]),
            ]
        )

    # ------------------------------------------------------------------
    # Bézier
    # ------------------------------------------------------------------
    @staticmethod
    def bezier(puntos, paso_actual, total_pasos, t_actual=0):
        n = len(puntos) - 1

        if paso_actual <= 0:
            coefs = [math.comb(n, i) for i in range(n + 1)]

            return _bloque(
                '▸ Bézier · Polinomios de Bernstein', (150, 200, 255),
                [
                    ("¿QUÉ HACE?", [
                        "Genera una curva suave que pasa por el primer",
                        "y último punto, atraída por los intermedios",
                        "sin pasar exactamente por ellos.",
                    ]),
                    ("FÓRMULA GENERAL", [
                        ("B(t) = Σ C(n,i)·(1−t)ⁿ⁻ⁱ·tⁱ·Pᵢ", C_FORMULA),
                        f"n = {n}  (puntos de control: {n + 1})",
                        "t recorre 0 → 1 (inicio → fin de la curva)",
                    ]),
                    ("COEFICIENTES BINOMIALES C(n,i)", [
                        f"{coefs}",
                    ]),
                ]
            )

        t = t_actual if t_actual > 0 else paso_actual / total_pasos
        x = y = 0
        terminos = []
        for i, p in enumerate(puntos):
            coef = math.comb(n, i) * ((1 - t) ** (n - i)) * (t ** i)
            x += coef * p[0]
            y += coef * p[1]
            terminos.append((i, coef, p))

        return _bloque(
            f'▸ Bézier · Iteración {paso_actual}/{total_pasos}', (150, 200, 255),
            [
                (f"t = {t:.3f}", []),
                ("PESO DE CADA PUNTO", [
                    ("B(t) = Σ wᵢ·Pᵢ", C_FORMULA),
                ] + [
                    f"w{i} = {coef:.3f} · P{i} = ({coef*p[0]:.1f}, {coef*p[1]:.1f})"
                    for i, coef, p in terminos
                ]),
                ("RESULTADO", [
                    (f"B({t:.3f}) = ({x:.3f}, {y:.3f})", C_RESULTADO),
                    f"Píxel: ({round(x)}, {round(y)})",
                ]),
            ]
        )

    # ------------------------------------------------------------------
    # B-Spline
    # ------------------------------------------------------------------
    @staticmethod
    def bspline(puntos, paso_actual, total_pasos, t_actual=0):
        if len(puntos) < 4:
            return _bloque(
                '▸ B-Spline · Faltan puntos', (255, 100, 100),
                [
                    ("REQUISITOS", [
                        (f"Puntos actuales: {len(puntos)}/4 necesarios", C_ALERTA),
                        "Se necesitan al menos 4 puntos de control.",
                    ]),
                ]
            )

        if paso_actual <= 0:
            return _bloque(
                '▸ B-Spline · Control Local', (200, 150, 255),
                [
                    ("¿QUÉ HACE?", [
                        "Como Bézier, pero cada tramo de la curva solo",
                        "depende de 4 puntos cercanos: mover un punto",
                        "no afecta a toda la curva, solo a su zona.",
                    ]),
                    ("MATRIZ B-SPLINE CÚBICA (M)", [
                        ("Q(t) = [t³ t² t 1] · (1/6)·M · [P₀ P₁ P₂ P₃]ᵀ", C_FORMULA),
                        ("┌ −1   3  −3   1 ┐", C_TEXTO),
                        ("│  3  −6   3   0 │", C_TEXTO),
                        ("│ −3   0   3   0 │", C_TEXTO),
                        ("└  1   4   1   0 ┘", C_TEXTO),
                    ]),
                    ("SEGMENTOS", [
                        f"Total de puntos de control: {len(puntos)}",
                        f"Curva dividida en {len(puntos) - 3} segmento(s)",
                    ]),
                ]
            )

        t = t_actual if t_actual > 0 else paso_actual / total_pasos
        segmento = min(paso_actual // 4, len(puntos) - 4)

        return _bloque(
            f'▸ B-Spline · Iteración {paso_actual}/{total_pasos}', (200, 150, 255),
            [
                (f"SEGMENTO {segmento + 1} DE {len(puntos) - 3}", [
                    f"t = {t:.3f}",
                ]),
                ("VECTOR DE POTENCIAS", [
                    (f"[t³, t², t, 1] = [{t**3:.3f}, {t**2:.3f}, {t:.3f}, 1]", C_FORMULA),
                ]),
                ("PUNTOS QUE INFLUYEN EN ESTE TRAMO", [
                    f"P₀ = {puntos[segmento]}",
                    f"P₁ = {puntos[segmento + 1]}",
                    f"P₂ = {puntos[segmento + 2]}",
                    f"P₃ = {puntos[segmento + 3]}",
                ]),
            ]
        )

    # ------------------------------------------------------------------
    # Traslación
    # ------------------------------------------------------------------
    @staticmethod
    def traslacion(puntos, tx, ty, paso_actual, total_pasos):
        if paso_actual <= 0:
            return _bloque(
                '▸ Traslación · Matriz Homogénea 3×3', (100, 255, 200),
                [
                    ("¿QUÉ HACE?", [
                        "Desplaza todos los puntos la misma distancia",
                        "en X y en Y, sin rotarlos ni cambiar su forma.",
                    ]),
                    ("MATRIZ DE TRASLACIÓN", [
                        ("┌ 1  0  tx ┐", C_FORMULA),
                        ("│ 0  1  ty │", C_FORMULA),
                        ("└ 0  0  1  ┘", C_FORMULA),
                        f"tx = {tx:.0f}    ty = {ty:.0f}",
                    ]),
                    ("ECUACIONES EQUIVALENTES", [
                        (f"x' = x + {tx:.0f}", C_RESULTADO),
                        (f"y' = y + {ty:.0f}", C_RESULTADO),
                        f"Puntos a mover: {len(puntos)}",
                    ]),
                ]
            )

        idx = min(paso_actual - 1, len(puntos) - 1)
        punto = puntos[idx]

        return _bloque(
            f'▸ Traslación · Punto {idx + 1}/{len(puntos)}', (100, 255, 200),
            [
                ("PUNTO ORIGINAL", [
                    f"P = ({punto[0]:.0f}, {punto[1]:.0f})",
                ]),
                ("APLICANDO LA TRASLACIÓN", [
                    (f"x' = {punto[0]:.0f} + {tx:.0f} = {punto[0] + tx:.0f}", C_FORMULA),
                    (f"y' = {punto[1]:.0f} + {ty:.0f} = {punto[1] + ty:.0f}", C_FORMULA),
                ]),
                ("NUEVA POSICIÓN", [
                    (f"P' = ({punto[0] + tx:.0f}, {punto[1] + ty:.0f})", C_RESULTADO),
                ]),
            ]
        )

    # ------------------------------------------------------------------
    # Rotación
    # ------------------------------------------------------------------
    @staticmethod
    def rotacion(puntos, theta, paso_actual, total_pasos):
        theta_rad = np.radians(theta)
        cos_t, sin_t = np.cos(theta_rad), np.sin(theta_rad)

        if paso_actual <= 0:
            return _bloque(
                '▸ Rotación · Matriz de Rotación 3×3', (200, 200, 255),
                [
                    ("¿QUÉ HACE?", [
                        "Gira todos los puntos alrededor del origen",
                        "un ángulo θ, manteniendo su distancia al centro.",
                    ]),
                    ("MATRIZ DE ROTACIÓN", [
                        ("┌ cosθ  −senθ  0 ┐", C_FORMULA),
                        ("│ senθ   cosθ  0 │", C_FORMULA),
                        ("└  0      0    1 ┘", C_FORMULA),
                        f"θ = {theta}° = {theta_rad:.3f} rad",
                        f"cosθ = {cos_t:.4f}    senθ = {sin_t:.4f}",
                    ]),
                    ("ECUACIONES EQUIVALENTES", [
                        (f"x' = x·cosθ − y·senθ", C_RESULTADO),
                        (f"y' = x·senθ + y·cosθ", C_RESULTADO),
                    ]),
                ]
            )

        idx = min(paso_actual - 1, len(puntos) - 1)
        punto = puntos[idx]
        x_new = punto[0] * cos_t - punto[1] * sin_t
        y_new = punto[0] * sin_t + punto[1] * cos_t

        return _bloque(
            f'▸ Rotación · Punto {idx + 1}/{len(puntos)}', (200, 200, 255),
            [
                ("PUNTO ORIGINAL", [
                    f"P = ({punto[0]:.0f}, {punto[1]:.0f})",
                ]),
                ("APLICANDO LA ROTACIÓN", [
                    (f"x' = {punto[0]:.0f}·{cos_t:.3f} − {punto[1]:.0f}·{sin_t:.3f} = {x_new:.3f}", C_FORMULA),
                    (f"y' = {punto[0]:.0f}·{sin_t:.3f} + {punto[1]:.0f}·{cos_t:.3f} = {y_new:.3f}", C_FORMULA),
                ]),
                ("NUEVA POSICIÓN", [
                    (f"P' = ({x_new:.3f}, {y_new:.3f})", C_RESULTADO),
                ]),
            ]
        )

    # ------------------------------------------------------------------
    # Esfera 3D
    # ------------------------------------------------------------------
    @staticmethod
    def esfera_3d(angulo_x, angulo_y):
        return _bloque(
            '▸ Esfera 3D · Ecuaciones Paramétricas', (150, 220, 255),
            [
                ("¿QUÉ HACE?", [
                    "Genera una malla de puntos sobre la superficie",
                    "de una esfera usando latitud y longitud, luego",
                    "la rota y proyecta a la pantalla en 2D.",
                ]),
                ("ECUACIONES DE LA SUPERFICIE", [
                    ("x = R·cos(u)·cos(v)", C_FORMULA),
                    ("y = R·cos(u)·sen(v)", C_FORMULA),
                    ("z = R·sen(u)", C_FORMULA),
                    "u ∈ [−π/2, π/2] (latitud)   v ∈ [0, 2π] (longitud)",
                    "R = radio de la esfera",
                ]),
                ("ROTACIÓN ACTUAL", [
                    f"θx = {angulo_x:.1f}°    θy = {angulo_y:.1f}°",
                    ("R = R_x(θx) · R_y(θy)", C_DATO),
                ]),
                ("PROYECCIÓN EN PERSPECTIVA", [
                    ("x_proy = x /(z + d)      y_proy = y /(z + d)", C_FORMULA),
                    "d = distancia del observador a la escena",
                ]),
            ]
        )

    # ------------------------------------------------------------------
    # Cubo 3D
    # ------------------------------------------------------------------
    @staticmethod
    def cubo_3d(angulo_x, angulo_y, distancia_vista):
        return _bloque(
            '▸ Cubo 3D · Render con Matrices', (255, 200, 100),
            [
                ("¿QUÉ HACE?", [
                    "Rota los 8 vértices del cubo con matrices 4×4,",
                    "los proyecta a 2D y ordena las caras de atrás",
                    "hacia adelante para dibujarlas correctamente.",
                ]),
                ("ROTACIÓN COMBINADA", [
                    ("R = R_x(θx) · R_y(θy)", C_FORMULA),
                    ("┌ 1    0       0    ┐   ┌ cosθy  0  senθy ┐", C_TEXTO),
                    ("│ 0   cosθx  −senθx │ · │   0    1    0   │", C_TEXTO),
                    ("│ 0   senθx   cosθx │   │−senθy  0  cosθy │", C_TEXTO),
                    ("└                   ┘   └                ┘", C_TEXTO),
                ]),
                ("PROYECCIÓN EN PERSPECTIVA", [
                    ("x_proy = x_rot·d /(z_rot + d)", C_FORMULA),
                    ("y_proy = y_rot·d /(z_rot + d)", C_FORMULA),
                    f"d = {distancia_vista:.1f}  (distancia de vista)",
                ]),
                ("ORDEN DE DIBUJO (pintor)", [
                    ("centro_cara = (1/4)·Σ Vᵢ", C_DATO),
                    "1. calcular profundidad promedio de cada cara",
                    "2. ordenar de más lejana a más cercana",
                    "3. dibujar en ese orden con transparencia",
                ]),
            ]
        )

    @staticmethod
    def explicacion(esfera):
        """Genera la explicación de la esfera interactiva."""
        luz_x, luz_y, luz_z = esfera.luz_pos
        
        return {
            'titulo': '▸ Esfera 3D Interactiva · Iluminación en Tiempo Real',
            'color': (100, 220, 255),
            'lineas': [
                {'texto': '─' * 39, 'color': (255, 200, 100)},
                {'texto': '▸ ¿QUÉ HACE?', 'color': (255, 200, 100)},
                {'texto': '  Renderiza una esfera con iluminación dinámica', 'color': (200, 200, 200)},
                {'texto': '  que sigue el movimiento del mouse en tiempo real.', 'color': (200, 200, 200)},
                {'texto': '  La sombra se proyecta en el suelo automáticamente.', 'color': (200, 200, 200)},
                {'texto': '', 'color': (200, 200, 200)},
                {'texto': '▸ MODELO DE ILUMINACIÓN', 'color': (255, 200, 100)},
                {'texto': '  I = Iₐ + I_d + Iₛ', 'color': (255, 255, 150)},
                {'texto': '', 'color': (200, 200, 200)},
                {'texto': '  Componente Ambiental (Iₐ):', 'color': (200, 200, 200)},
                {'texto': f'    kₐ = {esfera.ka:.2f}', 'color': (150, 255, 150)},
                {'texto': '    Iluminación base constante', 'color': (200, 200, 200)},
                {'texto': '', 'color': (200, 200, 200)},
                {'texto': '  Componente Difusa (I_d):', 'color': (200, 200, 200)},
                {'texto': '    I_d = k_d · max(0, N·L)', 'color': (255, 255, 150)},
                {'texto': f'    k_d = {esfera.kd:.2f}', 'color': (150, 255, 150)},
                {'texto': '    Depende del ángulo entre la normal', 'color': (200, 200, 200)},
                {'texto': '    y la dirección de la luz.', 'color': (200, 200, 200)},
                {'texto': '', 'color': (200, 200, 200)},
                {'texto': '  Componente Especular (Iₛ):', 'color': (200, 200, 200)},
                {'texto': '    Iₛ = kₛ · (R·V)^n', 'color': (255, 255, 150)},
                {'texto': f'    kₛ = {esfera.ks:.2f}', 'color': (150, 255, 150)},
                {'texto': f'    Brillo = {esfera.brillo_n}', 'color': (150, 255, 150)},
                {'texto': '    Crea el brillo especular en la superficie', 'color': (200, 200, 200)},
                {'texto': '', 'color': (200, 200, 200)},
                {'texto': '▸ POSICIÓN DE LA LUZ', 'color': (255, 200, 100)},
                {'texto': f'  Luz en: ({luz_x:.2f}, {luz_y:.2f}, {luz_z:.2f})', 'color': (255, 255, 150)},
                {'texto': '  Mueve el mouse para cambiar la posición', 'color': (200, 200, 200)},
                {'texto': '  de la fuente de luz en tiempo real.', 'color': (200, 200, 200)},
                {'texto': '', 'color': (200, 200, 200)},
                {'texto': '▸ ATENUACIÓN', 'color': (255, 200, 100)},
                {'texto': '  I = I₀ / (1 + α·d²)', 'color': (255, 255, 150)},
                {'texto': '  La luz se atenúa con la distancia', 'color': (200, 200, 200)},
                {'texto': '  para un efecto más realista.', 'color': (200, 200, 200)},
                {'texto': '', 'color': (200, 200, 200)},
                {'texto': '▸ SOMBRA EN EL SUELO', 'color': (255, 200, 100)},
                {'texto': '  La sombra se calcula por ray casting', 'color': (200, 200, 200)},
                {'texto': '  y se proyecta en el plano del suelo.', 'color': (200, 200, 200)},
                {'texto': '  Presiona [S] para activar/desactivar.', 'color': (150, 255, 150)},
                {'texto': '', 'color': (200, 200, 200)},
                {'texto': '▸ ROTACIÓN', 'color': (255, 200, 100)},
                {'texto': '  Arrastra con el mouse para rotar', 'color': (200, 200, 200)},
                {'texto': '  la esfera y ver la luz desde otro ángulo.', 'color': (200, 200, 200)},
            ]
        }