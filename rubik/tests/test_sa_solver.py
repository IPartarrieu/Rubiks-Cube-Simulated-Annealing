import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cube import RubiksCube  # noqa: E402
from sa_solver import solve_sa  # noqa: E402

# 1) Un cubo ya resuelto: SA debe devolver solved=True de inmediato
c = RubiksCube()
result = solve_sa(c, seed=0)
assert result["solved"]
assert result["fitness"] == 0
assert result["moves"] == []

# 2) Aplicar los movimientos devueltos al cubo original reproduce el resultado
c = RubiksCube()
c.scramble(4, rng=random.Random(1))
result = solve_sa(c.copy(), t0=500, alpha=0.03, iters_per_temp=200, seed=1)
replay = c.copy()
for m in result["moves"]:
    replay.apply_move(m)
assert replay.state_key() == result["cube"].state_key()
assert replay.fitness() == result["fitness"]

# 3) Calibracion empirica: tasa de exito y tiempo segun profundidad de mezcla
print("profundidad | resuelto | fitness_final | iters | tiempo(s)")
for depth in [1, 2, 3, 4, 5, 6, 8, 10]:
    times, solved_count = [], 0
    for trial in range(5):
        c = RubiksCube()
        c.scramble(depth, rng=random.Random(100 + trial))
        t_start = time.time()
        result = solve_sa(
            c, t0=500, alpha=0.03, iters_per_temp=200,
            max_total_iters=60_000, seed=trial,
        )
        elapsed = time.time() - t_start
        times.append(elapsed)
        solved_count += result["solved"]
    print(
        f"{depth:11d} | {solved_count}/5      | "
        f"~{result['fitness']:2d}          | {result['total_iters']:6d} | "
        f"{sum(times)/len(times):.2f}"
    )

print("Todas las verificaciones del solver SA pasaron OK")
