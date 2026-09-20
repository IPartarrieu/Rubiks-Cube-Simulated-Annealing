# Rubiks-Cube-Simulated-Annealing

Cubo de Rubik en 3D, mezclable a mano, resuelto por un algoritmo de **Simulated Annealing** — siguiendo el método de [Saeidi (2018), "Solving the Rubik's Cube using Simulated Annealing and Genetic Algorithm"](https://doi.org/10.5815/ijeme.2018.01.01).

🔗 **Demo en vivo:** [rubiks-cube-simulated-annealin-swrgpzutprn7ysd3gyhu7p.streamlit.app](https://rubiks-cube-simulated-annealin-swrgpzutprn7ysd3gyhu7p.streamlit.app/)

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://rubiks-cube-simulated-annealin-swrgpzutprn7ysd3gyhu7p.streamlit.app/)

## Qué hace

Mezclá el cubo con un número de movimientos al azar y apretá "Resolver con SA": el algoritmo prueba movimientos aleatorios entre los 18 posibles (girar cualquiera de las 6 caras 90°, -90° o 180°), aceptando cada uno si mejora la solución o, si no, con una probabilidad que baja a medida que el sistema se "enfría". Se puede volver a apretar "Resolver" para seguir intentando desde donde quedó.

## Cómo está construido

- **`rubik/cube.py`** — motor del cubo: en vez de tablas de permutación escritas a mano, cada movimiento rota geométricamente las piezas de una capa en coordenadas 3D. Verificado con tests algebraicos, incluida la identidad clásica de teoría de grupos `(R U R' U')⁶ = identidad`.
- **`rubik/sa_solver.py`** — Simulated Annealing fiel al pseudocódigo del paper, con la fitness corregida (el paper define fitness = piezas *fuera* de lugar en el texto, pero la Ec. 2-3 la define al revés — un error que el propio documento reconoce) y la temperatura inicial recalibrada empíricamente (el valor del paper, 1000-5000, resulta demasiado alto frente a la escala real de los saltos de fitness en este cubo).
- **`rubik/render.py`** — render 3D con matplotlib, compartiendo la misma estructura de piezas que el motor.
- **`rubik/app.py`** — interfaz interactiva en Streamlit.

**Nota honesta:** Simulated Annealing con esta función de fitness (número de piezas mal ubicadas) es un método relativamente débil para el cubo — el propio paper reporta necesitar hasta 358 movimientos para resolverlo, y mezclas profundas pueden no resolverse del todo dentro del presupuesto de cómputo de la demo. Esto no es un bug: es una limitación conocida del método, documentada en la interfaz.

## Correr en local

```bash
cd rubik
pip install -r requirements.txt
streamlit run app.py
```

## Tests

```bash
cd rubik
python tests/test_cube.py
python tests/test_sa_solver.py
python tests/test_render.py
```

