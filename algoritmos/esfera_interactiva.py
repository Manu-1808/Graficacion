import numpy as np
import pygame


class EsferaInteractiva:
    # esta clase crea una esfera que se puede iluminar y mover.
    # sirve para ver como cambia la luz sobre la superficie.

    def __init__(self, radio=0.8, resolucion=100):
        self.res = resolucion
        self.radio = radio

        self.luz_pos = np.array([0.0, 0.0, 3.0])
        self.vista_pos = np.array([0.0, 0.0, 5.0])

        self.ka = 0.1
        self.kd = 0.6
        self.ks = 0.3
        self.brillo_n = 32

        self.intensidad_luz = 1.0
        self.color_base = np.array([0.2, 1.0, 0.2])

        self.arrastrando = False
        self.ultimo_mouse = None

        self.crear_geometria()
        self.calcular_iluminacion()

    def crear_geometria(self):
        # aqui se construye la forma de la esfera con muchos puntos.

        self.x = np.linspace(-1, 1, self.res)
        self.y = np.linspace(-1, 1, self.res)

        self.xx, self.yy = np.meshgrid(
            self.x,
            self.y
        )

        self.dist_sq = self.xx**2 + self.yy**2

        self.mascara_esfera = (
            self.dist_sq <= self.radio**2
        )

        self.pz = np.sqrt(
            np.maximum(
                self.radio**2 - self.dist_sq,
                0
            )
        )

        self.px = self.xx
        self.py = self.yy

        self.puntos = np.stack(
            [
                self.px,
                self.py,
                self.pz
            ],
            axis=-1
        )

        self.N = self.puntos.copy()

        norma = np.linalg.norm(
            self.N,
            axis=-1,
            keepdims=True
        )

        self.N = self.N / np.where(
            norma > 0,
            norma,
            1
        )

    def calcular_iluminacion(self):
        # aqui se calcula cuanto brillo recibe la esfera.

        luz = self.luz_pos.reshape(
            1,
            1,
            3
        )

        L = luz - self.puntos

        dist_luz = np.linalg.norm(
            L,
            axis=-1,
            keepdims=True
        )

        L = L / np.where(
            dist_luz > 0,
            dist_luz,
            1
        )

        vista = self.vista_pos.reshape(
            1,
            1,
            3
        )

        V = vista - self.puntos

        dist_vista = np.linalg.norm(
            V,
            axis=-1,
            keepdims=True
        )

        V = V / np.where(
            dist_vista > 0,
            dist_vista,
            1
        )

        dot_nl = np.sum(
            self.N * L,
            axis=-1
        )

        dot_nl = np.maximum(
            dot_nl,
            0
        )

        R = (
            2
            * dot_nl[..., np.newaxis]
            * self.N
            - L
        )

        norma_r = np.linalg.norm(
            R,
            axis=-1,
            keepdims=True
        )

        R = R / np.where(
            norma_r > 0,
            norma_r,
            1
        )

        dot_rv = np.sum(
            R * V,
            axis=-1
        )

        dot_rv = np.maximum(
            dot_rv,
            0
        )

        luz_ambiental = self.ka
        luz_difusa = self.kd * dot_nl

        luz_especular = (
            self.ks
            * (dot_rv ** self.brillo_n)
        )

        atenuacion = (
            1.0
            / (
                1
                + 0.1
                * np.squeeze(
                    dist_luz,
                    axis=-1
                ) ** 2
            )
        )

        intensidad = (
            self.intensidad_luz
            * (
                luz_ambiental
                + luz_difusa
                + luz_especular
            )
            * atenuacion
        )

        img = (
            self.color_base
            * intensidad[..., np.newaxis]
        )

        img = np.clip(
            img,
            0,
            1
        )

        self.img = np.where(
            self.mascara_esfera[..., np.newaxis],
            img,
            0
        )

    def actualizar_luz(
        self,
        mouse_x,
        mouse_y,
        ancho,
        alto
    ):

        x = (
            mouse_x
            / ancho
        ) * 3 - 1.5

        y = -(
            mouse_y
            / alto
        ) * 3 + 1.5

        self.luz_pos[0] = np.clip(
            x,
            -1.5,
            1.5
        )

        self.luz_pos[1] = np.clip(
            -y,
            -1.5,
            1.5
        )

        self.luz_pos[2] = 3.0

        self.calcular_iluminacion()

    def obtener_superficie(
        self,
        tamano=350
    ):

        rgb = (
            self.img
            * 255
        ).astype(np.uint8)

        superficie = pygame.surfarray.make_surface(
            np.transpose(
                rgb,
                (1, 0, 2)
            )
        )

        superficie = pygame.transform.smoothscale(
            superficie,
            (tamano, tamano)
        )

        return superficie