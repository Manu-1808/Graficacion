
import pygame
import pygame_gui


class BarraHerramientas:

    def __init__(self, manager):

        self.combo = pygame_gui.elements.UIDropDownMenu(
            options_list=[
                "DDA",
                "Bresenham",
                "Bezier",
                "B-Spline",
                "Traslacion",
                "Rotacion"
            ],
            starting_option="DDA",
            relative_rect=pygame.Rect(
                20,
                20,
                200,
                40
            ),
            manager=manager
        )

        self.btn_ejecutar = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                20,
                80,
                200,
                40
            ),
            text="Ejecutar",
            manager=manager
        )

        self.btn_reiniciar = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                20,
                140,
                200,
                40
            ),
            text="Reiniciar",
            manager=manager
        )

        self.btn_cerrar_figura = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                20,
                200,
                200,
                40
            ),
            text="Cerrar Figura",
            manager=manager
        )

        self.lbl_tx = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(
                20,
                270,
                40,
                30
            ),
            text="Tx:",
            manager=manager
        )

        self.input_tx = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(
                60,
                270,
                80,
                30
            ),
            manager=manager
        )

        self.input_tx.set_text("5")

        self.lbl_ty = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(
                20,
                320,
                40,
                30
            ),
            text="Ty:",
            manager=manager
        )

        self.input_ty = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(
                60,
                320,
                80,
                30
            ),
            manager=manager
        )

        self.input_ty.set_text("5")

        self.lbl_theta = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(
                20,
                370,
                60,
                30
            ),
            text="Theta:",
            manager=manager
        )

        self.input_theta = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(
                80,
                370,
                60,
                30
            ),
            manager=manager
        )

        self.input_theta.set_text("45")
