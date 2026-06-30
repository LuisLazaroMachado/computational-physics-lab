import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator
import streamlit as st


# =========================================================
# DDD - PARTE 1
# Espejismos y refracción de la luz
# Método numérico: Runge-Kutta de cuarto orden (RK4)
# =========================================================

# =========================================================
# PARÁMETROS DEL PROBLEMA
# =========================================================

# Índice de refracción en la base
n0 = 1.00030

# Constante de variación del índice de refracción
alpha = 5.00e-3        # 1/m

# Condición inicial
x0 = 0.00              # m
y0 = 3.00              # m
theta0 = -0.150        # rad

# Condición final
xf = 60.0              # m

# Paso de integración
dx = 5.00e-3           # m

# =========================================================
# FORMATO DE 3 CIFRAS SIGNIFICATIVAS CON COMA DECIMAL
# =========================================================

def mostrar():
    
    def formato_3cs(valor, posicion=None):
        """
        Formatea números con 3 cifras significativas
        y coma decimal para los ejes de las gráficas.
        """

        if abs(valor) < 1e-12:
            return "0,00"

        cifras = 3
        decimales = cifras - int(np.floor(np.log10(abs(valor)))) - 1
        decimales = max(decimales, 0)

        texto = f"{valor:.{decimales}f}"
        return texto.replace(".", ",")


    def aplicar_formato_grafica(ax):
        """
        Aplica formato correcto a los ejes.
        """

        ax.xaxis.set_major_formatter(FuncFormatter(formato_3cs))
        ax.yaxis.set_major_formatter(FuncFormatter(formato_3cs))

        ax.xaxis.set_major_locator(MaxNLocator(nbins=8))
        ax.yaxis.set_major_locator(MaxNLocator(nbins=7))

        ax.grid(True, alpha=0.35)


    # =========================================================
    # MODELO FÍSICO
    # =========================================================

    def indice_refraccion(y):
        """
        Índice de refracción variable con la altura.
        n(y) = n0 + alpha*y
        """

        return n0 + alpha * y


    def sistema_ecuaciones(x, u):
        """
        Sistema de ecuaciones diferenciales:

        dy/dx = tan(theta)
        dtheta/dx = (1/n(y))*(dn/dy)

        Como n(y) = n0 + alpha*y,
        entonces dn/dy = alpha.
        """

        y = u[0]
        theta = u[1]

        n_y = indice_refraccion(y)

        dy_dx = np.tan(theta)
        dtheta_dx = alpha / n_y

        return np.array([dy_dx, dtheta_dx])


    # =========================================================
    # MÉTODO RUNGE-KUTTA DE CUARTO ORDEN
    # =========================================================

    def rk4(x0, y0, theta0, xf, dx):
        """
        Resuelve el sistema usando RK4.
        Devuelve arreglos de x, y y theta.
        """

        x_vals = []
        y_vals = []
        theta_vals = []

        x = x0
        u = np.array([y0, theta0], dtype=float)

        while x <= xf:
            x_vals.append(x)
            y_vals.append(u[0])
            theta_vals.append(u[1])

            k1 = sistema_ecuaciones(x, u)
            k2 = sistema_ecuaciones(x + dx/2, u + (dx/2)*k1)
            k3 = sistema_ecuaciones(x + dx/2, u + (dx/2)*k2)
            k4 = sistema_ecuaciones(x + dx, u + dx*k3)

            u = u + (dx/6)*(k1 + 2*k2 + 2*k3 + k4)
            x = x + dx

        return np.array(x_vals), np.array(y_vals), np.array(theta_vals)


    # =========================================================
    # EJECUTAR SIMULACIÓN
    # =========================================================

    x_vals, y_vals, theta_vals = rk4(x0, y0, theta0, xf, dx)

    # =========================================================
    # CÁLCULO DE ALTURA MÍNIMA SIMULADA
    # =========================================================

    indice_minimo = np.argmin(y_vals)

    y_min_simulado = y_vals[indice_minimo]
    x_retorno = x_vals[indice_minimo]
    theta_retorno = theta_vals[indice_minimo]

    # =========================================================
    # CÁLCULO TEÓRICO DE ALTURA MÍNIMA
    # =========================================================

    y_min_teorico = ((n0 + alpha*y0)*np.cos(theta0) - n0) / alpha

    # Porcentaje de error
    error_porcentual = abs((y_min_teorico - y_min_simulado) / y_min_teorico) * 100

    # =========================================================
    # VERIFICACIÓN DE EXISTENCIA DEL ESPEJISMO
    # =========================================================

    alpha_min = (n0 * (1 - np.cos(theta0))) / (y0 * np.cos(theta0))

    print("======================================================")
    print("               VERIFICACIÓN DEL ESPEJISMO")
    print("======================================================")

    print("Condición para que exista espejismo:")
    print(f"alpha > {alpha_min:.6g} 1/m")

    if alpha > alpha_min:
        print("Sí se garantiza la existencia del espejismo.")
    else:
        print("No se garantiza la existencia del espejismo.")

    print("\n======================================================")
    print("                    RESULTADOS")
    print("======================================================")

    print(f"Altura mínima simulada: {y_min_simulado:.6f} m")
    print(f"Posición de retorno simulada: {x_retorno:.6f} m")
    print(f"Ángulo en el retorno simulado: {theta_retorno:.6f} rad")
    print(f"Altura mínima teórica: {y_min_teorico:.6f} m")
    print(f"Porcentaje de error: {error_porcentual:.6f} %")

    # =========================================================
    # VENTANA INTERACTIVA CON BOTONES
    # Trayectoria, evolución angular y animación con slider
    # =========================================================

    from matplotlib.widgets import Slider, Button
    from matplotlib.colors import LinearSegmentedColormap

    # ---------------------------------------------------------
    # Formato especial para el ángulo de retorno
    # ---------------------------------------------------------

    def formato_theta_retorno(theta):
        """
        Si el ángulo numérico es muy pequeño, se muestra como cero,
        porque físicamente en el retorno θ = 0 rad.
        """
        if abs(theta) < 5e-4:
            return "0,000"
        return formato_3cs(theta)

    # Estado actual
    modo_actual = ["Trayectoria"]

    # Diccionario para guardar elementos móviles de la animación
    elementos_animacion = {}


    # ---------------------------------------------------------
    # Límites comunes para la gráfica de trayectoria
    # ---------------------------------------------------------

    x_min = float(x_vals.min())
    x_max = float(x_vals.max())

    y_min_grafica = -0.30
    y_max_grafica = float(max(y_vals) + 0.50)

    # Para que el observador entre en la gráfica de animación
    x_observador = x_max + 1.50
    y_observador = 1.20


    # ---------------------------------------------------------
    # Fondo físico: aire caliente y aire frío
    # ---------------------------------------------------------

    def dibujar_fondo_aire(ax):
        """
        Dibuja el fondo con gradiente:
        aire caliente abajo y aire frío arriba.
        """

        ax.set_xlim(x_min, x_max + 2.00)
        ax.set_ylim(y_min_grafica, y_max_grafica)

        gradiente = np.linspace(0, 1, 300).reshape(300, 1)

        mapa_aire = LinearSegmentedColormap.from_list(
            "gradiente_aire",
            ["#ffd1a3", "#fff7ec", "#dbe9ff"]
        )

        ax.imshow(
            gradiente,
            extent=[x_min, x_max + 2.00, y_min_grafica, y_max_grafica],
            origin="lower",
            aspect="auto",
            cmap=mapa_aire,
            alpha=0.75,
            zorder=0
        )

        # Suelo
        ax.axhline(
            0,
            linewidth=3,
            color="#8B4513",
            label="Suelo (y = 0 m)",
            zorder=3
        )

        # Etiquetas del medio
        ax.text(
            x_min + 0.02*(x_max - x_min),
            y_max_grafica - 0.35,
            "Aire FRÍO (n grande)",
            fontsize=11,
            color="navy",
            weight="bold"
        )

        ax.text(
            x_min + 0.02*(x_max - x_min),
            0.12,
            "Aire CALIENTE (n pequeño)",
            fontsize=11,
            color="#8B4513",
            weight="bold"
        )


    # ---------------------------------------------------------
    # Función para anotar ángulos con recta tangente
    # ---------------------------------------------------------

    def anotar_angulo_con_tangente(ax, indice, desplazamiento_x, desplazamiento_y, longitud_tangente=4.0):
        """
        Dibuja un punto sobre la trayectoria, una recta tangente local
        y el valor del ángulo θ en grados.
        """

        x_p = x_vals[indice]
        y_p = y_vals[indice]
        theta_p = theta_vals[indice]
        theta_p_deg = np.degrees(theta_p)

        # Punto sobre la curva
        ax.scatter(
            x_p,
            y_p,
            color="black",
            s=35,
            zorder=7
        )

        # Tangente local
        m_tangente = np.tan(theta_p)

        dx_t = longitud_tangente / 2
        x_tan = np.array([x_p - dx_t, x_p + dx_t])
        y_tan = y_p + m_tangente * (x_tan - x_p)

        ax.plot(
            x_tan,
            y_tan,
            color="black",
            linewidth=3,
            solid_capstyle="round",
            zorder=6
        )

        # Texto del ángulo
        texto = r"$\theta$ = " + formato_3cs(theta_p_deg) + "°"

        ax.annotate(
            texto,
            xy=(x_p, y_p),
            xytext=(x_p + desplazamiento_x, y_p + desplazamiento_y),
            arrowprops=dict(arrowstyle="->", color="black", linewidth=1.2),
            fontsize=10,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="gray", alpha=0.85),
            zorder=8
        )


    # ---------------------------------------------------------
    # Gráfica 1: trayectoria y vs x
    # ---------------------------------------------------------

    def mostrar_trayectoria(event=None):
        modo_actual[0] = "Trayectoria"
        elementos_animacion.clear()

        ax.clear()
        

        dibujar_fondo_aire(ax)

        # Trayectoria del rayo
        ax.plot(
            x_vals,
            y_vals,
            color="crimson",
            linewidth=3,
            label="Trayectoria del rayo (RK4)",
            zorder=5
        )

        # Punto de retorno
        ax.scatter(
            x_retorno,
            y_min_simulado,
            color="black",
            s=70,
            zorder=8,
            label=r"Punto de retorno $(x_{\mathrm{retorno}}, y_{\min})$"
        )

        # Líneas guía del retorno
        ax.axvline(
            x_retorno,
            linestyle="--",
            linewidth=1.3,
            color="gray",
            alpha=0.8,
            zorder=4
        )

        ax.axhline(
            y_min_simulado,
            linestyle="--",
            linewidth=1.3,
            color="gray",
            alpha=0.8,
            zorder=4
        )

        # Anotación del punto de retorno
        texto_retorno = (
            r"$y_{\min}$ = " + formato_3cs(y_min_simulado) + " m\n"
            r"$x_{\mathrm{retorno}}$ = " + formato_3cs(x_retorno) + " m"
        )

        ax.annotate(
            texto_retorno,
            xy=(x_retorno, y_min_simulado),
            xytext=(x_retorno + 0.13*(x_max - x_min), y_min_simulado + 0.28*(y_max_grafica - y_min_grafica)),
            arrowprops=dict(arrowstyle="->", color="black", linewidth=1.5),
            fontsize=11,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.85),
            zorder=9
        )

        # Ángulos con tangente
        indice_izquierdo = int(0.10 * len(x_vals))
        indice_derecho = int(0.68 * len(x_vals))

        anotar_angulo_con_tangente(ax, indice_izquierdo, 2.0, 0.20, longitud_tangente=4.0)
        anotar_angulo_con_tangente(ax, indice_derecho, 2.0, -0.10, longitud_tangente=4.0)

        ax.set_title(
            "Altura del rayo vs posición horizontal",
            fontsize=14,
            weight="bold"
        )

        ax.set_xlabel("Posición horizontal, x (m)", fontsize=12)
        ax.set_ylabel("Altura del rayo, y (m)", fontsize=12)

        ax.legend(loc="upper right", fontsize=10, framealpha=0.95)

        aplicar_formato_grafica(ax)

    # ---------------------------------------------------------
    # Gráfica 2: evolución angular θ vs x
    # ---------------------------------------------------------

    def mostrar_angulo(event=None):
        modo_actual[0] = "Angulo"
        elementos_animacion.clear()

        ax.clear()
        

        ax.plot(
            x_vals,
            theta_vals,
            linewidth=2,
            label="Ángulo local de propagación del rayo"
        )

        ax.axhline(
            0,
            linestyle="--",
            linewidth=1.5,
            label="Condición de retorno: θ = 0 rad"
        )

        ax.scatter(
            x_retorno,
            theta_retorno,
            s=60,
            zorder=5,
            label=f"Ángulo en el retorno: θ = {formato_theta_retorno(theta_retorno)} rad"
        )

        ax.set_title("Ángulo de Propagación vs Posición Horizontal", fontsize=14, weight="bold")
        ax.set_xlabel("Posición horizontal, x (m)", fontsize=12)
        ax.set_ylabel("Ángulo de propagación, θ (rad)", fontsize=12)

        ax.legend(loc="upper left", fontsize=10, framealpha=0.95)

        aplicar_formato_grafica(ax)

    # ---------------------------------------------------------
    # Gráfica 3: animación interactiva del espejismo
    # ---------------------------------------------------------

    def mostrar_animacion(event=None):
        modo_actual[0] = "Animacion"

        ax.clear()
        

        dibujar_fondo_aire(ax)

        ax.set_xlim(x_min, x_max + 2.00)
        ax.set_ylim(y_min_grafica, y_max_grafica)

        ax.set_title("Espejismo: exploración interactiva del rayo de luz", fontsize=14, weight="bold")
        ax.set_xlabel("Posición horizontal, x (m)", fontsize=12)
        ax.set_ylabel("Altura del rayo, y (m)", fontsize=12)

        # Trayectoria real
        ax.plot(
            x_vals,
            y_vals,
            color="crimson",
            linewidth=2.5,
            zorder=5,
            label="Trayectoria real del rayo"
        )

        # Punto de retorno
        ax.plot(
            x_retorno,
            y_min_simulado,
            marker="x",
            markersize=10,
            markeredgewidth=2,
            color="darkred",
            zorder=7,
            label="Punto de retorno"
        )

        # Observador
        ax.plot(
            x_observador,
            y_observador,
            "o",
            color="green",
            markersize=10,
            zorder=7,
            label="Observador"
        )

        # Elementos móviles
        punto_rayo, = ax.plot([], [], "o", color="black", markersize=8, zorder=9)

        linea_aparente, = ax.plot(
            [],
            [],
            "--",
            linewidth=2,
            color="deepskyblue",
            zorder=6,
            label="Dirección aparente"
        )

        linea_ref_angulo, = ax.plot(
            [],
            [],
            "--",
            color="gray",
            linewidth=1.4,
            zorder=7,
            label="Referencia horizontal"
        )

        linea_dir_angulo, = ax.plot(
            [],
            [],
            color="black",
            linewidth=2.2,
            zorder=8,
            label="Dirección real del rayo"
        )

        texto_angulo = ax.annotate(
            "",
            xy=(0, 0),
            fontsize=10,
            fontweight="bold",
            color="black",
            zorder=10
        )

        texto_info = ax.text(
            0.02,
            0.97,
            "",
            transform=ax.transAxes,
            va="top",
            fontsize=11,
            bbox=dict(facecolor="white", alpha=0.85),
            zorder=10
        )

        elementos_animacion.clear()
        elementos_animacion["punto_rayo"] = punto_rayo
        elementos_animacion["linea_aparente"] = linea_aparente
        elementos_animacion["linea_ref_angulo"] = linea_ref_angulo
        elementos_animacion["linea_dir_angulo"] = linea_dir_angulo
        elementos_animacion["texto_angulo"] = texto_angulo
        elementos_animacion["texto_info"] = texto_info

        ax.legend(loc="upper right", fontsize=9, framealpha=0.95)

        aplicar_formato_grafica(ax)




    # ---------------------------------------------------------
    # Actualización del slider
    # ---------------------------------------------------------

    LARGO_ANGULO = 5.0

    def actualizar_animacion(valor):
        if modo_actual[0] != "Animacion":
            return

        if len(elementos_animacion) == 0:
            return

        indice = np.argmin(np.abs(x_vals - valor))

        x = x_vals[indice]
        y = y_vals[indice]
        theta = theta_vals[indice]
        theta_deg = np.degrees(theta)

        punto_rayo = elementos_animacion["punto_rayo"]
        linea_aparente = elementos_animacion["linea_aparente"]
        linea_ref_angulo = elementos_animacion["linea_ref_angulo"]
        linea_dir_angulo = elementos_animacion["linea_dir_angulo"]
        texto_angulo = elementos_animacion["texto_angulo"]
        texto_info = elementos_animacion["texto_info"]

        # Punto actual
        punto_rayo.set_data([x], [y])

        # Línea aparente hacia el observador
        linea_aparente.set_data(
            [x, x_observador],
            [y, y_observador]
        )

        # Referencia horizontal
        linea_ref_angulo.set_data(
            [x, x + LARGO_ANGULO],
            [y, y]
        )

        # Dirección real del rayo
        linea_dir_angulo.set_data(
            [x, x + LARGO_ANGULO*np.cos(theta)],
            [y, y + LARGO_ANGULO*np.sin(theta)]
        )

        # Texto del ángulo
        r_etiqueta = LARGO_ANGULO * 0.35
        angulo_bisectriz = theta / 2

        texto_angulo.set_text(
            r"$\theta$ = " + formato_3cs(theta_deg) + "°"
        )

        texto_angulo.set_position(
            (
                x + r_etiqueta*np.cos(angulo_bisectriz),
                y + r_etiqueta*np.sin(angulo_bisectriz)
            )
        )

        # Texto informativo
        texto_info.set_text(
            "x = " + formato_3cs(x) + " m\n"
            "y = " + formato_3cs(y) + " m\n"
            r"$\theta$ = " + formato_3cs(theta) + " rad\n"
            r"$\theta$ = " + formato_3cs(theta_deg) + "°"
        )

    # ---------------------------------------------------------
    # Estado inicial
    # ---------------------------------------------------------

    # ---------------------------------------------------------
    # Gráfica 1: trayectoria y vs x
    # ---------------------------------------------------------
    fig1 = plt.figure(figsize=(12, 6.5))
    ax = fig1.add_axes([0.08, 0.12, 0.88, 0.80])
    mostrar_trayectoria()
    st.pyplot(fig1)
    plt.close(fig1)

    # ---------------------------------------------------------
    # Gráfica 2: evolución angular θ vs x
    # ---------------------------------------------------------
    fig2 = plt.figure(figsize=(12, 6.5))
    ax = fig2.add_axes([0.08, 0.12, 0.88, 0.80])
    mostrar_angulo()
    st.pyplot(fig2)
    plt.close(fig2)

    # ---------------------------------------------------------
    # Gráfica 3: animación interactiva con slider
    # ---------------------------------------------------------
    x_st = st.slider(
        "Posición x (m)",
        float(x_vals.min()),
        float(x_vals.max()),
        float(x_vals.min())
    )
    fig3 = plt.figure(figsize=(12, 6.5))
    ax = fig3.add_axes([0.08, 0.12, 0.88, 0.80])
    mostrar_animacion()
    actualizar_animacion(x_st)
    st.pyplot(fig3)
    plt.close(fig3)