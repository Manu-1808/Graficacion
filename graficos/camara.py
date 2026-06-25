class Camara:

    def __init__(self):

        self.zoom = 25

        self.offset_x = 0
        self.offset_y = 0

    def mundo_a_pantalla(self, x, y):

        return (
            x * self.zoom + self.offset_x,
            y * self.zoom + self.offset_y
        )

    def pantalla_a_mundo(self, x, y):

        return (
            int((x - self.offset_x) / self.zoom),
            int((y - self.offset_y) / self.zoom)
        )