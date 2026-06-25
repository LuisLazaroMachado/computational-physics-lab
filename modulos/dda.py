import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import streamlit.components.v1 as components

"""
Si no tienen las librerias, instálenlas con estos comandos en el cmd:
pip install matplotlib
pip install numpy
pip install streamlit
"""

#------------------------------------------------------------------------------
g=9.81

def integrando(y, L, H):
    """
    Integrando de la fuerza total:
    80*g*L*(0.250*y³ - y + 10.0)*(H - y)
    """
    return 80.0 * g * L * (0.250 * y**3 - y + 10.0) * (H - y)

def fuerza_trapecio(L, H, n):
    """
    Calcular la fuerza total usando el método del trapecio.
    """
    a = 0.0 # El límite inferior de integración es 0, ya que la fuerza se calcula desde la base del dique hasta la altura del fluido.
    b = H # El límite superior de integración es la altura del fluido, H.
    h = (b - a) / n # El tamaño del paso de integración

    suma = integrando(a, L, H) + integrando(b, L, H) # La suma de los valores en los extremos de la integración
    
    # Se suman los valores del integrando en los puntos intermedios, multiplicados por 2, 
    # ya que el método del trapecio requiere que se dupliquen los términos intermedios.
    for i in range(1, n):
        yi = a + i * h
        suma += 2.0 * integrando(yi, L, H)

    return (h / 2.0) * suma

def fuerza_teorica(L, H):
    """
    Ecuación teórica dada en el enunciado:
    FTotal = 80*g*L*(0.0125*H³ - H/6 + 5)*H²
    """
    return 80.0 * g * L * (0.0125 * H**3 - H / 6.0 + 5.0) * H**2

def porcentaje_error(valor_aprox, valor_teorico):
    return abs((valor_teorico - valor_aprox) / valor_teorico) * 100.0

def mostrar():
# -----------------------------
# Lectura de datos
# -----------------------------
    longitud = st.slider("Longitud del dique L (m)", min_value=1.50, max_value=3.50, value=2.00, step=0.10)
    altura = st.slider("Altura del fluido H (m)", min_value=1.00, max_value=4.80, value=3.00, step=0.10)
    n = st.slider(
        "Número de trapecios (n)",
        min_value=1,
        max_value=1000,
        value=6
    )

    # ==========================================
    # Control interactivo
    # ==========================================

    trapecios_visibles = st.slider(
        "Cantidad de trapecios visibles",
        min_value=1,
        max_value=n,
        value=1,
        step=1
    )

    # -----------------------------
    # Cálculos para un valor de H
    # -----------------------------
    F_trap = fuerza_trapecio(longitud, altura, n)
    F_teo = fuerza_teorica(longitud, altura)
    error = porcentaje_error(F_trap, F_teo)

    st.markdown("### Resultados")
    col1, col2, col3 = st.columns(3)
    col1.metric("F trapecio", f"{F_trap:,.2f} N")
    col2.metric("F teórica", f"{F_teo:,.2f} N")
    col3.metric("Error", f"{error:.4f} %")

    if error <= 2.0:
        st.success(f"✅ Con n={n} trapecios, el error es {error:.4f}% — dentro del límite del 2%.")
    else:
        st.warning(f"⚠️ Con n={n} trapecios, el error es {error:.4f}% — supera el 2%. Aumenta n.")
    # -----------------------------
    # Gráfica FTotal vs H
    # -----------------------------
    H_vals = np.linspace(1.00, 4.80, 200) # Se genera un rango de valores de H desde 1.0 hasta altura=3.0 con 200 puntos para obtener una curva suave en la gráfica.
    F_trap_vals = np.array([fuerza_trapecio(longitud, h_val, n) for h_val in H_vals]) # Se calcula la fuerza total usando el método del trapecio para cada valor de H en el rango especificado.
    F_teo_vals = np.array([fuerza_teorica(longitud, h_val) for h_val in H_vals]) # Se calcula la fuerza total usando la ecuación teórica para cada valor de H en el rango especificado.


    # Puntos discretos visibles en la gráfica principal
    n_grafico = n

    H_trap = np.linspace(1.00, 4.80, n_grafico + 1)

    F_trap_points = np.array([
        fuerza_trapecio(longitud, h_val, n)
        for h_val in H_trap
    ])
    # --------------------------------
    # Datos para gráfica del integrando
    # -----------------------------
    y_cont = np.linspace(0.00, altura, 400)
    f_cont = integrando(y_cont, longitud, altura)

    y_trap = np.linspace(0.00, altura, n + 1)
    f_trap = integrando(y_trap, longitud, altura)

    # -----------------------------
    # Subgráficas
    # -----------------------------
    fig, axs = plt.subplots(2, 1, figsize=(10, 10))

    # ==========================================
    # Gráfica 1: Fuerza total vs altura H
    # ==========================================
    axs[0].plot(H_vals, F_trap_vals, label=f"Método del trapecio (n={n})")
    axs[0].plot(H_vals, F_teo_vals, label="Ecuación teórica", linestyle="--")

    axs[0].scatter(H_trap, F_trap_points, color="blue", s=25, zorder=3, label="Puntos evaluados")

    # Cortes verticales
    for i in range(len(H_trap)):
        axs[0].plot([H_trap[i], H_trap[i]], [0, F_trap_points[i]],
                    color="gray", linestyle=":", linewidth=0.8)

    for i in range(len(H_trap) - 1):
        hh_trap = [H_trap[i], H_trap[i], H_trap[i+1], H_trap[i+1]]
        ff_trapecio = [0, F_trap_points[i], F_trap_points[i+1], 0]

        axs[0].fill(hh_trap, ff_trapecio, 
                    color='yellow', 
                    edgecolor='darkblue', 
                    alpha=0.5)
    axs[0].set_xlabel("Altura del fluido H (m)")
    axs[0].set_ylabel("Fuerza total F (N)")
    axs[0].set_title("Grafica Fuerza total vs altura H")
    axs[0].grid(True)
    axs[0].legend()



    # ==========================================
    # Gráfica 2: Integrando vs y
    # ==========================================
    axs[1].plot(y_cont, f_cont, label="Integrando f(y)")

    axs[1].scatter(
        y_trap,
        f_trap,
        color="red",
        s=30,
        zorder=3,
        label="Puntos del trapecio"
    )

    for i in range(len(y_trap)):
        axs[1].plot(
            [y_trap[i], y_trap[i]],
            [0, f_trap[i]],
            color="gray",
            linestyle=":",
            linewidth=0.8
        )

    for i in range(trapecios_visibles):
        x_trap = [y_trap[i], y_trap[i], y_trap[i+1], y_trap[i+1]]
        y_trapecio = [0, f_trap[i], f_trap[i+1], 0]

        axs[1].fill(
            x_trap,
            y_trapecio,
            color='lightblue',
            edgecolor='red',
            alpha=0.5
        )

    axs[1].plot(y_trap, f_trap, color="orange", linestyle="--", label="Aproximación trapezoidal")

    axs[1].set_xlabel("profundidad del Fluido 'y' (m)")
    axs[1].set_ylabel("Fuerza diferencial por unidad de altura f(y)")
    axs[1].set_title(f"Integracion de la fuerza para H = {altura:.2f} m")
    axs[1].grid(True)
    axs[1].legend()

    plt.tight_layout(pad=2.0, h_pad=2.0)

    st.markdown("### Visualización de presión sobre el dique")

    presiones_lista = [
        float(80.0 * g * (0.250 * yi**3 - yi + 10.0) * (altura - yi))
        for yi in np.linspace(0.05, altura - 0.05, 40)
    ]
    presion_max_val = float(max(presiones_lista))

    html_dique = f"""
    <canvas id="dique" width="700" height="420" style="background:#0a0a1a;border-radius:10px;"></canvas>
    <script>
    const canvas = document.getElementById("dique");
    const ctx = canvas.getContext("2d");
    const W = canvas.width, H = canvas.height;

    const altura = {altura};
    const longitud = {longitud};
    const n = {n};
    const presiones = {presiones_lista};
    const presionMax = {presion_max_val};

    const dique_x = W * 0.62;
    const base_y = H * 0.88;
    const escala_y = (H * 0.78) / altura;

    // Flechas activas
    let flechas = [];
    let tiempo = 0;

    function nuevaFlecha(yi, pi) {{
        const ratio = pi / presionMax;
        const velocidad = 1.5 + 4.5 * ratio;
        const largo_max = 180 * ratio;
        const y_canvas = base_y - yi * escala_y;
        return {{
            x: dique_x - 10,
            y: y_canvas,
            largo_max: largo_max,
            velocidad: velocidad,
            ratio: ratio,
            progreso: 0
        }};
    }}

    function dibujar() {{
        ctx.clearRect(0, 0, W, H);

        // Agua con gradiente
        for (let i = 0; i < 60; i++) {{
            const y0 = base_y - (i / 60) * altura * escala_y;
            const y1 = base_y - ((i + 1) / 60) * altura * escala_y;
            const prof = i / 60;
            const r = 0, g2 = Math.floor(60 + 80 * prof), b = Math.floor(180 + 60 * prof);
            ctx.fillStyle = `rgb(${{r}},${{g2}},${{b}})`;
            ctx.fillRect(20, y1, dique_x - 20, y0 - y1);
        }}

        // Olas en la superficie
        ctx.beginPath();
        ctx.strokeStyle = "rgba(180,230,255,0.7)";
        ctx.lineWidth = 2;
        const sup_y = base_y - altura * escala_y;
        for (let x = 20; x < dique_x; x += 2) {{
            const ola = Math.sin((x + tiempo * 2) * 0.08) * 4;
            if (x === 20) ctx.moveTo(x, sup_y + ola);
            else ctx.lineTo(x, sup_y + ola);
        }}
        ctx.stroke();

        // Dique
        const grad = ctx.createLinearGradient(dique_x, 0, dique_x + 60, 0);
        grad.addColorStop(0, "#777");
        grad.addColorStop(1, "#aaa");
        ctx.fillStyle = grad;
        ctx.fillRect(dique_x, base_y - altura * escala_y * 1.1, 60, altura * escala_y * 1.2);

        // Base del canal
        ctx.fillStyle = "#555";
        ctx.fillRect(20, base_y, dique_x + 60, 20);

        // Etiqueta H
        ctx.strokeStyle = "white";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(12, base_y);
        ctx.lineTo(12, base_y - altura * escala_y);
        ctx.stroke();
        ctx.fillStyle = "white";
        ctx.font = "13px Arial";
        ctx.fillText("H=" + altura.toFixed(1) + "m", 2, base_y - altura * escala_y / 2);

        // Etiqueta L (horizontal en la base)
        ctx.strokeStyle = "white";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(20, base_y + 8);
        ctx.lineTo(dique_x, base_y + 8);
        ctx.stroke();
        ctx.fillStyle = "white";
        ctx.font = "12px Arial";
        ctx.fillText("L=" + longitud.toFixed(1) + "m", 20 + (dique_x - 20)/2 - 20, base_y + 20);

        // Presión como texto detrás del agua en cada zona
        const n_etiq = 5;
        for (let i = 0; i < n_etiq; i++) {{
            const yi = altura * (i + 0.5) / n_etiq;
            const pi = 80.0 * 9.81 * (0.250 * yi*yi*yi - yi + 10.0) * (altura - yi);
            const y_canvas = base_y - yi * escala_y;
            const prof = yi / altura;
            ctx.fillStyle = `rgba(255,255,255,${{0.25 + 0.4 * prof}})`;
            ctx.font = "11px Arial";
            ctx.fillText((pi/1000).toFixed(1) + " kN/m²", 30, y_canvas);
        }}

        // Dibujar flechas activas
        for (let f of flechas) {{
            f.progreso += f.velocidad;
            const largo_actual = Math.min(f.progreso, f.largo_max);
            const r = Math.floor(255);
            const g3 = Math.floor(255 * (1 - f.ratio));
            const color = `rgb(${{r}},${{g3}},0)`;
            ctx.strokeStyle = color;
            ctx.lineWidth = 1 + 3 * f.ratio;
            ctx.beginPath();
            ctx.moveTo(f.x - largo_actual, f.y);
            ctx.lineTo(f.x, f.y);
            ctx.stroke();
            // Punta de flecha
            ctx.fillStyle = color;
            ctx.beginPath();
            ctx.moveTo(f.x, f.y);
            ctx.lineTo(f.x - 10, f.y - 4);
            ctx.lineTo(f.x - 10, f.y + 4);
            ctx.closePath();
            ctx.fill();
        }}

        // Eliminar flechas que llegaron
        flechas = flechas.filter(f => f.progreso < f.largo_max + 20);

        // Generar nuevas flechas proporcional a n
        tiempo++;
        const n_flechas_objetivo = Math.ceil((n / 1000) * 40);
        if (flechas.length < n_flechas_objetivo) {{
            const idx = Math.floor(Math.random() * presiones.length);
            const yi = altura * (idx + 0.5) / presiones.length;
            const pi = presiones[idx];
            const ratio = pi / presionMax;
            if (Math.random() < (0.3 + 0.7 * ratio) && pi > 0) {{
                flechas.push(nuevaFlecha(yi, pi));
            }}
        }}

        // Panel de datos reducido
        ctx.fillStyle = "rgba(0,0,0,0.65)";
        ctx.fillRect(W - 210, 8, 200, 95);
        ctx.strokeStyle = "rgba(255,255,255,0.3)";
        ctx.lineWidth = 1;
        ctx.strokeRect(W - 210, 8, 200, 95);

        ctx.fillStyle = "white";
        ctx.font = "bold 12px Arial";
        ctx.fillText("📊 Parámetros", W - 200, 28);

        ctx.font = "12px Arial";
        ctx.fillStyle = "#aef";
        ctx.fillText("H = " + altura.toFixed(2) + " m", W - 200, 48);
        ctx.fillStyle = "#ffa";
        ctx.fillText("n = " + n + " trapecios", W - 200, 65);

        // Barra de n/1000
        ctx.fillStyle = "#333";
        ctx.fillRect(W - 200, 72, 180, 10);
        const fill_n = (n / 1000) * 180;
        const grad2 = ctx.createLinearGradient(W - 200, 0, W - 200 + 180, 0);
        grad2.addColorStop(0, "#00ff88");
        grad2.addColorStop(0.5, "#ffaa00");
        grad2.addColorStop(1, "#ff3300");
        ctx.fillStyle = grad2;
        ctx.fillRect(W - 200, 72, fill_n, 10);
        ctx.fillStyle = "white";
        ctx.font = "10px Arial";
        ctx.fillText("densidad de trapecios", W - 200, 95);
        requestAnimationFrame(dibujar);
    }}
    
    dibujar();
    </script>
    """
    st.pyplot(fig)
  
    components.html(html_dique, height=440)
  

