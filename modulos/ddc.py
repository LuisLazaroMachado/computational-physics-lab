import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy.signal import find_peaks
import math
import streamlit as st
import streamlit.components.v1 as components

# =========================================================
# FÍSICA PARA CIENCIAS DE LA COMPUTACIÓN
# DDC - Parte 1
# Ondas estacionarias en una cuerda
# Método numérico: Diferencias finitas de 2do orden
# =========================================================


def tres_cifras_significativas(v, _=None, sig=3):
    if v == 0:
        return "0"
    decimales = sig - 1 - int(math.floor(math.log10(abs(v))))
    decimales = max(0, decimales)
    return f"{v:.{decimales}f}"


def mostrar():
    # =========================================================
    # PARÁMETROS DEL SISTEMA (sin cambios respecto al original)
    # =========================================================
    L = 2.50
    tension = 150
    densidad_lineal = 8.00e-3
    amplitud = 2.00e-2
    n_modo = 7
    dx = 1.00e-2

    # Antinodo de referencia
    x_antinodo_ref = 2 * L * 3 / (n_modo * 4)

    # MAGNITUDES DERIVADAS
    velocidad = np.sqrt(tension / densidad_lineal)
    k_n = n_modo * np.pi / L
    omega = k_n * velocidad
    f_osc = omega / (2 * np.pi)
    T_per = 1.00 / f_osc

    # MALLA ESPACIAL Y TEMPORAL
    dt = 0.90 * dx / velocidad
    # Número de Courant
    a = velocidad * dt / dx
    # Tiempo de estabilización: la onda recorre 100 veces la longitud de la cuerda
    t_estab = 100 * L / velocidad
    # Los 5 instantes de muestreo según la fórmula:
    # t_k = t_estab + (k-1) · T/4   para k = 1,2,3,4,5
    t_muestras = [t_estab + (k - 1) * T_per / 4 for k in range(1, 6)]
    # Tiempo total de simulación
    T_sim = max(t_muestras[-1], t_estab + 3 * T_per)

    nx = round(L / dx) + 1
    x = np.linspace(0, L, nx)
    idx_antinodo = int(round(x_antinodo_ref / dx))
    x_antinodo_real = x[idx_antinodo]

    def desplazamiento_exacto(x_arr, t_val):
        return 2 * amplitud * np.sin(k_n * x_arr) * np.sin(omega * t_val)

    def velocidad_exacta(x_arr, t_val):
        return 2 * amplitud * omega * np.sin(k_n * x_arr) * np.cos(omega * t_val)

    # Condiciones iniciales
    u_prev = desplazamiento_exacto(x, 0.0)               # nivel n = 0  (t = 0)
    u_curr = u_prev + dt * velocidad_exacta(x, 0.0)      # nivel n = 1  (t = Δt)

    perfiles = {}
    t_actual = dt
    instantes_pendientes = sorted(t_muestras)
    idx_muestra = 0
    tiempo_antinodo = []
    amplitud_antinodo = []

    # =========================================================
    # SIMULACIÓN POR DIFERENCIAS FINITAS (idéntica al original)
    # =========================================================
    with st.spinner("Calculando la simulación por diferencias finitas..."):
        while t_actual <= T_sim + dt:
            # Captura de perfiles en los instantes t_k
            if idx_muestra < len(instantes_pendientes):
                t_objetivo = instantes_pendientes[idx_muestra]
                if abs(t_actual - t_objetivo) < dt / 2:
                    perfiles[t_objetivo] = u_curr.copy()
                    idx_muestra += 1

            # Registro del antinodo
            if t_actual >= t_estab and t_actual <= t_estab + 2 * T_per + 10 * dt:
                tiempo_antinodo.append(t_actual)
                amplitud_antinodo.append(u_curr[idx_antinodo])

            # Diferencias finitas de 2do orden
            u_next = np.empty(nx)
            u_next[1:-1] = (
                2 * u_curr[1:-1] - u_prev[1:-1]
                + (a**2) * (u_curr[2:] - 2 * u_curr[1:-1] + u_curr[:-2])
            )
            u_next[0] = 0.0
            u_next[-1] = 0.0

            u_prev = u_curr
            u_curr = u_next
            t_actual += dt

    COLORES = ['#1a6faf', '#c94040', '#2a9d5c', '#e07b20', '#7b52ab']
    ESTILOS = ['-', '--', '-.', ':', (0, (3, 1, 1, 1))]

    t_arr = np.array(tiempo_antinodo)
    y_arr = np.array(amplitud_antinodo)
    t_rel = t_arr - t_estab

    # =========================================================
    # CONDICIÓN DE ESTABILIDAD Y RESULTADOS GENERALES
    # =========================================================
    st.markdown("### Parámetros calculados")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Velocidad de onda v", f"{velocidad:.2f} m/s")
    col2.metric("Frecuencia f", f"{f_osc:.2f} Hz")
    col3.metric("Periodo T", f"{T_per:.6f} s")
    col4.metric(
        "Número de Courant (a)",
        f"{a:.4f}",
        "✓ estable" if a <= 1 else "✗ inestable"
    )

    with st.expander("📋 Ver detalles numéricos de la simulación"):
        st.write(f"**Paso de tiempo (Δt):** {dt:.6f} s")
        st.write(f"**Nodos espaciales (nx):** {nx}")
        st.write(f"**Tiempo de estabilización:** {t_estab:.4f} s")
        st.write(f"**Antinodo de referencia:** x = {x_antinodo_real:.4f} m")
        st.write(f"**Perfiles capturados:** {len(perfiles)}")
        if a <= 1:
            st.success("El esquema cumple la condición de estabilidad de Courant (a ≤ 1).")
        else:
            st.error("El esquema NO cumple la condición de estabilidad de Courant (a > 1).")

    # =========================================================
    # FUNCIONES DE DIBUJO (idénticas en lógica al original,
    # solo adaptadas para recibir el eje 'ax' como parámetro)
    # =========================================================
    def dibujar_perfil(ax, mostrar_antinodo=False):
        for idx, (t_cap, perfil) in enumerate(sorted(perfiles.items())):
            k = idx + 1
            label = f"$t_{k}$ = {t_cap:.5f} s  [+{(k-1)/4:.2f}T]"
            ax.plot(x, perfil,
                    color=COLORES[idx], linestyle=ESTILOS[idx],
                    linewidth=1.8, label=label)

        if mostrar_antinodo:
            ax.axvline(x_antinodo_real,
                       color='black', linewidth=1.4, linestyle='--', alpha=0.7,
                       label=f"Antinodo  $x$ = {x_antinodo_real:.3f} m")

        ax.set_title("Perfil de la cuerda en estado estacionario",
                     fontsize=11, pad=10)
        ax.set_xlabel("Posición a lo largo de la cuerda,  $x$  (m)", fontsize=10)
        ax.set_ylabel("Desplazamiento transversal,  $y$  (m)", fontsize=10)
        ax.axhline(0, color='black', linewidth=0.7)
        ax.set_xlim(0, L)
        ax.set_ylim(-2 * amplitud * 1.25, 2 * amplitud * 1.25)
        ax.xaxis.set_major_locator(ticker.MultipleLocator(L / (2 * n_modo)))
        ax.yaxis.set_major_locator(ticker.MultipleLocator(2 * amplitud * 0.50))
        ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(4))
        ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(4))
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(tres_cifras_significativas))
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(tres_cifras_significativas))
        ax.grid(which='major', linestyle='--', linewidth=0.5, alpha=0.6)
        ax.grid(which='minor', linestyle=':', linewidth=0.3, alpha=0.4)
        ax.legend(
            title=f"Instantes de tiempo:\n$t_{{\\rm estab}}$ = {t_estab:.5f} s",
            title_fontsize=8, fontsize=8,
            loc='upper right', framealpha=0.92, edgecolor='#cccccc',
        )

    def dibujar_amplitud(ax):
        ax.plot(t_rel, y_arr, color='#1a6faf', linewidth=1.4,
                label=f"$x$ = {x_antinodo_real:.3f} m")

        indices_crestas, _ = find_peaks(y_arr)
        num = 1
        for i in indices_crestas:
            ax.scatter(t_rel[i], y_arr[i], color='red', zorder=6, s=60)
            ax.annotate(
                f"t{num} = {t_rel[i]:.8f} s",
                xy=(t_rel[i], y_arr[i]),
                xytext=(-30, -15),
                textcoords='offset points',
                fontsize=8,
                color='red',
            )
            num += 1

        ax.set_title(
            f"Evolución temporal de la amplitud en el antinodo $x$ = {x_antinodo_real:.3f} m",
            fontsize=11, pad=10
        )
        ax.set_xlabel(
            "Tiempo desde el estado estacionario,  $t - t_{\\rm estab}$  (s)",
            fontsize=10
        )
        ax.set_ylabel("Amplitud,  $A$  (m)", fontsize=10)
        ax.set_ylim(-2 * amplitud * 1.25, 2 * amplitud * 1.25)
        ax.yaxis.set_major_locator(ticker.MultipleLocator(2 * amplitud * 0.50))
        ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(4))
        ax.set_xlim(0, 2 * T_per)
        ax.xaxis.set_major_locator(ticker.MultipleLocator(T_per / 4))
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(tres_cifras_significativas))
        ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(4))
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(tres_cifras_significativas))
        ax.grid(which='major', linestyle='--', linewidth=0.5, alpha=0.6)
        ax.grid(which='minor', linestyle=':', linewidth=0.3, alpha=0.4)
        ax.legend(
            title=f"x = {x_antinodo_real:.3f} m",
            title_fontsize=8, fontsize=8,
            loc='upper right', framealpha=0.92, edgecolor='#cccccc',
        )

    # =========================================================
    # SELECTOR DE VISTA (reemplaza los RadioButtons de matplotlib)
    # =========================================================
    st.markdown("### Visualización de resultados")
    vista = st.radio(
        "Selecciona la vista:",
        ["Perfil de onda", "Perfil + antinodo", "Amplitud vs tiempo"],
        horizontal=True
    )

    fig, ax = plt.subplots(figsize=(12, 5.5))
    if vista == "Perfil de onda":
        dibujar_perfil(ax, mostrar_antinodo=False)
    elif vista == "Perfil + antinodo":
        dibujar_perfil(ax, mostrar_antinodo=True)
    else:
        dibujar_amplitud(ax)
    st.pyplot(fig)
    plt.close(fig)

    # =========================================================
    # ANIMACIÓN: cuerda vibrando en tiempo real (HTML5 canvas)
    # Usa la solución analítica exacta ya definida en el código
    # (desplazamiento_exacto) solo con fines visuales/educativos.
    # No reemplaza ni modifica el resultado numérico de arriba.
    # =========================================================
    st.markdown("### 🎻 Animación: la cuerda vibrando")
    st.caption(
        f"El periodo real de oscilación es T ≈ {T_per*1000:.3f} ms — demasiado "
        "rápido para verlo a simple vista. Esta animación lo muestra en cámara "
        "lenta, a una velocidad que podés ajustar, conservando la forma exacta "
        "del modo n = {} (nodos y antinodos en su posición real).".format(n_modo)
    )

    velocidad_anim = st.slider(
        "Velocidad de la animación (periodo visual, en segundos)",
        min_value=0.5, max_value=6.0, value=3.0, step=0.5
    )

    # Posiciones reales de nodos y antinodos del modo n_modo
    nodos_x = [j * L / n_modo for j in range(0, n_modo + 1)]
    antinodos_x = [(2 * j - 1) * L / (2 * n_modo) for j in range(1, n_modo + 1)]
    nodos_js = ", ".join(f"{val:.6f}" for val in nodos_x)
    antinodos_js = ", ".join(f"{val:.6f}" for val in antinodos_x)
    idx_antinodo_resaltado = min(
        range(len(antinodos_x)),
        key=lambda i: abs(antinodos_x[i] - x_antinodo_real)
    )

    html_cuerda = f"""
<canvas id="cv_cuerda" width="700" height="280"
        style="background:#0a0a1a;border-radius:10px;display:block;margin:auto;">
</canvas>
<script>
const canvas = document.getElementById("cv_cuerda");
const ctx    = canvas.getContext("2d");
const W = canvas.width, H = canvas.height;

const L_js       = {L};
const A_js       = {amplitud};
const k_js       = {k_n};
const n_modo_js  = {n_modo};
const T_visual   = {velocidad_anim};   // periodo visual en segundos (no es T real)
const nodos      = [{nodos_js}];
const antinodos  = [{antinodos_js}];
const idx_resaltado = {idx_antinodo_resaltado};

const margen_x = 50;
const margen_y = 40;
const cy = H / 2;
const PX_POR_M = (W - 2 * margen_x) / L_js;
const ESCALA_Y = (H / 2 - margen_y) / (2 * A_js);

function xPix(xm) {{ return margen_x + xm * PX_POR_M; }}
function yPix(ym) {{ return cy - ym * ESCALA_Y; }}

let inicio = null;

function dibujar(timestamp) {{
    if (inicio === null) inicio = timestamp;
    const t_s = (timestamp - inicio) / 1000;
    const omega_visual = 2 * Math.PI / T_visual;

    ctx.clearRect(0, 0, W, H);

    // Línea de referencia (cuerda en reposo)
    ctx.strokeStyle = "rgba(255,255,255,0.15)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(xPix(0), cy);
    ctx.lineTo(xPix(L_js), cy);
    ctx.stroke();

    // Envolvente (máxima amplitud posible en cada punto)
    ctx.strokeStyle = "rgba(100,180,255,0.35)";
    ctx.setLineDash([4, 4]);
    ctx.lineWidth = 1.2;
    ctx.beginPath();
    for (let i = 0; i <= 300; i++) {{
        const xm = (i / 300) * L_js;
        const env = 2 * A_js * Math.abs(Math.sin(k_js * xm));
        const px = xPix(xm), py = yPix(env);
        if (i === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
    }}
    for (let i = 300; i >= 0; i--) {{
        const xm = (i / 300) * L_js;
        const env = -2 * A_js * Math.abs(Math.sin(k_js * xm));
        const py = yPix(env);
        ctx.lineTo(xPix(xm), py);
    }}
    ctx.stroke();
    ctx.setLineDash([]);

    // Cuerda vibrando: y(x,t) = 2A sin(kx) sin(omega_visual t)
    const grad = ctx.createLinearGradient(xPix(0), 0, xPix(L_js), 0);
    grad.addColorStop(0, "#64dcff");
    grad.addColorStop(0.5, "#ffdd55");
    grad.addColorStop(1, "#64dcff");
    ctx.strokeStyle = grad;
    ctx.lineWidth = 3;
    ctx.beginPath();
    for (let i = 0; i <= 400; i++) {{
        const xm = (i / 400) * L_js;
        const ym = 2 * A_js * Math.sin(k_js * xm) * Math.sin(omega_visual * t_s);
        const px = xPix(xm), py = yPix(ym);
        if (i === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
    }}
    ctx.stroke();

    // Soportes fijos en los extremos
    ctx.fillStyle = "#888";
    ctx.fillRect(xPix(0) - 6, cy - 14, 12, 28);
    ctx.fillRect(xPix(L_js) - 6, cy - 14, 12, 28);

    // Nodos (puntos fijos, no se mueven)
    ctx.fillStyle = "#aaaaaa";
    for (const xn of nodos) {{
        ctx.beginPath();
        ctx.arc(xPix(xn), cy, 4, 0, 2 * Math.PI);
        ctx.fill();
    }}

    // Antinodos (oscilan junto con la cuerda)
    for (let i = 0; i < antinodos.length; i++) {{
        const xa = antinodos[i];
        const ya = 2 * A_js * Math.sin(k_js * xa) * Math.sin(omega_visual * t_s);
        const esResaltado = (i === idx_resaltado);
        ctx.beginPath();
        ctx.arc(xPix(xa), yPix(ya), esResaltado ? 7 : 5, 0, 2 * Math.PI);
        ctx.fillStyle = esResaltado ? "#ff5a36" : "#ffee44";
        ctx.fill();
        ctx.strokeStyle = "white";
        ctx.lineWidth = 1;
        ctx.stroke();
    }}

    // Etiqueta del antinodo de referencia
    const xa_ref = antinodos[idx_resaltado];
    const ya_ref = 2 * A_js * Math.sin(k_js * xa_ref) * Math.sin(omega_visual * t_s);
    ctx.fillStyle = "#ff5a36";
    ctx.font = "bold 12px Arial";
    ctx.fillText("x = " + xa_ref.toFixed(3) + " m", xPix(xa_ref) + 10, yPix(ya_ref) - 10);

    // Panel de datos
    ctx.fillStyle = "rgba(0,0,0,0.6)";
    ctx.fillRect(10, 10, 160, 60);
    ctx.strokeStyle = "rgba(255,255,255,0.25)";
    ctx.strokeRect(10, 10, 160, 60);
    ctx.fillStyle = "white";
    ctx.font = "bold 12px Arial";
    ctx.fillText("Modo n = " + n_modo_js, 20, 28);
    ctx.fillStyle = "#aef";
    ctx.font = "12px Arial";
    ctx.fillText("Nodos: " + nodos.length, 20, 45);
    ctx.fillStyle = "#ffa";
    ctx.fillText("Antinodos: " + antinodos.length, 20, 60);

    requestAnimationFrame(dibujar);
}}

requestAnimationFrame(dibujar);
</script>
"""
    components.html(html_cuerda, height=300)