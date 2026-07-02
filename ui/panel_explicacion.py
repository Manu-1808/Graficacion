import pygame
import textwrap

class PanelExplicacion:
    def __init__(self, x, y, ancho, alto):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.datos = None
        self.fuente = None
        self.fuente_titulo = None
        self.fuente_pequena = None
        self.lineas_procesadas = []  # Lista de (texto, color)
        self.titulo = ""
        self.color_titulo = (255, 255, 255)
        self.margen = 15
        self.espaciado_linea = 26
        self.ancho_texto = ancho - (self.margen * 2)

    def actualizar(self, datos, fuente=None):
        """Actualiza el panel con los datos de explicación"""
        self.datos = datos
        self.lineas_procesadas = []
        self.titulo = ""
        self.color_titulo = (255, 255, 255)
        
        if fuente:
            self.fuente = fuente
            self.fuente_titulo = pygame.font.SysFont("Consolas", 20, bold=True)
            self.fuente_pequena = pygame.font.SysFont("Consolas", 15)
        
        if isinstance(datos, str):
            self._procesar_texto_str(datos)
        elif isinstance(datos, dict):
            self._procesar_texto_dict(datos)
        else:
            # Mensaje por defecto
            self.lineas_procesadas = [
                ("Selecciona un algoritmo", (150, 150, 150)),
                ("y ejecuta para ver explicación", (120, 120, 120))
            ]

    def _procesar_texto_str(self, texto):
        """Procesa texto en formato string"""
        lineas = texto.split('\n')
        for linea in lineas:
            if linea.strip():
                # Limpiar formato LaTeX para display
                texto_limpio = self._limpiar_latex(linea)
                
                # Detectar si es título (contiene \textbf o es la primera línea)
                if 'textbf' in linea or (not self.titulo and len(linea) < 50):
                    self.titulo = texto_limpio
                    self.color_titulo = (255, 200, 100)
                else:
                    # Dividir líneas largas
                    for sublinea in self._dividir_texto(texto_limpio):
                        self.lineas_procesadas.append((sublinea, (200, 200, 200)))

    def _procesar_texto_dict(self, datos):
        """Procesa texto en formato diccionario"""
        # Título
        self.titulo = datos.get('titulo', '')
        self.color_titulo = (255, 200, 100)
        
        # Color del borde
        self.color_borde = datos.get('color', (100, 200, 255))
        
        # Procesar líneas
        for linea in datos.get('lineas', []):
            texto = linea.get('texto', '')
            color = linea.get('color', (220, 220, 220))
            
            if texto == '':
                self.lineas_procesadas.append(('', color))
                continue
            
            # Limpiar LaTeX
            texto_limpio = self._limpiar_latex(texto)
            
            # Dividir líneas largas
            for sublinea in self._dividir_texto(texto_limpio):
                self.lineas_procesadas.append((sublinea, color))

    def _limpiar_latex(self, texto):
        """Limpia el formato LaTeX para mostrar texto plano"""
        # Eliminar \textbf{} y otros comandos
        import re
        # Eliminar \textbf{...}
        texto = re.sub(r'\\textbf\{([^}]*)\}', r'\1', texto)
        # Eliminar \textit{...}
        texto = re.sub(r'\\textit\{([^}]*)\}', r'\1', texto)
        # Eliminar otros comandos LaTeX comunes
        texto = re.sub(r'\\[a-zA-Z]+', '', texto)
        # Limpiar llaves sobrantes
        texto = texto.replace('{', '').replace('}', '')
        return texto.strip()

    def _dividir_texto(self, texto, max_lineas=None):
        """Divide el texto en líneas que quepan en el panel"""
        if not texto:
            return ['']
        
        # Si el texto ya es corto, devolverlo
        if self.fuente and self.fuente.size(texto)[0] <= self.ancho_texto:
            return [texto]
        
        # Usar textwrap para dividir
        # Calcular caracteres por línea aproximados
        if self.fuente:
            # Estimar ancho promedio de caracter
            ancho_promedio = self.fuente.size(' ')[0] * 1.2
            max_caracteres = int(self.ancho_texto / ancho_promedio)
        else:
            max_caracteres = 40
        
        # Dividir con textwrap
        lineas = textwrap.wrap(texto, width=max_caracteres, break_long_words=False)
        
        if max_lineas:
            return lineas[:max_lineas]
        return lineas

    def dibujar(self, screen):
        """Dibuja el panel de explicación"""
        # Fondo
        pygame.draw.rect(screen, (30, 30, 35), self.rect)
        pygame.draw.rect(screen, (60, 60, 70), self.rect, 2)
        
        # Borde con color
        if hasattr(self, 'color_borde'):
            pygame.draw.line(
                screen,
                self.color_borde,
                (self.rect.x, self.rect.y),
                (self.rect.x + self.rect.width, self.rect.y),
                3
            )
        
        # Si no hay datos, mostrar mensaje por defecto
        if not self.datos or (isinstance(self.datos, dict) and not self.datos.get('lineas')):
            if self.fuente:
                texto = self.fuente.render(
                    "Selecciona un algoritmo",
                    True,
                    (150, 150, 150)
                )
                x = self.rect.x + (self.rect.width - texto.get_width()) // 2
                y = self.rect.y + 20
                screen.blit(texto, (x, y))
                
                texto2 = self.fuente_pequena.render(
                    "y ejecuta para ver explicación",
                    True,
                    (120, 120, 120)
                )
                x = self.rect.x + (self.rect.width - texto2.get_width()) // 2
                y = self.rect.y + 50
                screen.blit(texto2, (x, y))
            return
        
        # Dibujar título
        if self.titulo and self.fuente_titulo:
            # Limpiar el título de LaTeX
            titulo_limpio = self._limpiar_latex(self.titulo)
            titulo_render = self.fuente_titulo.render(
                titulo_limpio,
                True,
                self.color_titulo
            )
            screen.blit(titulo_render, (self.rect.x + self.margen, self.rect.y + 10))
            
            # Línea separadora
            y_titulo = self.rect.y + 40
            pygame.draw.line(
                screen,
                (60, 60, 70),
                (self.rect.x + self.margen, y_titulo),
                (self.rect.x + self.rect.width - self.margen, y_titulo),
                1
            )
            y_actual = y_titulo + 10
        else:
            y_actual = self.rect.y + 15
        
        # Dibujar líneas
        for texto, color in self.lineas_procesadas:
            # Verificar si hay espacio
            if y_actual > self.rect.y + self.rect.height - 20:
                break
            
            # Si es línea vacía, solo aumentar espacio
            if not texto:
                y_actual += 8
                continue
            
            # Renderizar texto
            if self.fuente:
                render = self.fuente.render(texto, True, color)
                x = self.rect.x + self.margen
                screen.blit(render, (x, y_actual))
                y_actual += self.espaciado_linea

    def _dict_a_string(self, datos):
        """Convierte diccionario a string formateado (método auxiliar)"""
        if isinstance(datos, str):
            return datos
        lineas = []
        if 'titulo' in datos:
            lineas.append(f"# {datos['titulo']}")
        for linea in datos.get('lineas', []):
            texto = linea.get('texto', '')
            if texto:
                lineas.append(texto)
        return "\n".join(lineas)