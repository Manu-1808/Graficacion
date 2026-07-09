# ui/barra_herramientas.py
import pygame
import pygame_gui

class BarraHerramientas:

    def __init__(self, manager):
        # Constantes para espaciado
        MARGEN = 20
        ANCHO_CONTROL = 200
        ALTO_CONTROL = 40
        ESPACIO = 8 
        
        y_actual = MARGEN

        self.combo = pygame_gui.elements.UIDropDownMenu(
            options_list=[
                "DDA",
                "Bresenham",
                "Bezier",
                "B-Spline",
                "Traslacion",
                "Rotacion",
                "Esfera 3D con rejillas",
                "Cubo 3D",
                "Esfera 3D Interactiva",
                "Gouraud vs Phong"
            ],
            starting_option="DDA",
            relative_rect=pygame.Rect(
                MARGEN,
                y_actual,
                ANCHO_CONTROL,
                ALTO_CONTROL
            ),
            manager=manager
        )
        y_actual += ALTO_CONTROL + ESPACIO

        # acciones
        self.btn_ejecutar = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                MARGEN,
                y_actual,
                ANCHO_CONTROL,
                ALTO_CONTROL
            ),
            text="Ejecutar",
            manager=manager
        )
        y_actual += ALTO_CONTROL + ESPACIO

        self.btn_reiniciar = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                MARGEN,
                y_actual,
                ANCHO_CONTROL,
                ALTO_CONTROL
            ),
            text="Reiniciar",
            manager=manager
        )
        y_actual += ALTO_CONTROL + ESPACIO

        self.btn_cerrar_figura = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                MARGEN,
                y_actual,
                ANCHO_CONTROL,
                ALTO_CONTROL
            ),
            text="Cerrar Figura",
            manager=manager
        )
        y_actual += ALTO_CONTROL + ESPACIO * 2 

        # transformaciones
        self.lbl_seccion_transformaciones = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(MARGEN, y_actual, ANCHO_CONTROL, 25),
            text="--- TRANSFORMACIONES ---",
            manager=manager
        )
        y_actual += 35

        self.lbl_tx = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(
                MARGEN,
                y_actual,
                30,
                30
            ),
            text="Tx:",
            manager=manager
        )

        self.input_tx = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(
                MARGEN + 35,
                y_actual,
                70,
                30
            ),
            manager=manager
        )
        self.input_tx.set_text("5")
        y_actual += 40

        self.lbl_ty = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(
                MARGEN,
                y_actual,
                30,
                30
            ),
            text="Ty:",
            manager=manager
        )

        self.input_ty = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(
                MARGEN + 35,
                y_actual,
                70,
                30
            ),
            manager=manager
        )
        self.input_ty.set_text("5")
        y_actual += 40

        self.lbl_theta = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(
                MARGEN,
                y_actual,
                45,
                30
            ),
            text="θ:",
            manager=manager
        )

        self.input_theta = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(
                MARGEN + 50,
                y_actual,
                55,
                30
            ),
            manager=manager
        )
        self.input_theta.set_text("45")