import streamlit as st
import requests
import datetime

# Configuración de página
st.set_page_config(
    page_title="Conversor BCV USD ↔ VES",
    page_icon="💱",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilo CSS Personalizado - Minimalista y Moderno
st.markdown("""
<style>
    /* Fondo y fuente principal */
    .main {
        background-color: #0E1117;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Contenedores / Tarjetas */
    .rate-card {
        background: linear-gradient(135deg, #161B22 0%, #1A212D 100%);
        border: 1px solid #1F6FEB;
        border-radius: 16px;
        padding: 22px 28px;
        margin-bottom: 20px;
        box-shadow: 0 8px 24px rgba(31, 111, 235, 0.12);
    }
    
    .card-title {
        color: #58A6FF;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    
    .rate-value {
        color: #3FB950;
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    
    .rate-subtitle {
        color: #8B949E;
        font-size: 0.82rem;
        margin-top: 4px;
    }
    
    /* Ocultar elementos innecesarios de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# TASA OFICIAL FIJADA DIRECTAMENTE A 888.11 Bs.
TASA_BCV_OFICIAL = 888.11

# Título de la Aplicación
st.markdown("<h1 style='text-align: center; color: #FFFFFF; font-size: 2rem; margin-bottom: 2px;'>Conversor BCV USD ↔ VES</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8B949E; font-size: 0.95rem; margin-bottom: 24px;'>Calculadora oficial de divisas al cambio del Banco Central de Venezuela</p>", unsafe_allow_html=True)

# Selección de Tasa (Prioriza 888.11 Bs. por defecto)
if "tasa_seleccionada" not in st.session_state:
    st.session_state.tasa_seleccionada = TASA_BCV_OFICIAL

# 1. Casilla Destacada con la Tasa Oficial del Día
st.markdown(f"""
<div class="rate-card">
    <div class="card-title">Tasa Oficial BCV del Día</div>
    <div class="rate-value">1 USD = {st.session_state.tasa_seleccionada:,.2f} VES</div>
    <div class="rate-subtitle">Fuente: Banco Central de Venezuela (BCV) • Tasa Oficial: 888.11 Bs.</div>
</div>
""", unsafe_allow_html=True)

# Control discreto para ajustar la tasa manualmente si el usuario lo desea
with st.expander("⚙️ Opciones de Tasa de Cambio (Ajuste Manual)"):
    tasa_input = st.number_input(
        "Tasa personalizada en Bs. por 1 USD:",
        min_value=0.01,
        value=float(st.session_state.tasa_seleccionada),
        step=1.0,
        format="%.2f"
    )
    if tasa_input != st.session_state.tasa_seleccionada:
        st.session_state.tasa_seleccionada = tasa_input
        st.rerun()
    
    if st.button("🔄 Restablecer a 888.11 Bs. (BCV)"):
        st.session_state.tasa_seleccionada = TASA_BCV_OFICIAL
        st.rerun()

tasa_actual = st.session_state.tasa_seleccionada

st.markdown("---")

# Inicializar estados de la sesión
if "historial" not in st.session_state:
    st.session_state.historial = []
if "monto_usd" not in st.session_state:
    st.session_state.monto_usd = 10.0
if "monto_ves" not in st.session_state:
    st.session_state.monto_ves = round(10.0 * tasa_actual, 2)

def actualizar_desde_usd():
    st.session_state.monto_ves = round(st.session_state.monto_usd * tasa_actual, 2)

def actualizar_desde_ves():
    if tasa_actual > 0:
        st.session_state.monto_usd = round(st.session_state.monto_ves / tasa_actual, 2)

def fijar_monto_usd(val):
    st.session_state.monto_usd = float(val)
    st.session_state.monto_ves = round(float(val) * tasa_actual, 2)

# Interfaz del Conversor Bidireccional
st.markdown("<h3 style='color: #FFFFFF; font-size: 1.1rem; margin-bottom: 16px;'>Calculadora de Conversión</h3>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.number_input(
        "Monto en Dólares ($ USD):",
        min_value=0.0,
        step=5.0,
        key="monto_usd",
        on_change=actualizar_desde_usd,
        format="%.2f"
    )

with col2:
    st.number_input(
        "Monto en Bolívares (Bs. VES):",
        min_value=0.0,
        step=50.0,
        key="monto_ves",
        on_change=actualizar_desde_ves,
        format="%.2f"
    )

# Resultados destacados
res_usd = st.session_state.monto_usd
res_ves = st.session_state.monto_ves

incluir_iva = st.checkbox("🧾 Calcular Impuesto al Valor Agregado (IVA 16%)", value=False)
iva_usd, total_usd_con_iva = res_usd * 0.16, res_usd * 1.16
iva_ves, total_ves_con_iva = res_ves * 0.16, res_ves * 1.16

if not incluir_iva:
    st.markdown(f"""
    <div style="background-color: #161B22; border-radius: 12px; padding: 18px 24px; margin-top: 16px; border-left: 4px solid #238636;">
        <div style="color: #8B949E; font-size: 0.85rem; margin-bottom: 4px;">RESUMEN DE CONVERSIÓN</div>
        <div style="color: #FFFFFF; font-size: 1.25rem; font-weight: 600;">
            <span style="color: #3FB950;">${res_usd:,.2f} USD</span> &nbsp;=&nbsp; <span style="color: #58A6FF;">{res_ves:,.2f} Bs.</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div style="background-color: #161B22; border-radius: 12px; padding: 18px 24px; margin-top: 16px; border-left: 4px solid #238636;">
        <div style="color: #8B949E; font-size: 0.85rem; margin-bottom: 4px;">DESGLOSE CON IVA (16%)</div>
        <div style="color: #FFFFFF; font-size: 1.1rem; font-weight: 600; margin-bottom: 6px;">
            Base: <span style="color: #3FB950;">${res_usd:,.2f} USD</span> / <span style="color: #58A6FF;">{res_ves:,.2f} Bs.</span>
        </div>
        <div style="color: #D29922; font-size: 0.95rem; margin-bottom: 6px;">
            + IVA (16%): <strong>${iva_usd:,.2f} USD</strong> / <strong>{iva_ves:,.2f} Bs.</strong>
        </div>
        <div style="color: #238636; font-size: 1.25rem; font-weight: 700; margin-top: 8px;">
            TOTAL CON IVA: ${total_usd_con_iva:,.2f} USD &nbsp;({total_ves_con_iva:,.2f} Bs.)
        </div>
    </div>
    """, unsafe_allow_html=True)

def guardar_historial():
    hora_actual = datetime.datetime.now().strftime("%H:%M:%S")
    registro = {
        "Hora": hora_actual,
        "USD Base": f"${res_usd:,.2f}",
        "Bs. Base": f"{res_ves:,.2f} Bs.",
        "Tasa BCV": f"{tasa_actual:,.2f}",
        "Con IVA (16%)": f"${total_usd_con_iva:,.2f} / {total_ves_con_iva:,.2f} Bs." if incluir_iva else "Sin IVA"
    }
    st.session_state.historial.insert(0, registro)

st.button("💾 Guardar esta conversión en el historial", on_click=guardar_historial)

# Botones de Accesos Rápidos
st.markdown("<p style='color: #8B949E; font-size: 0.85rem; margin-top: 24px; margin-bottom: 8px;'>Montos rápidos:</p>", unsafe_allow_html=True)
btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)

btn_col1.button("$5 USD", on_click=fijar_monto_usd, args=(5.0,))
btn_col2.button("$20 USD", on_click=fijar_monto_usd, args=(20.0,))
btn_col3.button("$50 USD", on_click=fijar_monto_usd, args=(50.0,))
btn_col4.button("$100 USD", on_click=fijar_monto_usd, args=(100.0,))

st.markdown("---")
st.markdown("<h3 style='color: #FFFFFF; font-size: 1.1rem; margin-bottom: 12px;'>📜 Historial de Conversiones</h3>", unsafe_allow_html=True)

def limpiar_historial():
    st.session_state.historial = []

if len(st.session_state.historial) > 0:
    st.dataframe(st.session_state.historial, use_container_width=True)
    st.button("🗑️ Limpiar Historial", on_click=limpiar_historial)
else:
    st.info("Aún no has guardado ninguna conversión en esta sesión. Haz clic en 'Guardar esta conversión' para ir registrando tus cálculos.")

st.markdown("<br><p style='text-align: center; color: #484F58; font-size: 0.8rem;'>Aplicación desarrollada con diseño minimalista • Tasa Oficial BCV</p>", unsafe_allow_html=True)
