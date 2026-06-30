import numpy as np
import matplotlib.pyplot as plt
from math import pi
from matplotlib.ticker import FuncFormatter
import streamlit as st
import streamlit.components.v1 as components
# =========================================================
# FÍSICA PARA CIENCIAS DE LA COMPUTACIÓN
# DDB - Parte 1
# Campo eléctrico de una barra infinita cargada
# Método numérico: Regla del trapecio
# =========================================================
# =========================================================
# CONSTANTES FÍSICAS
# =========================================================
epsilon0 = 8.85e-12
k = 9.00e9
# =========================================================
# PARÁMETROS DEL PROBLEMA
# =========================================================
lam = 40.0e-9
# Límite superior de integración.
# Se aproxima la barra infinita como:
# integral de -∞ a +∞ ≈ 2 integral de 0 a L
L = 100.0 # m representa la longitud de la barra usada para aproximar la barra infinita
dy = 0.0100 # Paso de integración (intervalo entre puntos en y)
N = int(L / dy) # Número de intervalos para la integración
x_values = np.linspace(2.00, 80.0, 200) # Valores de x desde 2.00 m hasta 80.0 m, con 200 puntos
# =========================================================
# FORMATO CON TRES CIFRAS SIGNIFICATIVAS Y COMA DECIMAL
# =========================================================
def formato_3_cifras(valor, posicion=None):
    """
    Muestra los valores de los ejes con tres cifras significativas
    y coma decimal.
    """
    if valor < 10:
        texto = f"{valor:.2f}"
    elif valor < 100:
        texto = f"{valor:.1f}"
    else:
        texto = f"{valor:.0f}"
    return texto.replace(".", ",")
def formato_tabla(valor):
    """
    Formato para la tabla de resultados con tres cifras significativas
    y coma decimal.
    """
    if valor < 10:
        texto = f"{valor:.2f}"
    elif valor < 100:
        texto = f"{valor:.1f}"
    else:
        texto = f"{valor:.0f}"
    return texto.replace(".", ",")
def mostrar():
    # =========================================================
    # MÉTODO NUMÉRICO DEL TRAPECIO
    # =========================================================
    E_numerico = []
    E_teorico = []
    for x in x_values:
        y = np.linspace(0, L, N + 1) # Valores de y desde 0 hasta L, con N+1 puntos (incluyendo el límite superior)
        f = (2 * k * lam * x) / ((y**2 + x**2)**(3/2)) # Función a integrar para el campo eléctrico, considerando la simetría de la barra
        integral = 0
        for i in range(N):
            area_trapecio = ((f[i] + f[i + 1]) / 2) * dy # Área del trapecio para el intervalo [y[i], y[i+1]]
            integral += area_trapecio
        E_numerico.append(integral)
        E_teo = lam / (2 * pi * epsilon0 * x) # Campo eléctrico teórico para una barra infinita cargada a distancia x
        E_teorico.append(E_teo)
    E_numerico = np.array(E_numerico)
    E_teorico = np.array(E_teorico)
    # =========================================================
    # ERROR PORCENTUAL
    # =========================================================
    error = np.abs((E_teorico - E_numerico) / E_teorico) * 100 # Error porcentual entre el método numérico y el modelo teórico
    # =========================================================
    # TABLA DE RESULTADOS PARA CONSOLA
    # =========================================================
    print("\n======================================================")
    print("                TABLA DE RESULTADOS")
    print("======================================================")
    print(f"{'x (m)':<12}{'E Numérico (N/C)':<22}{'E Teórico (N/C)':<22}{'Error %':<12}")
    for i in range(0, len(x_values), 20):
        print(
            f"{formato_tabla(x_values[i]):<12}"
            f"{formato_tabla(E_numerico[i]):<22}"
            f"{formato_tabla(E_teorico[i]):<22}"
            f"{formato_tabla(error[i]):<12}"
        )
    # =========================================================
    # SLIDER INTERACTIVO DE POSICIÓN x
    # =========================================================
    x_sel = st.slider(
        "Distancia a la barra x (m)",
        min_value=float(x_values.min()),
        max_value=float(x_values.max()),
        value=float(x_values.min()),
        step=0.5
    )
    idx_sel = int(np.argmin(np.abs(x_values - x_sel)))
    col1, col2, col3 = st.columns(3)
    col1.metric("E numérico (N/C)", formato_tabla(E_numerico[idx_sel]))
    col2.metric("E teórico (N/C)",  formato_tabla(E_teorico[idx_sel]))
    col3.metric("Error (%)",        f"{error[idx_sel]:.4f}")
    # =========================================================
    # GRÁFICAS MATPLOTLIB — una debajo de la otra
    # =========================================================
    # ---------------------------------------------------------
    # Gráfica 1: Método numérico
    # ---------------------------------------------------------
    fig1, ax1 = plt.subplots(figsize=(13, 5))
    ax1.plot(
        x_values,
        E_numerico,
        linewidth=2.5,
        label="Método numérico: regla del trapecio"
    )
    ax1.axvline(x_sel, color="orange", linestyle="--", linewidth=2,
                label=f"x = {formato_tabla(x_sel)} m")
    ax1.set_title("Gráfico campo eléctrico vs posición (Método numérico)",
                  fontsize=13, fontweight="bold", pad=8)
    ax1.set_xlabel("Posición x (m)", fontsize=11, labelpad=8)
    ax1.set_ylabel("Campo eléctrico E (N/C)", fontsize=11)
    ax1.grid(True)
    ax1.legend(loc="best", fontsize=9)
    ax1.xaxis.set_major_formatter(FuncFormatter(formato_3_cifras))
    ax1.yaxis.set_major_formatter(FuncFormatter(formato_3_cifras))
    st.pyplot(fig1)
    plt.close(fig1)
    # ---------------------------------------------------------
    # Gráfica 2: Modelo teórico
    # ---------------------------------------------------------
    fig2, ax2 = plt.subplots(figsize=(13, 5))
    ax2.plot(
        x_values,
        E_teorico,
        linewidth=2.5,
        label="Modelo teórico: barra infinita"
    )
    ax2.axvline(x_sel, color="orange", linestyle="--", linewidth=2,
                label=f"x = {formato_tabla(x_sel)} m")
    ax2.set_title("Gráfico campo eléctrico vs posición (Modelo teórico)",
                  fontsize=13, fontweight="bold", pad=8)
    ax2.set_xlabel("Posición x (m)", fontsize=11, labelpad=8)
    ax2.set_ylabel("Campo eléctrico E (N/C)", fontsize=11)
    ax2.grid(True)
    ax2.legend(loc="best", fontsize=9)
    ax2.xaxis.set_major_formatter(FuncFormatter(formato_3_cifras))
    ax2.yaxis.set_major_formatter(FuncFormatter(formato_3_cifras))
    st.pyplot(fig2)
    plt.close(fig2)
    # ---------------------------------------------------------
    # Gráfica 3: Comparación numérico vs teórico
    # ---------------------------------------------------------
    fig3, ax3 = plt.subplots(figsize=(13, 5))
    ax3.plot(x_values, E_numerico, linewidth=2.5,
             label="Método numérico: regla del trapecio")
    ax3.plot(x_values, E_teorico, linestyle="--", linewidth=2.5,
             label="Modelo teórico: barra infinita")
    ax3.axvline(x_sel, color="orange", linestyle="--", linewidth=2,
                label=f"x = {formato_tabla(x_sel)} m")
    ax3.set_title("Gráfico campo eléctrico vs posición (Método numérico y modelo teórico)",
                  fontsize=13, fontweight="bold", pad=8)
    ax3.set_xlabel("Posición x (m)", fontsize=11, labelpad=8)
    ax3.set_ylabel("Campo eléctrico E (N/C)", fontsize=11)
    ax3.grid(True)
    ax3.legend(loc="best", fontsize=9)
    ax3.xaxis.set_major_formatter(FuncFormatter(formato_3_cifras))
    ax3.yaxis.set_major_formatter(FuncFormatter(formato_3_cifras))
    st.pyplot(fig3)
    plt.close(fig3)
    # ---------------------------------------------------------
    # Gráfica 4: Trapecios
    # ---------------------------------------------------------
    fig4, ax4 = plt.subplots(figsize=(13, 5))
    # Valor fijo de x para mostrar cómo se aplica la regla del trapecio
    x_muestra = 2.00
    # Intervalo mostrado para la variable de integración y
    L_muestra = 20.0
    # Paso visual para los trapecios.
    # Se usa un paso grande solo para que los trapecios se distingan.
    dy_trapecio = 0.1
    # Puntos finos para dibujar la función suavemente
    y_suave = np.linspace(0, L_muestra, 1000)
    f_suave = (
        2 * k * lam * x_muestra
    ) / ((y_suave**2 + x_muestra**2)**(3/2))
    # Puntos gruesos para construir los trapecios
    y_trap = np.arange(0, L_muestra + dy_trapecio, dy_trapecio)
    f_trap = (
        2 * k * lam * x_muestra
    ) / ((y_trap**2 + x_muestra**2)**(3/2))
    # Dibujar trapecios sin alterar la curva real
    for i in range(len(y_trap) - 1):
        # Vértices del trapecio:
        # (y_i, 0), (y_i, f_i), (y_{i+1}, f_{i+1}), (y_{i+1}, 0)
        xs = [y_trap[i], y_trap[i], y_trap[i + 1], y_trap[i + 1]]
        ys = [0, f_trap[i], f_trap[i + 1], 0]
        ax4.fill(xs, ys, alpha=0.22, edgecolor="red", linewidth=1.2,
                 label="Trapecios de integración" if i == 0 else None)
        # Líneas verticales rojas, como en el esquema del enunciado
        ax4.plot([y_trap[i], y_trap[i]], [0, f_trap[i]],
                 color="red", linewidth=1)
    # Última línea vertical
    ax4.plot([y_trap[-1], y_trap[-1]], [0, f_trap[-1]],
             color="red", linewidth=1)
    # Dibujar la función real encima de los trapecios
    ax4.plot(y_suave, f_suave, linewidth=3,
             label="Integrando del campo eléctrico")
    ax4.set_title(
        "Representación de la regla del trapecio aplicada al integrando del campo eléctrico",
        fontsize=13, fontweight="bold", pad=8)
    ax4.set_xlabel("Posición sobre la barra, y (m)", fontsize=11, labelpad=8)
    ax4.set_ylabel("Integrando f(y) (N/C·m)", fontsize=11)
    ax4.grid(True)
    ax4.legend(loc="best", fontsize=9)
    ax4.xaxis.set_major_formatter(FuncFormatter(formato_3_cifras))
    ax4.yaxis.set_major_formatter(FuncFormatter(formato_3_cifras))
    st.pyplot(fig4)
    plt.close(fig4)
    # =========================================================
    # TABLA EN STREAMLIT
    # =========================================================
    st.markdown("### Tabla de resultados")
    indices_tabla = np.linspace(0, len(x_values) - 1, 6, dtype=int)
    datos = {
        "x (m)":            [formato_tabla(x_values[i]) for i in indices_tabla],
        "E numérico (N/C)": [formato_tabla(E_numerico[i]) for i in indices_tabla],
        "E teórico (N/C)":  [formato_tabla(E_teorico[i]) for i in indices_tabla],
        "Error (%)":        [formato_tabla(error[i]) for i in indices_tabla],
    }
    import pandas as pd
    st.dataframe(pd.DataFrame(datos), use_container_width=True)

    # =========================================================
    # ANIMACIÓN: barra cargada con partículas que salen radialmente
    # Las partículas salen más rápido y más juntas cerca de la barra
    # (campo fuerte) y más lento y espaciadas lejos (campo débil).
    # El slider de x mueve la línea de medición en tiempo real.
    # =========================================================
    E_en_x = float(lam / (2 * pi * epsilon0 * x_sel))
    E_max   = float(lam / (2 * pi * epsilon0 * x_values.min()))
    html_barra = f"""
<canvas id="cv" width="700" height="420"
        style="background:#0a0a1a;border-radius:10px;display:block;margin:auto;">
</canvas>
<script>
const canvas = document.getElementById("cv");
const ctx    = canvas.getContext("2d");
const W = canvas.width, H = canvas.height;
const CX = W * 0.18;          // centro x de la barra
const CY = H / 2;             // centro y
const x_sel  = {x_sel};       // distancia seleccionada (m)
const E_val  = {E_en_x};      // E en ese punto (N/C)
const E_max  = {E_max};       // E máximo (para normalizar)
const lam_js = {lam};
const k_js   = {k};
const eps0   = {epsilon0};
const pi     = Math.PI;
// Escala: cuántos píxeles por metro
const PX_POR_M = (W - CX - 30) / {float(x_values.max())};
// ── Partículas ──────────────────────────────────────────
const N_PART = 60;
let particulas = [];
function crearParticula() {{
    // Ángulo aleatorio (solo lado derecho, campo radial hacia afuera)
    const ang = (Math.random() - 0.5) * Math.PI;
    // Velocidad proporcional al campo en esa distancia angular inicial
    const vel_base = 1.5 + 5.0 * (E_val / E_max);
    return {{
        x: CX,
        y: CY,
        ang: ang,
        vel: vel_base * (0.7 + 0.6 * Math.random()),
        vida: 0,
        vida_max: 80 + Math.random() * 60
    }};
}}
for (let i = 0; i < N_PART; i++) {{
    let p = crearParticula();
    // Arrancar en posiciones distribuidas para que no salgan todas a la vez
    p.vida = Math.random() * p.vida_max;
    particulas.push(p);
}}
// ── Loop principal ───────────────────────────────────────
function dibujar() {{
    ctx.clearRect(0, 0, W, H);
    // Fondo con gradiente radial (campo más fuerte cerca de la barra)
    const grd = ctx.createRadialGradient(CX, CY, 5, CX, CY, W * 0.8);
    grd.addColorStop(0,   "rgba(255,200,50,0.18)");
    grd.addColorStop(0.3, "rgba(80,120,255,0.08)");
    grd.addColorStop(1,   "rgba(0,0,0,0)");
    ctx.fillStyle = grd;
    ctx.fillRect(0, 0, W, H);
    // ── Barra cargada (vertical, lado izquierdo) ──────────
    const grad_barra = ctx.createLinearGradient(CX - 8, 0, CX + 8, 0);
    grad_barra.addColorStop(0, "#ff8800");
    grad_barra.addColorStop(0.5, "#ffee44");
    grad_barra.addColorStop(1, "#ff8800");
    ctx.fillStyle = grad_barra;
    ctx.fillRect(CX - 6, 30, 12, H - 60);
    ctx.strokeStyle = "#fff";
    ctx.lineWidth = 1;
    ctx.strokeRect(CX - 6, 30, 12, H - 60);
    // Etiqueta barra
    ctx.fillStyle = "#ffee44";
    ctx.font = "bold 13px Arial";
    ctx.fillText("Barra", CX - 22, 22);
    ctx.fillText("+λ", CX - 10, H - 10);
    // ── Línea de medición en x_sel ────────────────────────
    const px_x = CX + x_sel * PX_POR_M;
    ctx.strokeStyle = "rgba(100,220,255,0.85)";
    ctx.lineWidth   = 2;
    ctx.setLineDash([6, 4]);
    ctx.beginPath();
    ctx.moveTo(px_x, 20);
    ctx.lineTo(px_x, H - 20);
    ctx.stroke();
    ctx.setLineDash([]);
    // Etiqueta x_sel
    ctx.fillStyle = "#64dcff";
    ctx.font = "12px Arial";
    ctx.fillText("x = " + x_sel.toFixed(1) + " m", px_x + 4, 32);
    // Valor E en esa línea
    const E_str = E_val > 1000
        ? (E_val / 1000).toFixed(1) + " kN/C"
        : E_val.toFixed(1) + " N/C";
    ctx.fillStyle = "#ffdd55";
    ctx.font = "bold 12px Arial";
    ctx.fillText("E = " + E_str, px_x + 4, 50);
    // ── Partículas (cargas positivas que salen radialmente) ──
    for (let p of particulas) {{
        p.vida += 1;
        if (p.vida > p.vida_max) {{
            // Reiniciar
            Object.assign(p, crearParticula());
        }}
        const t      = p.vida / p.vida_max;
        const dist   = p.vel * p.vida;          // píxeles desde la barra
        const px     = CX + dist * Math.cos(p.ang);
        const py     = CY + dist * Math.sin(p.ang);
        const alpha  = 1 - t;                  // desvanece al alejarse
        const radio  = 3 + 2 * (1 - t);
        // Color: amarillo cerca, azul lejos (campo débil)
        const r = Math.floor(255 * (1 - t * 0.6));
        const g = Math.floor(200 * (1 - t));
        const b = Math.floor(80  + 175 * t);
        ctx.beginPath();
        ctx.arc(px, py, radio, 0, 2 * Math.PI);
        ctx.fillStyle = `rgba(${{r}},${{g}},${{b}},${{alpha}})`;
        ctx.fill();
        // "+" en la partícula
        ctx.fillStyle = `rgba(255,255,255,${{alpha * 0.9}})`;
        ctx.font = "bold 9px Arial";
        ctx.fillText("+", px - 3, py + 3);
    }}
    // ── Líneas de campo radiales (fijas, estilo libro de texto) ──
    const N_LINEAS = 8;
    for (let i = 0; i < N_LINEAS; i++) {{
        const ang = -Math.PI/2 + (i / N_LINEAS) * Math.PI;
        ctx.strokeStyle = "rgba(255,180,0,0.18)";
        ctx.lineWidth   = 1;
        ctx.beginPath();
        ctx.moveTo(CX + 8 * Math.cos(ang), CY + 8 * Math.sin(ang));
        ctx.lineTo(CX + (W - CX - 20) * Math.cos(ang),
                   CY + (W - CX - 20) * Math.sin(ang));
        ctx.stroke();
    }}
    // ── Panel de datos ────────────────────────────────────
    ctx.fillStyle   = "rgba(0,0,0,0.65)";
    ctx.fillRect(W - 215, 8, 205, 90);
    ctx.strokeStyle = "rgba(255,255,255,0.25)";
    ctx.lineWidth   = 1;
    ctx.strokeRect(W - 215, 8, 205, 90);
    ctx.fillStyle = "white";
    ctx.font = "bold 12px Arial";
    ctx.fillText("📊 Parámetros", W - 205, 28);
    ctx.font = "12px Arial";
    ctx.fillStyle = "#aef";
    ctx.fillText("λ = 40,0 × 10⁻⁹ C/m", W - 205, 48);
    ctx.fillStyle = "#ffa";
    ctx.fillText("x = " + x_sel.toFixed(1) + " m", W - 205, 65);
    ctx.fillStyle = "#aff";
    ctx.fillText("E = " + E_str, W - 205, 82);
    requestAnimationFrame(dibujar);
}}
dibujar();
</script>
"""
    st.markdown("### Visualización del campo eléctrico de la barra")
    st.caption("Las partículas representan cargas positivas empujadas por el campo. "
               "Cerca de la barra salen más rápido (campo fuerte). "
               "Mové el slider para ver cómo cambia E con la distancia.")
    components.html(html_barra, height=440)
    # =========================================================
    # ANÁLISIS
    # =========================================================
    print("\n======================================================")
    print("                     ANÁLISIS")
    print("======================================================")
    print("""
1. El campo eléctrico disminuye al aumentar la distancia x, 
   lo cual concuerda con el modelo teórico E = λ/(2πε0x).
2. El método numérico aproxima correctamente el comportamiento
   del modelo teórico, ya que ambas gráficas presentan una tendencia
   decreciente de tipo inversamente proporcional.
3. Las diferencias entre el método numérico y el modelo teórico se deben
   a la discretización de la integral mediante la regla del trapecio y a que
   la barra infinita se aproxima usando un límite finito L = 100,0 m.
4. Para valores pequeños de x, la aproximación numérica es más cercana
   al modelo teórico. Para valores grandes de x, el error puede aumentar
   porque la longitud finita usada en la integración representa peor
   a una barra infinita.
5. Si se disminuye Δy o se aumenta el valor de L, la aproximación numérica
   mejora, aunque también aumenta el costo computacional.
""")