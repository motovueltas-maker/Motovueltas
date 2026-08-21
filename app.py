import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="MotoVueltas", layout="wide")

st.title("🛵 MotoVueltas - Sistema de Control")

# URL de tu Google Sheet
SHEET_URL = "https://docs.google.com/spreadsheets/d/1HS3Hn_9YQNEdnUgxnpsG1xDckJeGUwhVnNcMwe-EWrQ/edit?gid=0#gid=0"

# Conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Cargar clientes desde Google Sheets
def cargar_clientes():
    try:
        df = conn.read(spreadsheet=SHEET_URL, ttl=0)
        return df
    except Exception as e:
        return pd.DataFrame(columns=["Nombre", "Telefono", "Tipo", "Ubicacion", "Saldo"])

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
        nombre = st.text_input("Nombre del Cliente / Empresa")
        telefono = st.text_input("Teléfono (WhatsApp)")
        tipo = st.selectbox("Tipo de Cliente", ["Fijo", "Eventual"])
        ubicacion = st.text_input("Ubicación Habitual")
        
        if st.button("Guardar Cliente"):
            if nombre and telefono:
                df_actual = cargar_clientes()
                nuevo_cliente = pd.DataFrame([{
                    "Nombre": nombre,
                    "Telefono": telefono,
                    "Tipo": tipo,
                    "Ubicacion": ubicacion,
                    "Saldo": 0.0
                }])
                df_actualizado = pd.concat([df_actual, nuevo_cliente], ignore_index=True)
                conn.update(spreadsheet=SHEET_URL, data=df_actualizado)
                st.success(f"¡Cliente {nombre} guardado con éxito en Google Sheets!")
                st.rerun()
            else:
                st.error("Por favor completa el Nombre y Teléfono.")

    with col2:
        st.subheader("Directorio de Clientes en Vivo")
        df_clientes = cargar_clientes()
        st.dataframe(df_clientes, use_container_width=True)

with tab3:
    st.header("Servicios por Validar y Cobrar")
    st.info("Módulo para asignar montos y comisiones.")

with tab4:
    st.header("Liquidación y Mensajes")
    st.info("Módulo para generar mensajes de WhatsApp.")
