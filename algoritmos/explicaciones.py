class ExplicadorAlgoritmos:
    """Explicaciones para público general - sin tecnicismos"""

    @staticmethod
    def dda(x1, y1, x2, y2, paso_actual, total_pasos):
        """Explicación amigable del algoritmo DDA"""

        if paso_actual <= 0:
            dx = x2 - x1
            dy = y2 - y1

            return {
                'titulo': 'DDA - Dibujando una línea recta',
                'color': (100, 200, 255),
                'lineas': [
                    {'texto': 'Paso 1: Comprendiendo el problema', 'color': (255, 200, 100)},
                    {'texto': 'Imagina que quieres dibujar una línea', 'color': (220, 220, 220)},
                    {'texto': 'del punto A al punto B en una cuadrícula.', 'color': (220, 220, 220)},
                    {'texto': '', 'color': (220, 220, 220)},
                    
                    {'texto': 'Paso 2: Analizando los datos', 'color': (255, 200, 100)},
                    {'texto': f'• Punto de inicio: ({x1:.0f}, {y1:.0f})', 'color': (200, 200, 200)},
                    {'texto': f'• Punto final: ({x2:.0f}, {y2:.0f})', 'color': (200, 200, 200)},
                    {'texto': f'• Distancia horizontal: {dx:.0f} pasos', 'color': (200, 200, 200)},
                    {'texto': f'• Distancia vertical: {dy:.0f} pasos', 'color': (200, 200, 200)},
                    {'texto': '', 'color': (220, 220, 220)},
                    
                    {'texto': 'Paso 3: Planificando el recorrido', 'color': (255, 200, 100)},
                    {'texto': 'El algoritmo calculará paso a paso', 'color': (150, 255, 150)},
                    {'texto': 'cómo llegar del inicio al final.', 'color': (150, 255, 150)},
                    {'texto': 'En cada paso, avanzará un poco en', 'color': (150, 255, 150)},
                    {'texto': 'horizontal y vertical simultáneamente.', 'color': (150, 255, 150)}
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
                    {'texto': 'Paso 1: Verificando el progreso', 'color': (255, 200, 100)},
                    {'texto': f'• Avance: {paso_actual}/{total_pasos} del camino', 'color': (255, 200, 100)},
                    {'texto': f'• Posición actual: ({x_actual:.1f}, {y_actual:.1f})', 'color': (200, 200, 200)},
                    {'texto': '', 'color': (220, 220, 220)},
                    
                    {'texto': 'Paso 2: Calculando el siguiente punto', 'color': (255, 200, 100)},
                    {'texto': 'El algoritmo avanza un poco en horizontal', 'color': (220, 220, 220)},
                    {'texto': 'y un poco en vertical, manteniendo', 'color': (220, 220, 220)},
                    {'texto': 'la proporción de la línea original.', 'color': (220, 220, 220)},
                    {'texto': '', 'color': (220, 220, 220)},
                    
                    {'texto': 'Paso 3: Pintando el píxel', 'color': (255, 200, 100)},
                    {'texto': f'→ Pintamos el píxel ({round(x_actual)}, {round(y_actual)})', 'color': (255, 255, 150)}
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
                    {'texto': 'Paso 1: Conociendo el algoritmo', 'color': (255, 200, 100)},
                    {'texto': 'Este algoritmo es más eficiente porque', 'color': (220, 220, 220)},
                    {'texto': 'solo usa números enteros para decidir', 'color': (220, 220, 220)},
                    {'texto': 'qué píxeles debe iluminar.', 'color': (220, 220, 220)},
                    {'texto': '', 'color': (220, 220, 220)},
                    
                    {'texto': 'Paso 2: Analizando la línea', 'color': (255, 200, 100)},
                    {'texto': f'• Avanza {dx} pasos en horizontal', 'color': (200, 200, 200)},
                    {'texto': f'• Avanza {dy} pasos en vertical', 'color': (200, 200, 200)},
                    {'texto': f'• Inclinación: {dy / dx:.2f}', 'color': (200, 200, 200)},
                    {'texto': '', 'color': (220, 220, 220)},
                    
                    {'texto': 'Paso 3: Preparando la decisión', 'color': (255, 200, 100)},
                    {'texto': 'El algoritmo va decidiendo en cada paso', 'color': (150, 255, 150)},
                    {'texto': 'si debe subir, bajar o seguir recto.', 'color': (150, 255, 150)},
                    {'texto': 'Para eso usa un "error" que se actualiza', 'color': (150, 255, 150)},
                    {'texto': 'en cada iteración.', 'color': (150, 255, 150)}
                ]
            }
        else:
            decision = "subir" if error_actual < 0 else "seguir recto"
            return {
                'titulo': f'Bresenham - Paso {paso_actual}',
                'color': (255, 150, 100),
                'lineas': [
                    {'texto': 'Paso 1: Evaluando el error', 'color': (255, 200, 100)},
                    {'texto': f'• Error actual = {error_actual}', 'color': (255, 200, 100)},
                    {'texto': '', 'color': (220, 220, 220)},
                    
                    {'texto': 'Paso 2: Tomando una decisión', 'color': (255, 200, 100)},
                    {'texto': 'El error nos indica si estamos', 'color': (220, 220, 220)},
                    {'texto': 'por encima o por debajo de la línea ideal.', 'color': (220, 220, 220)},
                    {'texto': f'→ Decisión: {decision}', 'color': (150, 255, 150)},
                    {'texto': '', 'color': (220, 220, 220)},
                    
                    {'texto': 'Paso 3: Actualizando el error', 'color': (255, 200, 100)},
                    {'texto': 'El error se actualiza para la siguiente', 'color': (200, 200, 200)},
                    {'texto': 'iteración, manteniendo la precisión', 'color': (200, 200, 200)},
                    {'texto': 'de la línea que estamos dibujando.', 'color': (200, 200, 200)}
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
                    {'texto': 'Paso 1: Entendiendo las curvas Bézier', 'color': (255, 200, 100)},
                    {'texto': 'Esta curva se crea usando puntos de control', 'color': (220, 220, 220)},
                    {'texto': 'que funcionan como "imanes" que atraen', 'color': (220, 220, 220)},
                    {'texto': 'la curva hacia ellos.', 'color': (220, 220, 220)},
                    {'texto': '', 'color': (220, 220, 220)},
                    
                    {'texto': 'Paso 2: Configurando los puntos', 'color': (255, 200, 100)},
                    {'texto': f'• Puntos de control: {len(puntos)}', 'color': (255, 200, 100)},
                    {'texto': f'• Grado de la curva: {n}', 'color': (255, 200, 100)},
                    {'texto': '', 'color': (220, 220, 220)},
                    
                    {'texto': 'Paso 3: Visualizando el recorrido', 'color': (255, 200, 100)},
                    {'texto': 'La curva comenzará en el primer punto', 'color': (150, 255, 150)},
                    {'texto': 'y terminará en el último, pasando', 'color': (150, 255, 150)},
                    {'texto': 'cerca de los puntos intermedios.', 'color': (150, 255, 150)},
                    {'texto': 'El parámetro t controla el avance.', 'color': (150, 255, 150)}
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
                    {'texto': 'Paso 1: Calculando la posición', 'color': (255, 200, 100)},
                    {'texto': f'• Progreso: {paso_actual * 100 // total_pasos}% completado', 'color': (255, 200, 100)},
                    {'texto': f'• Posición actual: ({x:.1f}, {y:.1f})', 'color': (200, 200, 200)},
                    {'texto': '', 'color': (220, 220, 220)},
                    
                    {'texto': 'Paso 2: Aplicando la fórmula', 'color': (255, 200, 100)},
                    {'texto': 'La posición se calcula usando', 'color': (220, 220, 220)},
                    {'texto': 'los polinomios de Bernstein, que', 'color': (220, 220, 220)},
                    {'texto': 'combinan todos los puntos de control.', 'color': (220, 220, 220)},
                    {'texto': '', 'color': (220, 220, 220)},
                    
                    {'texto': 'Paso 3: Dibujando el punto', 'color': (255, 200, 100)},
                    {'texto': f'→ Píxel pintado: ({round(x)}, {round(y)})', 'color': (255, 255, 150)}
                ]
            }

    @staticmethod
    def bspline(puntos, paso_actual, total_pasos, t_actual=0):
        """Explicación amigable de la B-Spline"""

        if len(puntos) < 4:
            return {
                'titulo': 'B-Spline - Se necesitan más puntos',
                'color': (255, 100, 100),
                'lineas': [
                    {'texto': r'\textbf{Paso 1:} Verificando requisitos', 'color': (255, 200, 100)},
                    {'texto': 'Para crear una B-Spline necesitas', 'color': (255, 200, 200)},
                    {'texto': f'al menos 4 puntos de control.', 'color': (255, 200, 200)},
                    {'texto': '', 'color': (220, 220, 220)},
                    
                    {'texto': r'\textbf{Paso 2:} Contando puntos disponibles', 'color': (255, 200, 100)},
                    {'texto': f'  • Tienes: {len(puntos)} puntos', 'color': (255, 200, 200)},
                    {'texto': f'  • Necesitas: 4 puntos', 'color': (255, 200, 100)},
                    {'texto': '', 'color': (220, 220, 220)},
                    
                    {'texto': r'\textbf{Paso 3:} Próxima acción', 'color': (255, 200, 100)},
                    {'texto': 'Agrega más puntos de control', 'color': (200, 200, 200)},
                    {'texto': 'para poder crear la curva B-Spline.', 'color': (200, 200, 200)}
                ]
            }

        if paso_actual <= 0:
            return {
                'titulo': 'B-Spline - Control local',
                'color': (200, 150, 255),
                'lineas': [
                    {'texto': r'\textbf{Paso 1:} Entendiendo B-Spline', 'color': (255, 200, 100)},
                    {'texto': 'La B-Spline es como la Bézier pero', 'color': (220, 220, 220)},
                    {'texto': 'con una ventaja: si mueves un punto', 'color': (220, 220, 220)},
                    {'texto': 'solo afectas una parte de la curva.', 'color': (220, 220, 220)},
                    {'texto': '', 'color': (220, 220, 220)},
                    
                    {'texto': r'\textbf{Paso 2:} Configuración de la curva', 'color': (255, 200, 100)},
                    {'texto': f'  • Puntos de control: {len(puntos)}', 'color': (255, 200, 100)},
                    {'texto': '  • Cada segmento usa 4 puntos', 'color': (255, 200, 100)},
                    {'texto': '', 'color': (220, 220, 220)},
                    
                    {'texto': r'\textbf{Paso 3:} Ventajas del control local', 'color': (255, 200, 100)},
                    {'texto': 'Es perfecta para diseños donde', 'color': (150, 255, 150)},
                    {'texto': 'quieres modificar solo una parte', 'color': (150, 255, 150)},
                    {'texto': 'sin afectar el resto de la curva.', 'color': (150, 255, 150)}
                ]
            }
        else:
            t = t_actual if t_actual > 0 else paso_actual / total_pasos
            segmento = min(paso_actual // 4, len(puntos) - 4)

            return {
                'titulo': f'B-Spline - Paso {paso_actual} de {total_pasos}',
                'color': (200, 150, 255),
                'lineas': [
                    {'texto': r'\textbf{Paso 1:} Progreso del dibujo', 'color': (255, 200, 100)},
                    {'texto': f'  • Segmento actual: {segmento + 1}', 'color': (255, 200, 100)},
                    {'texto': f'  • Progreso: {paso_actual * 100 // total_pasos}%', 'color': (255, 200, 100)},
                    {'texto': '', 'color': (220, 220, 220)},
                    
                    {'texto': r'\textbf{Paso 2:} Creando el segmento', 'color': (255, 200, 100)},
                    {'texto': 'Este segmento usa 4 puntos', 'color': (200, 200, 200)},
                    {'texto': 'de control para crear una curva suave', 'color': (200, 200, 200)},
                    {'texto': '', 'color': (220, 220, 220)},
                    
                    {'texto': r'\textbf{Paso 3:} Conexión con vecinos', 'color': (255, 200, 100)},
                    {'texto': 'La curva se conecta perfectamente', 'color': (150, 255, 150)},
                    {'texto': 'con los segmentos vecinos.', 'color': (150, 255, 150)}
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
                    {'texto': r'\textbf{Paso 1:} ¿Qué es la traslación?', 'color': (255, 200, 100)},
                    {'texto': 'La traslación es como mover un objeto', 'color': (220, 220, 220)},
                    {'texto': 'de un lugar a otro en la pantalla.', 'color': (220, 220, 220)},
                    {'texto': '', 'color': (220, 220, 220)},
                    
                    {'texto': r'\textbf{Paso 2:} Especificando el movimiento', 'color': (255, 200, 100)},
                    {'texto': f'  • Movimiento horizontal: {tx} pasos', 'color': (200, 200, 200)},
                    {'texto': f'  • Movimiento vertical: {ty} pasos', 'color': (200, 200, 200)},
                    {'texto': f'  • Puntos a mover: {len(puntos)}', 'color': (255, 200, 100)},
                    {'texto': '', 'color': (220, 220, 220)},
                    
                    {'texto': r'\textbf{Paso 3:} El proceso de movimiento', 'color': (255, 200, 100)},
                    {'texto': 'Cada punto se moverá la misma', 'color': (150, 255, 150)},
                    {'texto': 'cantidad en la misma dirección.', 'color': (150, 255, 150)},
                    {'texto': 'La forma del objeto se mantiene igual.', 'color': (150, 255, 150)}
                ]
            }
        else:
            idx = min(paso_actual - 1, len(puntos) - 1)
            if idx < len(puntos):
                punto = puntos[idx]
                return {
                    'titulo': f'Traslación - Moviendo punto {idx + 1} de {len(puntos)}',
                    'color': (100, 255, 200),
                    'lineas': [
                        {'texto': r'\textbf{Paso 1:} Punto original', 'color': (255, 200, 100)},
                        {'texto': f'  • Posición original: ({punto[0]:.0f}, {punto[1]:.0f})', 'color': (200, 200, 200)},
                        {'texto': f'  • Desplazamiento: ({tx}, {ty})', 'color': (255, 200, 100)},
                        {'texto': '', 'color': (220, 220, 220)},
                        
                        {'texto': r'\textbf{Paso 2:} Aplicando la traslación', 'color': (255, 200, 100)},
                        {'texto': 'Se suman las distancias horizontal', 'color': (220, 220, 220)},
                        {'texto': 'y vertical a cada punto del objeto.', 'color': (220, 220, 220)},
                        {'texto': '', 'color': (220, 220, 220)},
                        
                        {'texto': r'\textbf{Paso 3:} Resultado', 'color': (255, 200, 100)},
                        {'texto': f'  • Nueva posición: ({punto[0] + tx:.0f}, {punto[1] + ty:.0f})', 'color': (150, 255, 150)}
                    ]
                }
        return None

    @staticmethod
    def rotacion(puntos, theta, paso_actual, total_pasos):
        """Explicación amigable de la rotación"""

        if paso_actual <= 0:
            return {
                'titulo': 'Rotación - Girar la figura',
                'color': (200, 200, 255),
                'lineas': [
                    {'texto': r'\textbf{Paso 1:} ¿Qué es la rotación?', 'color': (255, 200, 100)},
                    {'texto': 'La rotación gira todos los puntos', 'color': (220, 220, 220)},
                    {'texto': 'alrededor de un punto central.', 'color': (220, 220, 220)},
                    {'texto': '', 'color': (220, 220, 220)},
                    
                    {'texto': r'\textbf{Paso 2:} Preparando la transformación', 'color': (255, 200, 100)},
                    {'texto': 'Usaremos coordenadas homogéneas', 'color': (200, 200, 200)},
                    {'texto': 'para realizar la transformación con una', 'color': (200, 200, 200)},
                    {'texto': 'matriz 3x3.', 'color': (200, 200, 200)},
                    {'texto': f'  • Ángulo: {theta}°', 'color': (255, 200, 100)},
                    {'texto': f'  • Puntos: {len(puntos)}', 'color': (255, 200, 100)},
                    {'texto': '', 'color': (220, 220, 220)},
                    
                    {'texto': r'\textbf{Paso 3:} El proceso de rotación', 'color': (255, 200, 100)},
                    {'texto': 'Primero trasladamos al centro,', 'color': (150, 255, 150)},
                    {'texto': 'luego rotamos y finalmente', 'color': (150, 255, 150)},
                    {'texto': 'regresamos al centro original.', 'color': (150, 255, 150)}
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
                        {'texto': r'\textbf{Paso 1:} Punto a rotar', 'color': (255, 200, 100)},
                        {'texto': f'  • Punto original: ({punto[0]:.0f}, {punto[1]:.0f})', 'color': (200, 200, 200)},
                        {'texto': f'  • Ángulo de rotación: {theta}°', 'color': (255, 200, 100)},
                        {'texto': '', 'color': (220, 220, 220)},
                        
                        {'texto': r'\textbf{Paso 2:} Aplicando la matriz de rotación', 'color': (255, 200, 100)},
                        {'texto': 'Cada punto se transforma con', 'color': (220, 220, 220)},
                        {'texto': 'una matriz 3x3 de coordenadas homogéneas.', 'color': (220, 220, 220)},
                        {'texto': 'La matriz incluye senos y cosenos', 'color': (220, 220, 220)},
                        {'texto': 'del ángulo de rotación.', 'color': (220, 220, 220)},
                        {'texto': '', 'color': (220, 220, 220)},
                        
                        {'texto': r'\textbf{Paso 3:} Resultado', 'color': (255, 200, 100)},
                        {'texto': f'→ Nuevo punto: ({round(punto[0])}, {round(punto[1])})', 'color': (255, 255, 150)}
                    ]
                }
        return None

    @staticmethod
    def esfera_3d(angulo_x, angulo_y):
        """Explicación amigable de la esfera 3D"""

        return {
            'titulo': 'Esfera 3D - Visualización interactiva',
            'color': (150, 220, 255),
            'lineas': [
                {'texto': r'\textbf{Paso 1:} ¿Cómo se genera una esfera 3D?', 'color': (255, 200, 100)},
                {'texto': 'La esfera se genera utilizando', 'color': (220, 220, 220)},
                {'texto': 'coordenadas paramétricas en 3D.', 'color': (220, 220, 220)},
                {'texto': 'Se divide en pequeñas cuadrículas', 'color': (220, 220, 220)},
                {'texto': 'que forman polígonos en la superficie.', 'color': (220, 220, 220)},
                {'texto': '', 'color': (220, 220, 220)},

                {'texto': r'\textbf{Paso 2:} Características principales', 'color': (255, 200, 100)},
                {'texto': '  • 25 divisiones en cada dirección', 'color': (200, 200, 200)},
                {'texto': '  • 625 polígonos en total', 'color': (200, 200, 200)},
                {'texto': '  • Colores que muestran profundidad', 'color': (200, 200, 200)},
                {'texto': '  • Iluminación según la superficie', 'color': (200, 200, 200)},
                {'texto': '', 'color': (220, 220, 220)},

                {'texto': r'\textbf{Paso 3:} Controles de la vista', 'color': (255, 200, 100)},
                {'texto': f'  • Ángulo X: {angulo_x:.1f}°', 'color': (200, 200, 200)},
                {'texto': f'  • Ángulo Y: {angulo_y:.1f}°', 'color': (200, 200, 200)},
                {'texto': '', 'color': (220, 220, 220)},

                {'texto': r'\textbf{Paso 4:} Interacción', 'color': (255, 200, 100)},
                {'texto': '  • Arrastra el mouse para rotar la esfera', 'color': (150, 255, 150)},
                {'texto': '  • Usa la rueda para hacer zoom', 'color': (150, 255, 150)},
                {'texto': '  • Observa cómo cambia la perspectiva', 'color': (150, 255, 150)},
                {'texto': '  • Los colores se actualizan dinámicamente', 'color': (150, 255, 150)}
            ]
        }
    
    def cubo_3d(self, angulo_x, angulo_y, distancia_vista):
        """Genera explicación para el cubo 3D."""
        import numpy as np
        return {
            'titulo': 'Cubo 3D - Renderizado en tiempo real',
            'color': (255, 200, 100),
            'lineas': [
                {'texto': r'\textbf{Paso 1:} Estructura del cubo 3D', 'color': (255, 200, 100)},
                {'texto': '  • 8 vértices en coordenadas 3D', 'color': (200, 200, 200)},
                {'texto': '  • 12 aristas que forman el cubo', 'color': (200, 200, 200)},
                {'texto': '  • 6 caras renderizadas', 'color': (200, 200, 200)},
                {'texto': '  • Caras semi-transparentes', 'color': (200, 200, 200)},
                {'texto': '', 'color': (220, 220, 220)},
                
                {'texto': r'\textbf{Paso 2:} Vista actual', 'color': (255, 200, 100)},
                {'texto': f'  • Ángulo X: {np.degrees(angulo_x):.1f}°', 'color': (200, 200, 200)},
                {'texto': f'  • Ángulo Y: {np.degrees(angulo_y):.1f}°', 'color': (200, 200, 200)},
                {'texto': f'  • Distancia de vista: {distancia_vista:.1f}', 'color': (200, 200, 200)},
                {'texto': '', 'color': (220, 220, 220)},
                
                {'texto': r'\textbf{Paso 3:} Proceso de renderizado', 'color': (255, 200, 100)},
                {'texto': '  • Se rotan los vértices según ángulos', 'color': (150, 255, 150)},
                {'texto': '  • Se proyectan a 2D con perspectiva', 'color': (150, 255, 150)},
                {'texto': '  • Se ordenan las caras por profundidad', 'color': (150, 255, 150)},
                {'texto': '  • Se dibujan de atrás hacia adelante', 'color': (150, 255, 150)},
                {'texto': '', 'color': (220, 220, 220)},
                
                {'texto': r'\textbf{Paso 4:} Interacción', 'color': (255, 200, 100)},
                {'texto': '  • Arrastra con el mouse para rotar', 'color': (200, 200, 200)},
                {'texto': '  • Rueda para acercar/alejar', 'color': (200, 200, 200)},
                {'texto': f'  • Zoom actual: {distancia_vista:.1f}x', 'color': (200, 200, 200)}
            ]
        }