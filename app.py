import streamlit as st

st.set_page_config(
    page_title="Física para Ciencias de la Computación",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Menú lateral ──────────────────────────────────────────────────────────────
st.sidebar.title("🔬 Física — Simulaciones")
st.sidebar.markdown("---")
if "ir_a" in st.session_state:
    st.session_state["seccion"] = st.session_state.pop("ir_a")
if "seccion" not in st.session_state:
    st.session_state["seccion"] = "🏠 Inicio"

seccion = st.sidebar.radio(
    "Selecciona la entrega:",
    [
        "🏠 Inicio",
        "📐 DDA — Fuerza hidráulica",
        "⚡ DDB — Campo eléctrico",
        "〰️ DDC — Ondas estacionarias",
        "🌅 DDD — Espejismo óptico",
    ],
    index=[
        "🏠 Inicio",
        "📐 DDA — Fuerza hidráulica",
        "⚡ DDB — Campo eléctrico",
        "〰️ DDC — Ondas estacionarias",
        "🌅 DDD — Espejismo óptico",
    ].index(st.session_state["seccion"]),
    key="seccion",
)
st.sidebar.markdown("---")
st.sidebar.caption("Física para Ciencias de la Computación")

# ── Enrutamiento ──────────────────────────────────────────────────────────────
if seccion == "🏠 Inicio":
    from modulos import inicio
    inicio.mostrar()
elif seccion == "📐 DDA — Fuerza hidráulica":
    from modulos import dda
    dda.mostrar()
elif seccion == "⚡ DDB — Campo eléctrico":
    from modulos import ddb
    ddb.mostrar()
elif seccion == "〰️ DDC — Ondas estacionarias":
    from modulos import ddc
    ddc.mostrar()
elif seccion == "🌅 DDD — Espejismo óptico":
    from modulos import ddd
    ddd.mostrar()
