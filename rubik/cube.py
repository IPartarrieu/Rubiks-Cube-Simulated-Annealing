"""Motor del Cubo de Rubik 3x3x3.

En vez de escribir a mano las tablas de permutacion de las 54
stickers para cada uno de los 18 movimientos (facil de transcribir
mal), el cubo se modela geometricamente: 26 "cubies" (piezas)
ubicadas en coordenadas enteras (x,y,z) en {-1,0,1}^3, cada una con
sus stickers (caras pintadas). Un movimiento de capa se implementa
como una rotacion real de 90 grados de las piezas de esa capa, tanto
en posicion como en la direccion de sus stickers. Esto es mucho mas
facil de verificar (ver tests/test_cube.py) que tablas de indices.
"""

import itertools
import random

AXES = {"x": 0, "y": 1, "z": 2}

# Direccion (eje, signo) -> color de esa cara cuando el cubo esta resuelto.
FACE_COLORS = {
    ("x", 1): "R",   # derecha  (rojo)
    ("x", -1): "L",  # izquierda (naranjo)
    ("y", 1): "U",   # arriba   (blanco)
    ("y", -1): "D",  # abajo    (amarillo)
    ("z", 1): "F",   # frente   (verde)
    ("z", -1): "B",  # atras    (azul)
}

# Nombre de movimiento base -> (eje, capa) que mueve.
MOVES = {
    "R": ("x", 1), "L": ("x", -1),
    "U": ("y", 1), "D": ("y", -1),
    "F": ("z", 1), "B": ("z", -1),
}

ALL_MOVE_NAMES = [base + suf for base in MOVES for suf in ("", "'", "2")]


class Cubie:
    __slots__ = ("pos", "stickers")

    def __init__(self, pos, stickers):
        self.pos = pos            # (x, y, z)
        self.stickers = stickers  # {(eje, signo): color} solo caras expuestas


def _solved_cubies():
    cubies = []
    for x, y, z in itertools.product((-1, 0, 1), repeat=3):
        if (x, y, z) == (0, 0, 0):
            continue
        stickers = {}
        if x != 0:
            stickers[("x", x)] = FACE_COLORS[("x", x)]
        if y != 0:
            stickers[("y", y)] = FACE_COLORS[("y", y)]
        if z != 0:
            stickers[("z", z)] = FACE_COLORS[("z", z)]
        cubies.append(Cubie((x, y, z), stickers))
    return cubies


def _rotate_layer(cubies, axis, layer, clockwise=True):
    """Rota 90 grados (posicion y stickers) los cubies con coord `axis`==layer."""
    ai = AXES[axis]
    other_axes = [a for a in ("x", "y", "z") if a != axis]
    o1, o2 = AXES[other_axes[0]], AXES[other_axes[1]]
    sign = 1 if clockwise else -1

    for c in cubies:
        if c.pos[ai] != layer:
            continue

        p = list(c.pos)
        v1, v2 = p[o1], p[o2]
        p[o1], p[o2] = -sign * v2, sign * v1
        c.pos = tuple(p)

        new_stickers = {}
        for (sax, ssign), color in c.stickers.items():
            if sax == axis:
                new_stickers[(sax, ssign)] = color
                continue
            si = AXES[sax]
            v = [0, 0, 0]
            v[si] = ssign
            v1o, v2o = v[o1], v[o2]
            v[o1], v[o2] = -sign * v2o, sign * v1o
            if v[o1] != 0:
                new_axis, new_sign = other_axes[0], v[o1]
            else:
                new_axis, new_sign = other_axes[1], v[o2]
            new_stickers[(new_axis, new_sign)] = color
        c.stickers = new_stickers


class RubiksCube:
    def __init__(self):
        self.cubies = _solved_cubies()

    def apply_move(self, move_name):
        """move_name: 'R', "R'" (contrareloj) o 'R2' (180 grados)."""
        base = move_name[0]
        axis, layer = MOVES[base]
        if move_name.endswith("'"):
            _rotate_layer(self.cubies, axis, layer, clockwise=False)
        elif move_name.endswith("2"):
            _rotate_layer(self.cubies, axis, layer, clockwise=True)
            _rotate_layer(self.cubies, axis, layer, clockwise=True)
        else:
            _rotate_layer(self.cubies, axis, layer, clockwise=True)

    def scramble(self, n_moves, rng=None):
        rng = rng or random
        seq = [rng.choice(ALL_MOVE_NAMES) for _ in range(n_moves)]
        for m in seq:
            self.apply_move(m)
        return seq

    def fitness(self):
        """Numero de stickers que no estan en la cara que les corresponde."""
        mismatches = 0
        for c in self.cubies:
            for direction, color in c.stickers.items():
                if color != FACE_COLORS[direction]:
                    mismatches += 1
        return mismatches

    def is_solved(self):
        return self.fitness() == 0

    def copy(self):
        new = RubiksCube.__new__(RubiksCube)
        new.cubies = [Cubie(c.pos, dict(c.stickers)) for c in self.cubies]
        return new

    def state_key(self):
        """Representacion inmutable y comparable del estado completo."""
        return tuple(
            sorted((c.pos, tuple(sorted(c.stickers.items()))) for c in self.cubies)
        )
