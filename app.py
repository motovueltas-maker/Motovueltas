import streamlit as st
import pandas as pd

st.set_page_config(page_title="MotoVueltas", layout="wide")

st.title("🛵 MotoVueltas - Sistema de Control")

# Pestañas principales
tab1, tab2, tab3, tab4 = st.tabs(["📋 Registrar Carrera", "👥 Clientes", "📊 Servicios Pendientes", "💰 Cortar Cuenta / WhatsApp"])

with tab1:
    st.header("Nuevo Servicio")
    motorizado = st.selectbox("Motorizado", ["Omar", "Jhoiner", "Deiby", "Génesis"])
    cliente = st.text_input("Nombre / Teléfono del Cliente")
    ruta = st.text_area("Ruta / Detalle del servicio")
    
    if st.button("Registrar Carrera"):
        st.success("¡Carrera registrada con éxito!")

with tab2:
    st.header("Gestión de Clientes")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Registrar Nuevo Cliente")
        nombre_cliente = st.text_input("Nombre del Cliente / Empresa")
        telefono_cliente = st.text_input("Teléfono (WhatsApp)")
        tipo_cliente = st.selectbox("Tipo de Cliente", ["Fijo", "Eventual"])
        ubicacion = st.text_input("Ubicación Habitual")
        
        if st.button("Guardar Cliente"):
            st.success(f"Cliente {nombre_cliente} guardado con éxito.")

    with col2:
        st.subheader("Directorio de Clientes")
        # Vista previa demostrativa de la tabla de clientes
        df_clientes = pd.DataFrame({
            "Cliente": ["Cliente Ejemplo 1", "Cliente Ejemplo 2"],
            "Teléfono": ["+584141234567", "+584129876543"],
            "Tipo": ["Fijo", "Eventual"],
            "Saldo Pendiente ($)": [0.0, 15.0]
        })
        st.dataframe(df_clientes, use_container_width=True)

with tab3:
    st.header("Servicios por Validar y Cobrar")
    st.info("Módulo para asignar montos y comisiones.")

with tab4:
    st.header("Liquidación y Mensajes")
    st.info("Módulo para generar mensajes de WhatsApp.")
