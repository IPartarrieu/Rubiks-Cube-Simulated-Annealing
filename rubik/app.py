import matplotlib.pyplot as plt
import streamlit as st

from cube import RubiksCube
from render import render_cube_3d
from sa_solver import solve_sa

st.set_page_config(page_title="Rubik SA", page_icon="🧊", layout="centered")

st.title("Resolviendo el Cubo Rubik con Simulated Annealing")
st.markdown(
    "Mezcla el cubo y deja que un algoritmo de **Simulated Annealing** "
    "intente resolverlo, siguiendo el método de "
    "[Saeidi (2018)](https://doi.org/10.5815/ijeme.2018.01.01): la fitness "
    "es el número de piezas fuera de lugar, y en cada paso se prueba un "
    "movimiento al azar entre los 18 posibles, aceptándolo si mejora o, "
    "si no, con una probabilidad que baja a medida que el sistema se "
    "'enfría'."
)

if "cube" not in st.session_state:
    st.session_state.cube = RubiksCube()
    st.session_state.last_result = None

with st.sidebar:
    st.header("Mezclar")
    depth = st.slider("Movimientos de mezcla", 1, 20, 5)
    if st.button("🔀 Mezclar cubo"):
        st.session_state.cube = RubiksCube()
        st.session_state.cube.scramble(depth)
        st.session_state.last_result = None

    if st.button("🔄 Reiniciar (cubo resuelto)"):
        st.session_state.cube = RubiksCube()
        st.session_state.last_result = None

    st.header("Resolver")
    presupuesto = st.select_slider(
        "Presupuesto de cómputo",
        options=["Rápido", "Medio", "Largo"],
        value="Medio",
    )
    max_iters = {"Rápido": 50_000, "Medio": 150_000, "Largo": 400_000}[presupuesto]

    with st.expander("Parámetros avanzados de SA"):
        t0 = st.slider("Temperatura inicial (T0)", 0.5, 20.0, 3.0, 0.5)
        alpha = st.slider("Tasa de enfriamiento (α)", 0.005, 0.10, 0.02, 0.005)
        iters_per_temp = st.slider("Iteraciones por temperatura", 100, 1000, 400, 50)

    resolver = st.button("🧠 Resolver con SA", type="primary")

if resolver:
    with st.spinner("Buscando la solución..."):
        result = solve_sa(
            st.session_state.cube,
            t0=t0,
            alpha=alpha,
            iters_per_temp=iters_per_temp,
            max_total_iters=max_iters,
        )
    st.session_state.cube = result["cube"]
    st.session_state.last_result = result

cube = st.session_state.cube
fitness = cube.fitness()

col1, col2 = st.columns(2)
col1.metric("Piezas mal ubicadas", f"{fitness} / 48")
col2.metric("Estado", "¡Resuelto! 🎉" if fitness == 0 else "Sin resolver")

fig = render_cube_3d(cube)
st.pyplot(fig)
plt.close(fig)

result = st.session_state.last_result
if result is not None:
    st.markdown(
        f"**Último intento:** {len(result['moves'])} movimientos aceptados, "
        f"{result['total_iters']:,} vecinos evaluados — "
        + ("cubo resuelto." if result["solved"] else "no se resolvió del todo, puedes apretar 'Resolver con SA' de nuevo para seguir intentando desde acá.")
    )

    fig2, ax = plt.subplots(figsize=(7, 2.5))
    ax.plot(result["history"], color="#c0392b", lw=0.8)
    ax.set_xlabel("Movimientos aceptados")
    ax.set_ylabel("Fitness")
    ax.set_title("Convergencia del SA")
    ax.grid(alpha=0.3)
    st.pyplot(fig2)
    plt.close(fig2)

with st.expander("¿Cómo funciona?"):
    st.markdown(
        """
El cubo se modela como 26 piezas ubicadas en coordenadas 3D; cada uno
de los 18 movimientos (girar una de las 6 caras 90°, -90° o 180°) rota
geométricamente la capa correspondiente. La fitness cuenta cuántos
"stickers" no están en la cara que les corresponde (0 = resuelto).

El paper original ([Saeidi 2018](https://doi.org/10.5815/ijeme.2018.01.01))
reporta una temperatura inicial de 1000-5000, pero calibrando contra
este motor esos valores resultan demasiado altos frente a la escala
real de los saltos de fitness (~10-12), haciendo que el algoritmo
camine casi al azar. Los valores por defecto acá se recalibraron para
que la búsqueda sea selectiva desde el principio — ver
[`sa_solver.py`](https://github.com/IPartarrieu/Rubiks-Cube-Simulated-Annealing/blob/main/rubik/sa_solver.py).

Ojo: Simulated Annealing con esta fitness es un método débil para el
cubo (el propio paper reporta hasta 358 movimientos necesarios) —
mezclas profundas pueden no resolverse del todo dentro del
presupuesto de cómputo. El motor está verificado con tests
algebraicos (incluyendo la identidad clásica de teoría de grupos
`(R U R' U')⁶ = identidad`) en
[`tests/test_cube.py`](https://github.com/IPartarrieu/Rubiks-Cube-Simulated-Annealing/blob/main/rubik/tests/test_cube.py).
"""
    )
