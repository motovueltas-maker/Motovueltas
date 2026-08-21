import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="MotoVueltas - Control Operativo", layout="wide", page_icon="🛵")

# ---------------------------------------------------------
# MANEJO DE ARCHIVOS CSV (PERSISTENCIA SEGURA EN GITHUB)
# ---------------------------------------------------------
FILE_CLIENTES = "clientes.csv"
FILE_MOTORIZADOS = "motorizados.csv"
FILE_SERVICIOS = "servicios.csv"

def cargar_datos():
    if os.path.exists(FILE_CLIENTES):
        df_cli = pd.read_csv(FILE_CLIENTES)
        if 'Ubicacion' not in df_cli.columns:
            df_cli['Ubicacion'] = "-"
            df_cli.to_csv(FILE_CLIENTES, index=False)
    else:
        df_cli = pd.DataFrame([{"Nombre": "Cliente General", "Telefono": "04140000000", "Ubicacion": "Centro"}])
        df_cli.to_csv(FILE_CLIENTES, index=False)
    if os.path.exists(FILE_MOTORIZADOS):
        df_mot = pd.read_csv(FILE_MOTORIZADOS)
    else:
        df_mot = pd.DataFrame([
            {"Nombre": "Omar", "Comision_Base": 66.67},
            {"Nombre": "Jhoiner", "Comision_Base": 66.67},
            {"Nombre": "Deiby", "Comision_Base": 66.67},
            {"Nombre": "Génesis", "Comision_Base": 66.67}
        ])
        df_mot.to_csv(FILE_MOTORIZADOS, index=False)

    if os.path.exists(FILE_SERVICIOS):
        df_ser = pd.read_csv(FILE_SERVICIOS)
    else:
        df_ser = pd.DataFrame(columns=[
            'ID', 'Fecha', 'Motorizado', 'Cliente', 'Origen', 'Destino', 'Detalle',
            'Precio_Cliente', 'Porcentaje_Comision', 'Monto_Motorizado', 'Ganancia_Empresa',
            'Estado_Validacion', 'Estado_Cliente', 'Estado_Motorizado'
        ])
        df_ser.to_csv(FILE_SERVICIOS, index=False)

    return df_cli, df_mot, df_ser

df_clientes, df_motorizados, df_servicios = cargar_datos()

st.title("🛵 MotoVueltas - Sistema de Gestión")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🛵 Registrar Vuelta (Motorizado)", 
    "✅ Validar Precios (Admin)", 
    "💵 Corte Clientes (WhatsApp)", 
    "🏍️ Liquidación Motorizados",
    "👥 Directorio Clientes",
    "⚙️ Perfiles Motorizados"
])

# ---------------------------------------------------------
# TAB 1: REGISTRAR VUELTA (SOLO MOTORIZADO)
# ---------------------------------------------------------
with tab1:
    st.subheader("Registro Rápido de Carrera")
    
    col1, col2 = st.columns(2)
    with col1:
        lista_motos = df_motorizados['Nombre'].tolist()
        moto_sel = st.selectbox("Tu Nombre (Motorizado)", lista_motos)
        
        lista_cli = df_clientes['Nombre'].tolist()
        cli_sel = st.selectbox("Seleccionar Cliente", lista_cli)
        
    with col2:
        origen = st.text_input("Origen (Desde)", value="Local")
        destino = st.text_input("Destino (Hasta)")
        detalle = st.text_area("Detalle / Observación del servicio")

    if st.button("Enviar Vuelta para Validación", type="primary", use_container_width=True):
        if destino.strip():
            nuevo_id = len(df_servicios) + 1
            nueva_fila = {
                'ID': nuevo_id,
                'Fecha': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'Motorizado': moto_sel,
                'Cliente': cli_sel,
                'Origen': origen.strip(),
                'Destino': destino.strip(),
                'Detalle': detalle.strip(),
                'Precio_Cliente': 0.0,
                'Porcentaje_Comision': 0.0,
                'Monto_Motorizado': 0.0,
                'Ganancia_Empresa': 0.0,
                'Estado_Validacion': 'Pendiente',
                'Estado_Cliente': 'Pendiente',
                'Estado_Motorizado': 'Pendiente'
            }
            df_servicios = pd.concat([df_servicios, pd.DataFrame([nueva_fila])], ignore_index=True)
            df_servicios.to_csv(FILE_SERVICIOS, index=False)
            st.success(f"¡Vuelta #{nuevo_id} enviada! Quedó en espera de validación.")
            st.rerun()
        else:
            st.error("Ingresa el destino de la carrera.")

# ---------------------------------------------------------
# TAB 2: VALIDAR PRECIOS (ADMINISTRADOR)
# ---------------------------------------------------------
with tab2:
    st.subheader("Validación de Vueltas por el Administrador")
    
    vueltas_pendientes = df_servicios[df_servicios['Estado_Validacion'] == 'Pendiente']
    
    if not vueltas_pendientes.empty:
        for idx, row in vueltas_pendientes.iterrows():
            with st.expander(f"Vuelta #{row['ID']} - {row['Motorizado']} -> {row['Cliente']} ({row['Origen']} a {row['Destino']})", expanded=True):
                st.write(f"**Fecha:** {row['Fecha']} | **Detalle:** {row['Detalle']}")
                
                # Obtener porcentaje predeterminado del perfil del motorizado
                com_base = df_motorizados.loc[df_motorizados['Nombre'] == row['Motorizado'], 'Comision_Base'].values
                com_val = float(com_base[0]) if len(com_base) > 0 else 66.67
                
                col_v1, col_v2 = st.columns(2)
                with col_v1:
                    precio = st.number_input(f"Precio Cliente ($) [ID #{row['ID']}]", min_value=0.0, value=0.0, step=0.50, key=f"p_{row['ID']}")
                with col_v2:
                    comision = st.number_input(f"% Comisión [ID #{row['ID']}]", min_value=0.0, max_value=100.0, value=com_val, step=1.0, key=f"c_{row['ID']}")
                
                monto_moto = round(precio * (comision / 100.0), 2)
                ganancia_emp = round(precio - monto_moto, 2)
                
                st.write(f"Pago Chofer: **${monto_moto:.2f}** | Ganancia MotoVueltas: **${ganancia_emp:.2f}**")
                
                if st.button(f"Validar Vuelta #{row['ID']}", type="primary", key=f"btn_{row['ID']}"):
                    if precio > 0:
                        df_servicios.loc[df_servicios['ID'] == row['ID'], [
                            'Precio_Cliente', 'Porcentaje_Comision', 'Monto_Motorizado', 
                            'Ganancia_Empresa', 'Estado_Validacion'
                        ]] = [precio, comision, monto_moto, ganancia_emp, 'Validado']
                        
                        df_servicios.to_csv(FILE_SERVICIOS, index=False)
                        st.success(f"Vuelta #{row['ID']} validada correctamente.")
                        st.rerun()
                    else:
                        st.error("Ingresa un precio mayor a $0 para validar.")
    else:
        st.info("No hay vueltas pendientes por validar.")

# ---------------------------------------------------------
# TAB 3: CORTE CLIENTES Y WHATSAPP
# ---------------------------------------------------------
with tab3:
    st.subheader("Corte de Cuenta Clientes")
    validados_cli = df_servicios[(df_servicios['Estado_Validacion'] == 'Validado') & (df_servicios['Estado_Cliente'] == 'Pendiente')]
    
    if not validados_cli.empty:
        cli_corte = st.selectbox("Cliente", validados_cli['Cliente'].unique())
        df_c = validados_cli[validados_cli['Cliente'] == cli_corte]
        
        total_deuda = df_c['Precio_Cliente'].sum()
        st.metric("Total Deuda", f"${total_deuda:.2f}")
        st.dataframe(df_c[['ID', 'Fecha', 'Origen', 'Destino', 'Detalle', 'Precio_Cliente']], use_container_width=True)
        
        msj = f"*MOTOVUELTAS - Resumen de Cuenta*\nCliente: *{cli_corte}*\n---\n"
        for _, r in df_c.iterrows():
            msj += f"• Vuelta #{r['ID']} ({r['Origen']} -> {r['Destino']}): ${r['Precio_Cliente']:.2f}\n"
        msj += f"---\n*TOTAL A PAGAR: ${total_deuda:.2f}*"
        
        st.text_area("Mensaje de WhatsApp:", msj, height=150)
        
        if st.button(f"Marcar Deuda de {cli_corte} como PAGADA", type="primary"):
            df_servicios.loc[(df_servicios['Cliente'] == cli_corte) & (df_servicios['Estado_Cliente'] == 'Pendiente'), 'Estado_Cliente'] = 'Pagado'
            df_servicios.to_csv(FILE_SERVICIOS, index=False)
            st.success("Corte realizado.")
            st.rerun()
    else:
        st.info("Sin cuentas pendientes por cobrar a clientes.")

# ---------------------------------------------------------
# TAB 4: LIQUIDACIÓN MOTORIZADOS
# ---------------------------------------------------------
with tab4:
    st.subheader("Liquidación a Choferes")
    validados_mot = df_servicios[(df_servicios['Estado_Validacion'] == 'Validado') & (df_servicios['Estado_Motorizado'] == 'Pendiente')]
    
    if not validados_mot.empty:
        mot_corte = st.selectbox("Motorizado", validados_mot['Motorizado'].unique())
        df_m = validados_mot[validados_mot['Motorizado'] == mot_corte]
        
        total_pago = df_m['Monto_Motorizado'].sum()
        st.metric("Total a Pagar", f"${total_pago:.2f}")
        st.dataframe(df_m[['ID', 'Fecha', 'Cliente', 'Origen', 'Destino', 'Monto_Motorizado']], use_container_width=True)
        
        if st.button(f"Liquidar a {mot_corte}", type="primary"):
            df_servicios.loc[(df_servicios['Motorizado'] == mot_corte) & (df_servicios['Estado_Motorizado'] == 'Pendiente'), 'Estado_Motorizado'] = 'Pagado'
            df_servicios.to_csv(FILE_SERVICIOS, index=False)
            st.success("Pago registrado.")
            st.rerun()
    else:
        st.info("Sin liquidaciones pendientes a choferes.")

# ---------------------------------------------------------
# TAB 5: DIRECTORIO DE CLIENTES
# ---------------------------------------------------------
with tab5:
    st.subheader("Directorio de Clientes")
    st.dataframe(df_clientes, use_container_width=True)
    
    # SECCIÓN PARA EDITAR CLIENTE EXISTENTE
    if not df_clientes.empty:
        st.write("---")
        st.write("### ✏️ Editar / Actualizar Cliente Existente")
        cliente_a_editar = st.selectbox("Seleccionar Cliente a Modificar", df_clientes['Nombre'].tolist())
        
        # Obtener datos actuales del cliente seleccionado
        datos_cli = df_clientes[df_clientes['Nombre'] == cliente_a_editar].iloc[0]
        
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            edit_tel = st.text_input("Teléfono / WhatsApp", value=str(datos_cli.get('Telefono', '')))
        with col_e2:
            edit_ubicacion = st.text_input("Ubicación / Dirección Referencial", value=str(datos_cli.get('Ubicacion', '')))
            
        if st.button("Actualizar Datos del Cliente", type="primary"):
            # Actualización columna por columna para evitar el TypeError de Pandas
            idx = df_clientes[df_clientes['Nombre'] == cliente_a_editar].index
            df_clientes.loc[idx, 'Telefono'] = edit_tel.strip()
            df_clientes.loc[idx, 'Ubicacion'] = edit_ubicacion.strip()
            
            df_clientes.to_csv(FILE_CLIENTES, index=False)
            st.success(f"¡Datos de '{cliente_a_editar}' actualizados correctamente!")
            st.rerun()

    # SECCIÓN PARA AGREGAR NUEVO CLIENTE
    st.write("---")
    st.write("### ➕ Agregar Nuevo Cliente")
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        nuevo_cli_nombre = st.text_input("Nombre / Negocio")
    with col_c2:
        nuevo_cli_tel = st.text_input("Teléfono / WhatsApp (Nuevo)")
    with col_c3:
        nuevo_cli_ubicacion = st.text_input("Ubicación / Dirección (Nuevo)")
        
    if st.button("Guardar Nuevo Cliente"):
        if nuevo_cli_nombre.strip():
            nuevo_registro_cli = {
                "Nombre": nuevo_cli_nombre.strip(), 
                "Telefono": nuevo_cli_tel.strip(),
                "Ubicacion": nuevo_cli_ubicacion.strip() if nuevo_cli_ubicacion.strip() else "-"
            }
            df_clientes = pd.concat([df_clientes, pd.DataFrame([nuevo_registro_cli])], ignore_index=True)
            df_clientes.to_csv(FILE_CLIENTES, index=False)
            st.success(f"Cliente '{nuevo_cli_nombre}' agregado con éxito.")
            st.rerun()
        else:
            st.error("Por favor ingresa al menos el nombre del cliente.")

# ---------------------------------------------------------
# TAB 6: PERFILES DE MOTORIZADOS
# ---------------------------------------------------------
with tab6:
    st.subheader("Perfiles y Comisiones Base")
    st.dataframe(df_motorizados, use_container_width=True)
    
    st.write("---")
    st.write("### Agregar Nuevo Motorizado")
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        nuevo_mot_nombre = st.text_input("Nombre del Chofer")
    with col_m2:
        nuevo_mot_com = st.number_input("% Comisión Predeterminada", min_value=0.0, max_value=100.0, value=66.67, step=1.0)
        
    if st.button("Guardar Motorizado"):
        if nuevo_mot_nombre.strip():
            df_motorizados = pd.concat([df_motorizados, pd.DataFrame([{"Nombre": nuevo_mot_nombre.strip(), "Comision_Base": nuevo_mot_com}])], ignore_index=True)
            df_motorizados.to_csv(FILE_MOTORIZADOS, index=False)
            st.success(f"Motorizado '{nuevo_mot_nombre}' registrado.")
            st.rerun()
