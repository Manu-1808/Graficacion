from __future__ import annotations

import io
from functools import lru_cache
from typing import Tuple

import pygame

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

Color = Tuple[int, int, int]


def _color_a_mpl(color: Color) -> tuple[float, float, float]:
    return tuple(max(0, min(255, c)) / 255 for c in color)


@lru_cache(maxsize=256)
def _renderizar_formula_cache(
    formula: str,
    color: Color,
    fondo: Color,
    fontsize: int,
    dpi: int,
) -> bytes:
    formula = formula.strip()

    # MathText necesita que la expresión vaya entre signos $...$.
    if not (formula.startswith("$") and formula.endswith("$")):
        formula = f"${formula}$"

    fig = plt.figure(figsize=(0.01, 0.01), dpi=dpi)
    fig.patch.set_facecolor(_color_a_mpl(fondo))

    texto = fig.text(
        0,
        0,
        formula,
        fontsize=fontsize,
        color=_color_a_mpl(color),
        va="bottom",
        ha="left",
    )

    # Calcula el tamaño exacto del texto para recortar la imagen.
    fig.canvas.draw()
    bbox = texto.get_window_extent(renderer=fig.canvas.get_renderer())

    ancho = max(1, bbox.width / dpi)
    alto = max(1, bbox.height / dpi)

    plt.close(fig)

    fig = plt.figure(figsize=(ancho, alto), dpi=dpi)
    fig.patch.set_facecolor(_color_a_mpl(fondo))
    fig.text(
        0,
        0,
        formula,
        fontsize=fontsize,
        color=_color_a_mpl(color),
        va="bottom",
        ha="left",
    )

    buffer = io.BytesIO()
    fig.savefig(
        buffer,
        format="png",
        dpi=dpi,
        facecolor=fig.get_facecolor(),
        edgecolor="none",
        bbox_inches="tight",
        pad_inches=0.08,
    )
    plt.close(fig)

    buffer.seek(0)
    return buffer.read()


def renderizar_latex_a_surface(
    formula: str,
    color: Color = (240, 240, 240),
    fondo: Color = (30, 30, 35),
    fontsize: int = 18,
    dpi: int = 160,
) -> pygame.Surface:
    try:
        png_bytes = _renderizar_formula_cache(
            formula.strip(),
            color,
            fondo,
            fontsize,
            dpi,
        )
        return pygame.image.load(io.BytesIO(png_bytes), "formula.png").convert()

    except Exception:
        fuente = pygame.font.SysFont("Consolas", max(14, fontsize))
        return fuente.render(formula, True, color, fondo)
