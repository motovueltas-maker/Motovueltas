import streamlit as st
import pandas as pd
from datetime import datetime, date

st.set_page_config(page_title="MotoVueltas - Gestión Operativa", layout="wide", page_icon="🛵")

# Initializing local database in Session State
if 'servicios' not in st.session_state:
    st.session_state.servicios = pd.DataFrame(columns=[
        'ID', 'Fecha', 'Cliente', 'Motorizado', 'Ruta_Detalle', 
        'Precio_Cliente', 'Porcentaje_Comision', 'Pago_Motorizado', 
        'Estado_Cliente', 'Estado_Motorizado'
    ])

if 'cortes_clientes' not in st.session_state:
    st.session_state.cortes_clientes = {}

if 'cortes_motorizados' not in st.session_state:
    st.session_state.cortes_motorizados = {}

st.title("🛵 MotoVueltas - Sistema de Control Unificado")

tab1, tab2, tab3, tab4 = st.tabs([
    "📝 Registrar Servicio", 
    "📊 Pendientes por Validar / Cobrar", 
    "💵 Corte Clientes & WhatsApp", 
    "🏍️ Liquidación Motorizados"
])

# TAB 1: REGISTRO RÁPIDO
with tab1:
    st.subheader("Registrar Nueva Carrera")
    col1, col2 = st.columns(2)
    with col1:
        motorizado = st.selectbox("Motorizado", ["Omar", "Jhoiner", "Deiby", "Génesis"])
        cliente = st.text_input("Nombre del Cliente / Negocio")
        ruta = st.text_area("Ruta / Descripción del servicio")
    with col2:
        precio_cliente = st.number_input("Monto Cobrado al Cliente ($)", min_value=0.0, step=0.5)
        comision_pct = st.number_input("% Comisión Motorizado", min_value=0.0, max_value=100.0, value=66.67)
        pago_motorizado = round(precio_cliente * (comision_pct / 100), 2)
        st.info(f"Monto correspondiente al motorizado: **${pago_motorizado}**")

    if st.button("Guardar Carrera", type="primary"):
        if cliente and ruta:
            nuevo_id = len(st.session_state.servicios) + 1
            nueva_fila = {
                'ID': nuevo_id,
                'Fecha': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'Cliente': cliente,
                'Motorizado': motorizado,
                'Ruta_Detalle': ruta,
                'Precio_Cliente': precio_cliente,
                'Porcentaje_Comision': comision_pct,
                'Pago_Motorizado': pago_motorizado,
                'Estado_Cliente': 'Pendiente',
                'Estado_Motorizado': 'Pendiente'
            }
            st.session_state.servicios = pd.concat([st.session_state.servicios, pd.DataFrame([nueva_fila])], ignore_index=True)
            st.success(f"Servicio #{nuevo_id} registrado correctamente.")
        else:
            st.error("Por favor completa el cliente y la ruta.")

# TAB 2: GESTIÓN Y EDICIÓN DE PENDIENTES
with tab2:
    st.subheader("Panel General de Servicios Registrados")
    if not st.session_state.servicios.empty:
        st.dataframe(st.session_state.servicios, use_container_width=True)
    else:
        st.info("No hay servicios registrados en esta sesión.")

# TAB 3: CORTE Y GENERADOR DE WHATSAPP CLIENTES
with tab3:
    st.subheader("Corte de Cuenta por Cliente y Mensaje de WhatsApp")
    if not st.session_state.servicios.empty:
        clientes_lista = st.session_state.servicios['Cliente'].unique()
        cliente_sel = st.selectbox("Seleccionar Cliente", clientes_lista)
        
        # Filtrar pendientes del cliente
        df_cliente = st.session_state.servicios[
            (st.session_state.servicios['Cliente'] == cliente_sel) & 
            (st.session_state.servicios['Estado_Cliente'] == 'Pendiente')
        ]
        
        total_deuda = df_cliente['Precio_Cliente'].sum()
        st.write(f"### Deuda Pendiente Actual: **${total_deuda:.2f}**")
        st.dataframe(df_cliente[['ID', 'Fecha', 'Ruta_Detalle', 'Precio_Cliente']], use_container_width=True)
        
        # Generar texto de WhatsApp
        msj = f"*MOTOVUELTAS - Resumen de Cuenta*\nCliente: {cliente_sel}\n---\n"
        for _, row in df_cliente.iterrows():
            msj += f"• Servicio #{row['ID']} ({row['Ruta_Detalle']}): ${row['Precio_Cliente']:.2f}\n"
        msj += f"---\n*TOTAL A PAGAR: ${total_deuda:.2f}*"
        
        st.text_area("Mensaje listo para copiar a WhatsApp:", msj, height=150)
        
        if st.button(f"Marcar Deuda de {cliente_sel} como PAGADA"):
            st.session_state.servicios.loc[
                (st.session_state.servicios['Cliente'] == cliente_sel) & 
                (st.session_state.servicios['Estado_Cliente'] == 'Pendiente'), 
                'Estado_Cliente'
            ] = 'Pagado'
            st.success(f"Corte realizado. Las vueltas de {cliente_sel} quedaron marcadas como pagadas.")
            st.rerun()

# TAB 4: LIQUIDACIÓN A MOTORIZADOS
with tab4:
    st.subheader("Liquidación de Vueltas a Motorizados")
    if not st.session_state.servicios.empty:
        moto_sel = st.selectbox("Seleccionar Motorizado", ["Omar", "Jhoiner", "Deiby", "Génesis"])
        
        df_moto = st.session_state.servicios[
            (st.session_state.servicios['Motorizado'] == moto_sel) & 
            (st.session_state.servicios['Estado_Motorizado'] == 'Pendiente')
        ]
        
        total_pago_moto = df_moto['Pago_Motorizado'].sum()
        st.write(f"### Total a Liquidar a {moto_sel}: **${total_pago_moto:.2f}**")
        st.dataframe(df_moto[['ID', 'Fecha', 'Cliente', 'Ruta_Detalle', 'Porcentaje_Comision', 'Pago_Motorizado']], use_container_width=True)
        
        if st.button(f"Liquidar / Pagar a {moto_sel}"):
            st.session_state.servicios.loc[
                (st.session_state.servicios['Motorizado'] == moto_sel) & 
                (st.session_state.servicios['Estado_Motorizado'] == 'Pendiente'), 
                'Estado_Motorizado'
            ] = 'Pagado'
            st.success(f"Se ha registrado el pago completo a {moto_sel}.")
            st.rerun()
