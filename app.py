import streamlit as st
import pandas as pd

st.set_page_config(page_title="MotoVueltas", layout="wide")

st.title("🛵 MotoVueltas - Sistema de Control")

# Pestañas principales de la App
tab1, tab2, tab3 = st.tabs(["📋 Registrar Carrera", "📊 Servicios Pendientes", "💰 Cortar Cuenta / WhatsApp"])

with tab1:
    st.header("Nuevo Servicio")
    motorizado = st.selectbox("Motorizado", ["Omar", "Jhoiner", "Deiby", "Génesis"])
    cliente = st.text_input("Nombre / Teléfono del Cliente")
    ruta = st.text_area("Ruta / Detalle del servicio")
    
    if st.button("Registrar Carrera"):
        st.success("¡Carrera registrada con éxito (Estado: Pendiente)!")

with tab2:
    st.header("Servicios por Validar y Cobrar")
    st.info("Aquí Esneyder podrá asignar precios, comisiones y validar cada servicio.")

with tab3:
    st.header("Liquidación y Mensajes")
    st.info("Módulo para generar el resumen de WhatsApp sin incluir cobros anteriores.")
