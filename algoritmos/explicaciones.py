class ExplicadorAlgoritmos:
    """Explicaciones para público general - sin tecnicismos"""

    @staticmethod
    def dda(x1, y1, x2, y2, paso_actual, total_pasos):
        """Explicación amigable del algoritmo DDA"""

        if paso_actual <= 0:
            dx = x2 - x1
            dy = y2 - y1
            pasos = max(abs(dx), abs(dy))

            return {
                'titulo': 'DDA - Dibujando una línea recta',
                'color': (100, 200, 255),
                'lineas': [
                    {'texto': 'Imagina que quieres dibujar una línea', 'color': (220, 220, 220)},
                    {'texto': 'del punto A al punto B en una cuadrícula.', 'color': (220, 220, 220)},
                    {'texto': '', 'color': (220, 220, 220)},
                    {'texto': 'Datos de tu línea:', 'color': (255, 200, 100)},
                    {'texto': f'  • Punto de inicio: ({x1:.0f}, {y1:.0f})', 'color': (200, 200, 200)},
                    {'texto': f'  • Punto final: ({x2:.0f}, {y2:.0f})', 'color': (200, 200, 200)},
                    {'texto': f'  • Distancia horizontal: {dx:.0f} pasos', 'color': (200, 200, 200)},
                    {'texto': f'  • Distancia vertical: {dy:.0f} pasos', 'color': (200, 200, 200)},
                    {'texto': '', 'color': (220, 220, 220)},
                    {'texto': 'El algoritmo calculará paso a paso', 'color': (150, 255, 150)},
                    {'texto': 'cómo llegar del inicio al final.', 'color': (150, 255, 150)},
                ]
            }
        else:
            t = paso_actual / total_pasos if total_pasos > 0 else 0
            x_actual = x1 + (x2 - x1) * t
            y_actual = y1 + (y2 - y1) * t

            return {
                'titulo': f'DDA - Paso {paso_actual} de {total_pasos}',
                'color': (100, 200, 255),
                'lineas': [
                    {'texto': '¿Dónde estamos ahora?', 'color': (220, 220, 220)},
                    {'texto': f'  • Avance: {paso_actual}/{total_pasos} del camino', 'color': (255, 200, 100)},
                    {'texto': f'  • Posición actual: ({x_actual:.1f}, {y_actual:.1f})', 'color': (200, 200, 200)},
                    {'texto': '', 'color': (220, 220, 220)},
                    {'texto': 'En cada paso, el algoritmo avanza', 'color': (220, 220, 220)},
                    {'texto': 'un poco en horizontal y vertical', 'color': (220, 220, 220)},
                    {'texto': 'hasta llegar al destino.', 'color': (220, 220, 220)},
                    {'texto': '', 'color': (220, 220, 220)},
                    {'texto': f'→ Pintamos el píxel ({round(x_actual)}, {round(y_actual)})', 'color': (255, 255, 150)},
                ]
            }

    @staticmethod
    def bresenham(x1, y1, x2, y2, paso_actual, error_actual):
        """Explicación amigable del algoritmo de Bresenham"""

        if paso_actual <= 0:
            dx = abs(x2 - x1)
            dy = abs(y2 - y1)

            return {
                'titulo': 'Bresenham - Una línea más inteligente',
                'color': (255, 150, 100),
                'lineas': [
                    {'texto': 'Este algoritmo es más eficiente porque', 'color': (220, 220, 220)},
                    {'texto': 'solo usa números enteros para decidir', 'color': (220, 220, 220)},
                    {'texto': 'qué píxeles debe iluminar.', 'color': (220, 220, 220)},
                    {'texto': '', 'color': (220, 220, 220)},
                    {'texto': 'Datos de la línea:', 'color': (255, 200, 100)},
                    {'texto': f'  • Avanza {dx} pasos en horizontal', 'color': (200, 200, 200)},
                    {'texto': f'  • Avanza {dy} pasos en vertical', 'color': (200, 200, 200)},
                    {'texto': f'  • Inclinación: {dy / dx:.2f}', 'color': (200, 200, 200)},
                    {'texto': '', 'color': (220, 220, 220)},
                    {'texto': 'El algoritmo va decidiendo en cada paso', 'color': (150, 255, 150)},
                    {'texto': 'si debe subir, bajar o seguir recto.', 'color': (150, 255, 150)},
                ]
            }
        else:
            decision = "subir" if error_actual < 0 else "seguir recto"
            return {
                'titulo': f'Bresenham - Paso {paso_actual}',
                'color': (255, 150, 100),
                'lineas': [
                    {'texto': 'El algoritmo evalúa:', 'color': (220, 220, 220)},
                    {'texto': f'  • Error actual = {error_actual}', 'color': (255, 200, 100)},
                    {'texto': '', 'color': (220, 220, 220)},
                    {'texto': 'Esto le dice que debe:', 'color': (220, 220, 220)},
                    {'texto': f'  → {decision}', 'color': (150, 255, 150)},
                    {'texto': '', 'color': (220, 220, 220)},
                    {'texto': 'Es como si tuviera un indicador', 'color': (200, 200, 200)},
                    {'texto': 'que le dice si está muy arriba', 'color': (200, 200, 200)},
                    {'texto': 'o muy abajo de la línea ideal.', 'color': (200, 200, 200)},
                ]
            }

    @staticmethod
    def bezier(puntos, paso_actual, total_pasos, t_actual=0):
        """Explicación amigable de la curva de Bézier"""

        n = len(puntos) - 1

        if paso_actual <= 0:
            return {
                'titulo': 'Bézier - Curvas suaves y elegantes',
                'color': (150, 200, 255),
                'lineas': [
                    {'texto': 'Esta curva se crea usando puntos de control', 'color': (220, 220, 220)},
                    {'texto': 'que funcionan como "imanes" que atraen', 'color': (220, 220, 220)},
                    {'texto': 'la curva hacia ellos.', 'color': (220, 220, 220)},
                    {'texto': '', 'color': (220, 220, 220)},
                    {'texto': f'  • Puntos de control: {len(puntos)}', 'color': (255, 200, 100)},
                    {'texto': f'  • Grado de la curva: {n}', 'color': (255, 200, 100)},
                    {'texto': '', 'color': (220, 220, 220)},
                    {'texto': 'La curva comenzará en el primer punto', 'color': (150, 255, 150)},
                    {'texto': 'y terminará en el último, pasando', 'color': (150, 255, 150)},
                    {'texto': 'cerca de los puntos intermedios.', 'color': (150, 255, 150)},
                ]
            }
        else:
            t = t_actual if t_actual > 0 else paso_actual / total_pasos

            # Calcular punto actual
            x = 0
            y = 0
            from math import comb
            for i, p in enumerate(puntos):
                coef = comb(n, i) * ((1 - t) ** (n - i)) * (t ** i)
                x += coef * p[0]
                y += coef * p[1]

            return {
                'titulo': f'Bézier - Paso {paso_actual} de {total_pasos}',
                'color': (150, 200, 255),
                'lineas': [
                    {'texto': 'Avanzando a lo largo de la curva...', 'color': (220, 220, 220)},
                    {'texto': f'  • Progreso: {paso_actual * 100 // total_pasos}% completado',
                     'color': (255, 200, 100)},
                    {'texto': f'  • Posición actual: ({x:.1f}, {y:.1f})', 'color': (200, 200, 200)},
                    {'texto': '', 'color': (220, 220, 220)},
                    {'texto': 'La curva se va dibujando desde el inicio', 'color': (220, 220, 220)},
                    {'texto': 'hasta el final, como si un lápiz', 'color': (220, 220, 220)},
                    {'texto': 'estuviera trazando el camino.', 'color': (220, 220, 220)},
                    {'texto': '', 'color': (220, 220, 220)},
                    {'texto': f'→ Píxel pintado: ({round(x)}, {round(y)})', 'color': (255, 255, 150)},
                ]
            }

    @staticmethod
    def bspline(puntos, paso_actual, total_pasos, t_actual=0):
        """Explicación amigable de la B-Spline"""

        if len(puntos) < 4:
            return {
                'titulo': 'B-Spline - Necesita más puntos',
                'color': (255, 100, 100),
                'lineas': [
                    {'texto': 'Para crear una B-Spline necesitas', 'color': (255, 200, 200)},
                    {'texto': f'al menos 4 puntos de control.', 'color': (255, 200, 200)},
                    {'texto': f'  • Tienes: {len(puntos)} puntos', 'color': (255, 200, 200)},
                    {'texto': f'  • Necesitas: 4 puntos', 'color': (255, 200, 100)},
                    {'texto': '', 'color': (220, 220, 220)},
                    {'texto': 'Agrega más puntos para continuar.', 'color': (200, 200, 200)},
                ]
            }

        if paso_actual <= 0:
            return {
                'titulo': 'B-Spline - Curvas con control local',
                'color': (200, 150, 255),
                'lineas': [
                    {'texto': 'La B-Spline es como la Bézier pero', 'color': (220, 220, 220)},
                    {'texto': 'con una ventaja: si mueves un punto', 'color': (220, 220, 220)},
                    {'texto': 'solo afectas una parte de la curva.', 'color': (220, 220, 220)},
                    {'texto': '', 'color': (220, 220, 220)},
                    {'texto': f'  • Puntos de control: {len(puntos)}', 'color': (255, 200, 100)},
                    {'texto': '  • Cada segmento usa 4 puntos', 'color': (255, 200, 100)},
                    {'texto': '', 'color': (220, 220, 220)},
                    {'texto': 'Es perfecta para diseños donde', 'color': (150, 255, 150)},
                    {'texto': 'quieres modificar solo una parte', 'color': (150, 255, 150)},
                    {'texto': 'sin afectar el resto de la curva.', 'color': (150, 255, 150)},
                ]
            }
        else:
            t = t_actual if t_actual > 0 else paso_actual / total_pasos
            segmento = min(paso_actual // 4, len(puntos) - 4)

            return {
                'titulo': f'B-Spline - Paso {paso_actual} de {total_pasos}',
                'color': (200, 150, 255),
                'lineas': [
                    {'texto': f'Dibujando segmento {segmento + 1}...', 'color': (220, 220, 220)},
                    {'texto': f'  • Progreso: {paso_actual * 100 // total_pasos}%', 'color': (255, 200, 100)},
                    {'texto': '', 'color': (220, 220, 220)},
                    {'texto': 'Este segmento usa 4 puntos', 'color': (200, 200, 200)},
                    {'texto': 'de control para crear una curva suave', 'color': (200, 200, 200)},
                    {'texto': 'que se conecta perfectamente', 'color': (200, 200, 200)},
                    {'texto': 'con los segmentos vecinos.', 'color': (200, 200, 200)},
                ]
            }

    @staticmethod
    def traslacion(puntos, tx, ty, paso_actual, total_pasos):
        """Explicación amigable de la traslación"""

        if paso_actual <= 0:
            return {
                'titulo': 'Traslación - Mover objetos',
                'color': (100, 255, 200),
                'lineas': [
                    {'texto': 'La traslación es como mover un objeto', 'color': (220, 220, 220)},
                    {'texto': 'de un lugar a otro en la pantalla.', 'color': (220, 220, 220)},
                    {'texto': '', 'color': (220, 220, 220)},
                    {'texto': '¿Cuánto lo moveremos?', 'color': (255, 200, 100)},
                    {'texto': f'  • Horizontal: {tx} pasos', 'color': (200, 200, 200)},
                    {'texto': f'  • Vertical: {ty} pasos', 'color': (200, 200, 200)},
                    {'texto': '', 'color': (220, 220, 220)},
                    {'texto': f'  • Puntos a mover: {len(puntos)}', 'color': (255, 200, 100)},
                    {'texto': '', 'color': (220, 220, 220)},
                    {'texto': 'Cada punto se moverá la misma', 'color': (150, 255, 150)},
                    {'texto': 'cantidad en la misma dirección.', 'color': (150, 255, 150)},
                ]
            }

    @staticmethod
    def rotacion(puntos, theta, paso_actual, total_pasos):
        """Explicación amigable de la rotación"""

        if paso_actual <= 0:
            return {
                'titulo': 'Rotación - Girar la figura',
                'color': (200, 200, 255),
                'lineas': [
                    {'texto': 'La rotación gira todos los puntos', 'color': (220, 220, 220)},
                    {'texto': 'alrededor de un punto central.', 'color': (220, 220, 220)},
                    {'texto': '', 'color': (220, 220, 220)},
                    {'texto': 'Usaremos coordenadas homogéneas', 'color': (255, 200, 100)},
                    {'texto': 'para realizar la transformación con una', 'color': (220, 220, 220)},
                    {'texto': 'matriz 3x3.', 'color': (220, 220, 220)},
                    {'texto': '', 'color': (220, 220, 220)},
                    {'texto': f'  • Ángulo: {theta}°', 'color': (200, 200, 200)},
                    {'texto': f'  • Puntos: {len(puntos)}', 'color': (200, 200, 200)},
                    {'texto': '', 'color': (220, 220, 220)},
                    {'texto': 'Primero trasladamos, luego rotamos', 'color': (150, 255, 150)},
                    {'texto': 'y finalmente regresamos al centro original.', 'color': (150, 255, 150)},
                ]
            }
        else:
            idx = min(paso_actual - 1, len(puntos) - 1)
            if idx < len(puntos):
                punto = puntos[idx]
                return {
                    'titulo': f'Rotación - Procesando punto {idx + 1} de {len(puntos)}',
                    'color': (200, 200, 255),
                    'lineas': [
                        {'texto': 'Rotando el punto alrededor del centro.', 'color': (220, 220, 220)},
                        {'texto': f'  • Punto original: ({punto[0]:.0f}, {punto[1]:.0f})', 'color': (200, 200, 200)},
                        {'texto': f'  • Ángulo: {theta}°', 'color': (255, 200, 100)},
                        {'texto': '', 'color': (220, 220, 220)},
                        {'texto': 'Cada punto se transforma con', 'color': (150, 255, 150)},
                        {'texto': 'una matriz 3x3 de coordenadas homogéneas.', 'color': (150, 255, 150)},
                        {'texto': f'→ Nuevo punto: ({round(punto[0])}, {round(punto[1])})', 'color': (255, 255, 150)},
                    ]
                }
        return None