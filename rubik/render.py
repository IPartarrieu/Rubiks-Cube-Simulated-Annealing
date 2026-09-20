"""Renderizado 3D del cubo con matplotlib (Poly3DCollection).

Reutiliza directamente la lista de cubies del motor (cube.py): cada
sticker se dibuja como un cuadrado 3D ubicado en la cara del cubie que
le corresponde, asi el render y la logica de resolucion comparten la
misma fuente de verdad (no hay una representacion 2D separada que
pueda desincronizarse del estado real).
"""

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import proj3d
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from cube import AXES

COLOR_HEX = {
    "U": "#FFFFFF",  # blanco
    "D": "#FFD500",  # amarillo
    "F": "#00A651",  # verde
    "B": "#0051BA",  # azul
    "L": "#FF5800",  # naranjo
    "R": "#C41E3A",  # rojo
}

CUBIE_SIZE = 0.94
STICKER_INSET = 0.07


def _sticker_quad(cubie_pos, axis, sign):
    ai = AXES[axis]
    other = [a for a in ("x", "y", "z") if a != axis]
    o1, o2 = AXES[other[0]], AXES[other[1]]

    half = CUBIE_SIZE / 2 - STICKER_INSET
    face_center = np.array(cubie_pos, dtype=float)
    face_center[ai] += sign * (CUBIE_SIZE / 2)

    corners = []
    for d1, d2 in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
        p = face_center.copy()
        p[o1] += d1 * half
        p[o2] += d2 * half
        corners.append(p)
    return corners


def _camera_direction(elev, azim):
    """Aproxima la direccion camara->origen para el mismo view_init usado
    al graficar (con vertical_axis='y'). Sirve para descartar stickers
    que miran hacia el lado opuesto de la camara (back-face culling):
    matplotlib no ordena bien en profundidad una escena con muchos
    poligonos como un cubo de Rubik, así que en vez de pelear con su
    z-sorting interno, simplemente no se dibujan las caras ocultas.
    """
    e, a = np.deg2rad(elev), np.deg2rad(azim)
    return np.array([np.cos(e) * np.cos(a), np.sin(e), np.cos(e) * np.sin(a)])


BACKGROUND = "#e9ecef"  # gris claro: mantiene visibles los stickers blancos


def render_cube_3d(rubiks_cube, elev=25, azim=45):
    fig = plt.figure(figsize=(5, 5), facecolor=BACKGROUND)
    ax = fig.add_subplot(111, projection="3d")
    ax.set_facecolor(BACKGROUND)
    ax.computed_zorder = False  # respeta el orden que le damos, no el suyo
    ax.set_xlim(-1.6, 1.6)
    ax.set_ylim(-1.6, 1.6)
    ax.set_zlim(-1.6, 1.6)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elev, azim=azim, vertical_axis="y")

    cam = _camera_direction(elev, azim)

    items = []  # (profundidad_real, quad, color)
    for cubie in rubiks_cube.cubies:
        for (axis, sign), color in cubie.stickers.items():
            normal = np.zeros(3)
            normal[AXES[axis]] = sign
            if np.dot(normal, cam) <= 0.05:
                continue  # cara no visible desde la camara: no dibujar
            quad = _sticker_quad(cubie.pos, axis, sign)
            cx, cy, cz = np.mean(quad, axis=0)
            # Profundidad real segun la matriz de proyeccion de matplotlib
            # (mas confiable que aproximar la direccion de camara a mano).
            _, _, depth = proj3d.proj_transform(cx, cy, cz, ax.get_proj())
            items.append((depth, quad, COLOR_HEX[color]))

    items.sort(key=lambda t: t[0])  # de mas lejos a mas cerca de la camara

    # Poly3DCollection reordena los poligonos de UNA coleccion segun su
    # propio heuristico interno de profundidad, lo que ignora el orden
    # que le pasemos. Para respetar el orden pintor calculado arriba,
    # cada sticker se agrega como su propia coleccion (matplotlib SI
    # respeta el orden de insercion entre artistas distintos).
    for z, (_, quad, color) in enumerate(items):
        poly = Poly3DCollection(
            [quad], facecolors=color, edgecolors="black", linewidths=0.8
        )
        poly.set_zorder(z)
        ax.add_collection3d(poly)

    ax.set_axis_off()
    fig.tight_layout(pad=0)
    return fig
