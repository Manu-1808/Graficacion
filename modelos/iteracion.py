from dataclasses import dataclass

@dataclass
class Iteracion:
    paso: int

    x: float
    y: float

    x_redondeado: int
    y_redondeado: int

    error: float = 0