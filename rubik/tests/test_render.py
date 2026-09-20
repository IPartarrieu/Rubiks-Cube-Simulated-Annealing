import random
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cube import RubiksCube  # noqa: E402
from render import render_cube_3d  # noqa: E402

# El render no debe fallar para un cubo resuelto ni para uno mezclado,
# y debe producir al menos algunos poligonos visibles (culling no
# deberia dejar la escena vacia).
for depth in [0, 5, 15]:
    c = RubiksCube()
    if depth:
        c.scramble(depth, rng=random.Random(0))
    fig = render_cube_3d(c)
    ax = fig.axes[0]
    n_collections = len(ax.collections)
    assert n_collections > 0, f"no se dibujo ningun sticker (depth={depth})"
    assert n_collections <= 27, f"deberian verse a lo sumo 3 caras (27 stickers): {n_collections}"

print("Render OK: se genera la figura y hay stickers visibles sin excepciones")
