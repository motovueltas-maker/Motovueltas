import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de la aplicación
st.set_page_config(page_title="MotoVueltas - Control Operativo", layout="wide", page_icon="🛵")

# 1. BASE DE DATOS PERSISTENTE (Simulada en Session State con respaldo completo)
if 'servicios' not in st.session_state:
    st.session_state.servicios = pd.DataFrame(columns=[
        'ID', 'Fecha', 'Cliente', 'Motorizado', 'Ruta_Detalle', 
        'Precio_Cliente', 'Porcentaje_Comision', 'Monto_Motorizado', 'Ganancia_Empresa',
        'Estado_Cliente', 'Estado_Motorizado', 'Fecha_Pago_Cliente', 'Fecha_Pago_Motorizado'
    ])

# Tarifas de comisión predeterminadas por motorizado
COMISIONES_BASE = {
    "Omar": 66.67,
    "Jhoiner": 66.67,
    "Deiby": 66.67,
    "Génesis": 66.67
}

st.title("🛵 MotoVueltas - Sistema Integral de Gestión")

# Pestañas principales
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 Registrar Servicio", 
    "📊 Panel General / Filtros", 
    "💵 Corte Clientes (WhatsApp)", 
    "🏍️ Liquidación Motorizados",
    "📈 Resumen de Ganancias"
])

# ==========================================
# PESTAÑA 1: REGISTRAR SERVICIO
# ==========================================
with tab1:
    st.subheader("Registrar Nueva Carrera")
    
    col1, col2 = st.columns(2)
    with col1:
        motorizado = st.selectbox("Seleccionar Motorizado", list(COMISIONES_BASE.keys()))
        cliente = st.text_input("Nombre del Cliente / Comercio")
        ruta = st.text_area("Ruta / Detalle del Envío")
    
    with col2:
        precio_cliente = st.number_input("Precio Cobrado al Cliente ($)", min_value=0.0, value=0.0, step=0.50)
        
        # Comisión editable con valor predeterminado del motorizado
        comision_pct = st.number_input(
            "% Comisión Motorizado (Editable)", 
            min_value=0.0, max_value=100.0, 
            value=COMISIONES_BASE[motorizado], 
            step=1.0
        )
        
        # Cálculos automáticos e instantáneos
        monto_motorizado = round(precio_cliente * (comision_pct / 100.0), 2)
        ganancia_empresa = round(precio_cliente - monto_motorizado, 2)
        
        st.markdown(f"""
        * **Pago al Motorizado:** `${monto_motorizado:.2f}`
        * **Ganancia MotoVueltas:** `${ganancia_empresa:.2f}`
        """)

    if st.button("Guardar Servicio", type="primary", use_container_width=True):
        if cliente.strip() and ruta.strip() and precio_cliente > 0:
            nuevo_id = len(st.session_state.servicios) + 1
            nuevo_registro = {
                'ID': nuevo_id,
                'Fecha': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'Cliente': cliente.strip(),
                'Motorizado': motorizado,
                'Ruta_Detalle': ruta.strip(),
                'Precio_Cliente': precio_cliente,
                'Porcentaje_Comision': comision_pct,
                'Monto_Motorizado': monto_motorizado,
                'Ganancia_Empresa': ganancia_empresa,
                'Estado_Cliente': 'Pendiente',
                'Estado_Motorizado': 'Pendiente',
                'Fecha_Pago_Cliente': '-',
                'Fecha_Pago_Motorizado': '-'
            }
            st.session_state.servicios = pd.concat([st.session_state.servicios, pd.DataFrame([nuevo_registro])], ignore_index=True)
            st.success(f"¡Servicio #{nuevo_id} registrado exitosamente!")
            st.rerun()
        else:
            st.error("Por favor ingresa Cliente, Ruta y un Precio mayor a 0.")

# ==========================================
# PESTAÑA 2: PANEL GENERAL Y FILTROS
# ==========================================
with tab2:
    st.subheader("Filtros y Control de Servicios")
    
    if not st.session_state.servicios.empty:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filtro_est_cliente = st.selectbox("Filtrar por Cobro a Cliente", ["Todos", "Pendiente", "Pagado"])
        with col_f2:
            filtro_est_moto = st.selectbox("Filtrar por Pago a Motorizado", ["Todos", "Pendiente", "Pagado"])
        
        df_filtrado = st.session_state.servicios.copy()
        
        if filtro_est_cliente != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Estado_Cliente'] == filtro_est_cliente]
        if filtro_est_moto != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Estado_Motorizado'] == filtro_est_moto]
            
        st.dataframe(df_filtrado, use_container_width=True)
    else:
        st.info("Aún no hay servicios registrados.")

# ==========================================
# PESTAÑA 3: CORTE CLIENTES Y WHATSAPP
# ==========================================
with tab3:
    st.subheader("Corte de Cuenta por Cliente y Mensaje de WhatsApp")
    
    if not st.session_state.servicios.empty:
        # Filtrar solo servicios pendientes por cobrar al cliente
        pendientes_cliente = st.session_state.servicios[st.session_state.servicios['Estado_Cliente'] == 'Pendiente']
        
        if not pendientes_cliente.empty:
            clientes_activos = pendientes_cliente['Cliente'].unique()
            cliente_sel = st.selectbox("Seleccionar Cliente para Corte", clientes_activos)
            
            servicios_corte = pendientes_cliente[pendientes_cliente['Cliente'] == cliente_sel]
            total_cobrar = servicios_corte['Precio_Cliente'].sum()
            
            st.metric(label=f"Total Deuda Pendiente de {cliente_sel}", value=f"${total_cobrar:.2f}")
            st.dataframe(servicios_corte[['ID', 'Fecha', 'Ruta_Detalle', 'Precio_Cliente']], use_container_width=True)
            
            # Generador dinámico de mensaje para WhatsApp
            mensaje_wa = f"*MOTOVUELTAS - Resumen de Cuenta*\n"
            mensaje_wa += f"Cliente: *{cliente_sel}*\n"
            mensaje_wa += f"Fecha de Corte: {datetime.now().strftime('%d/%m/%Y')}\n"
            mensaje_wa += "-----------------------------------\n"
            for _, r in servicios_corte.iterrows():
                mensaje_wa += f"• Servicio #{r['ID']} ({r['Ruta_Detalle']}): ${r['Precio_Cliente']:.2f}\n"
            mensaje_wa += "-----------------------------------\n"
            mensaje_wa += f"*TOTAL A PAGAR: ${total_cobrar:.2f}*"
            
            st.text_area("Copiar Mensaje para WhatsApp:", mensaje_wa, height=180)
            
            if st.button(f"Marcar Deuda de {cliente_sel} como PAGADA", type="primary"):
                fecha_hoy = datetime.now().strftime("%Y-%m-%d %H:%M")
                st.session_state.servicios.loc[
                    (st.session_state.servicios['Cliente'] == cliente_sel) & 
                    (st.session_state.servicios['Estado_Cliente'] == 'Pendiente'),
                    ['Estado_Cliente', 'Fecha_Pago_Cliente']
                ] = ['Pagado', fecha_hoy]
                st.success(f"Corte realizado. Las carreras de {cliente_sel} quedaron registradas como PAGADAS.")
                st.rerun()
        else:
            st.success("¡Excelente! Todos los clientes están al día con sus pagos.")
    else:
        st.info("No hay registros en el sistema.")

# ==========================================
# PESTAÑA 4: LIQUIDACIÓN A MOTORIZADOS
# ==========================================
with tab4:
    st.subheader("Liquidación y Pago a Choferes")
    
    if not st.session_state.servicios.empty:
        pendientes_moto = st.session_state.servicios[st.session_state.servicios['Estado_Motorizado'] == 'Pendiente']
        
        if not pendientes_moto.empty:
            moto_sel = st.selectbox("Seleccionar Motorizado para Liquidar", list(COMISIONES_BASE.keys()))
            
            vueltas_moto = pendientes_moto[pendientes_moto['Motorizado'] == moto_sel]
            total_pagar_moto = vueltas_moto['Monto_Motorizado'].sum()
            
            st.metric(label=f"Monto Total a Liquidar a {moto_sel}", value=f"${total_pagar_moto:.2f}")
            st.dataframe(vueltas_moto[['ID', 'Fecha', 'Cliente', 'Ruta_Detalle', 'Porcentaje_Comision', 'Monto_Motorizado']], use_container_width=True)
            
            if st.button(f"Pagar / Liquidar a {moto_sel}", type="primary"):
                fecha_hoy = datetime.now().strftime("%Y-%m-%d %H:%M")
                st.session_state.servicios.loc[
                    (st.session_state.servicios['Motorizado'] == moto_sel) & 
                    (st.session_state.servicios['Estado_Motorizado'] == 'Pendiente'),
                    ['Estado_Motorizado', 'Fecha_Pago_Motorizado']
                ] = ['Pagado', fecha_hoy]
                st.success(f"Pago de ${total_pagar_moto:.2f} registrado para {moto_sel}.")
                st.rerun()
        else:
            st.success("¡Todos los motorizados tienen sus cuentas liquidadas!")
    else:
        st.info("No hay registros en el sistema.")

# ==========================================
# PESTAÑA 5: RESUMEN FINANCIERO
# ==========================================
with tab5:
    st.subheader("Balance Financiero General")
    if not st.session_state.servicios.empty:
        total_facturado = st.session_state.servicios['Precio_Cliente'].sum()
        total_motorizados = st.session_state.servicios['Monto_Motorizado'].sum()
        total_ganancia = st.session_state.servicios['Ganancia_Empresa'].sum()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Facturación Total Clientes", f"${total_facturado:.2f}")
        c2.metric("Total Pagado a Choferes", f"${total_motorizados:.2f}")
        c3.metric("Ganancia Neta MotoVueltas", f"${total_ganancia:.2f}")
    else:
        st.info("Sin datos suficientes para mostrar balance.")
