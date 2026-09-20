import random
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cube import ALL_MOVE_NAMES, MOVES, RubiksCube  # noqa: E402


def inverse(move):
    if move.endswith("'"):
        return move[0]
    if move.endswith("2"):
        return move
    return move + "'"


# 1) Cubo resuelto tiene fitness 0
c = RubiksCube()
assert c.is_solved()
assert c.fitness() == 0

# 2) Cada movimiento base aplicado 4 veces vuelve al cubo resuelto
for base in MOVES:
    c = RubiksCube()
    for _ in range(4):
        c.apply_move(base)
    assert c.is_solved(), f"{base}^4 no vuelve al cubo resuelto"

# 3) Un solo movimiento desarma el cubo
for base in MOVES:
    c = RubiksCube()
    c.apply_move(base)
    assert not c.is_solved(), f"{base} no cambio el cubo"

# 4) Un movimiento y su inverso se cancelan
for base in MOVES:
    c = RubiksCube()
    c.apply_move(base)
    c.apply_move(inverse(base))
    assert c.is_solved()

# 5) X2 equivale a aplicar X dos veces
for base in MOVES:
    c1 = RubiksCube()
    c1.apply_move(base + "2")
    c2 = RubiksCube()
    c2.apply_move(base)
    c2.apply_move(base)
    assert c1.state_key() == c2.state_key()

# 6) Caras opuestas conmutan (no comparten piezas)
for a, b in [("R", "L"), ("U", "D"), ("F", "B")]:
    c1 = RubiksCube()
    c1.apply_move(a)
    c1.apply_move(b)
    c2 = RubiksCube()
    c2.apply_move(b)
    c2.apply_move(a)
    assert c1.state_key() == c2.state_key()

# 7) El "sexy move" (R U R' U') tiene orden 6 (identidad clasica de teoria de grupos)
c = RubiksCube()
for _ in range(6):
    for m in ["R", "U", "R'", "U'"]:
        c.apply_move(m)
assert c.is_solved(), "R U R' U' repetido 6 veces deberia resolver el cubo"

# 8) Conservacion de color: cada color aparece siempre exactamente 9 veces
c = RubiksCube()
rng = random.Random(0)
for _ in range(300):
    c.apply_move(rng.choice(ALL_MOVE_NAMES))
counts = Counter()
for cb in c.cubies:
    for color in cb.stickers.values():
        counts[color] += 1
assert all(v == 9 for v in counts.values()), counts
assert set(counts) == set("RLUDFB")

# 9) Mezclar y deshacer la secuencia inversa resuelve el cubo
c = RubiksCube()
seq = c.scramble(25, rng=random.Random(1))
for m in reversed(seq):
    c.apply_move(inverse(m))
assert c.is_solved()

# 10) fitness() nunca supera 48 (6 centros siempre correctos, 54-6=48)
c = RubiksCube()
c.scramble(50, rng=random.Random(2))
assert 0 <= c.fitness() <= 48

print("Todas las verificaciones del motor del cubo pasaron OK")
