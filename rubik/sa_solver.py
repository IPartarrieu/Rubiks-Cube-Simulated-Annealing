"""Simulated Annealing para resolver el Cubo de Rubik.

Sigue el pseudocodigo de Saeidi (2018) "Solving the Rubik's Cube using
Simulated Annealing and Genetic Algorithm": en cada temperatura se
prueban `iters_per_temp` vecinos (aplicar un movimiento aleatorio de
los 18 posibles); se acepta si mejora la fitness o, si no, con
probabilidad exp(-delta/T). La temperatura baja geometricamente
(T *= 1-alpha) hasta un minimo o hasta resolver el cubo.

Nota sobre el paper original: el texto define la fitness como el
numero de piezas FUERA de su posicion correcta, pero la Ec. (2)-(3)
del paper cuenta al reves (piezas SI correctas), un error que el
propio documento reconoce. Aqui se implementa la version correcta:
fitness = piezas fuera de lugar (0 = cubo resuelto).

Nota sobre la temperatura inicial: el paper reporta T0=5000 (seccion
2.3) o T0=1000 (seccion 3.1), inconsistentes entre si. Calibrando
empiricamente contra este motor, esos valores son demasiado altos
frente a la escala real de los saltos de fitness entre vecinos (~10-12
en este cubo de 54 stickers): con T0=1000, incluso un movimiento que
empeora la solucion en 10 tiene ~98% de probabilidad de aceptarse
(exp(-10/1000)), por lo que el algoritmo camina practicamente al azar
y nunca converge. Los valores por defecto aqui (T0=3, alpha=0.02) se
ajustaron para que la aceptacion de movimientos sea selectiva desde el
principio.
"""

import math
import random

from cube import ALL_MOVE_NAMES


def solve_sa(
    cube,
    t0=3.0,
    alpha=0.02,
    iters_per_temp=400,
    t_min=1e-3,
    max_total_iters=150_000,
    seed=None,
):
    rng = random.Random(seed)
    current = cube.copy()
    current_fitness = current.fitness()

    best = current.copy()
    best_fitness = current_fitness
    move_sequence = []
    best_move_count = 0
    history = [current_fitness]

    T = t0
    total_iters = 0
    while T > t_min and best_fitness > 0 and total_iters < max_total_iters:
        for _ in range(iters_per_temp):
            total_iters += 1
            move = rng.choice(ALL_MOVE_NAMES)
            neighbor = current.copy()
            neighbor.apply_move(move)
            neighbor_fitness = neighbor.fitness()
            delta = neighbor_fitness - current_fitness

            accept = delta <= 0 or rng.random() < math.exp(-delta / T)
            if accept:
                current, current_fitness = neighbor, neighbor_fitness
                move_sequence.append(move)
                history.append(current_fitness)
                if current_fitness < best_fitness:
                    best_fitness = current_fitness
                    best = current.copy()
                    best_move_count = len(move_sequence)

            if best_fitness == 0 or total_iters >= max_total_iters:
                break
        T *= 1 - alpha

    return {
        "cube": best,
        "moves": move_sequence[:best_move_count],
        "fitness": best_fitness,
        "solved": best_fitness == 0,
        "history": history,
        "total_iters": total_iters,
    }
