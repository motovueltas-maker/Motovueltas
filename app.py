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
# TAB 1: REGISTRAR VUELTA (CON FORMULARIO Y RESET NATIVO)
# ---------------------------------------------------------
with tab1:
    st.subheader("Agregar Vuelta")
    
    fecha_operativa = st.date_input("Fecha de las carreras", key="fecha_carreras_fija", format="DD/MM/YYYY")
    
    # Formulario con limpieza automática al presionar enviar
    with st.form("form_agregar_vuelta", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            lista_motos = df_motorizados['Nombre'].tolist()
            moto_sel = st.selectbox("Motorizado", lista_motos)
            
            lista_cli = df_clientes['Nombre'].tolist()
            cli_sel = st.selectbox("Seleccionar Cliente", lista_cli)
            
        with col2:
            origen = st.text_input("Desde", placeholder="Local")
            destino = st.text_input("Hasta", placeholder="Local")

        precio_directo = st.number_input("Precio Cliente ($) (Opcional - Valida de inmediato si > 0)", min_value=0.0, value=0.0, step=0.50)

        guardar_btn = st.form_submit_button("Guardar Vuelta", type="primary", use_container_width=True)

    if guardar_btn:
        if destino.strip() or origen.strip():
            nuevo_id = len(df_servicios) + 1
            fecha_final = f"{fecha_operativa} {datetime.now().strftime('%H:%M')}"
            
            origen_final = origen.strip() if origen.strip() else "Local"
            destino_final = destino.strip() if destino.strip() else "Local"
            
            com_base = df_motorizados.loc[df_motorizados['Nombre'] == moto_sel, 'Comision_Base'].values
            comision_val = float(com_base[0]) if len(com_base) > 0 else 66.67
            
            if precio_directo > 0:
                monto_moto = round(precio_directo * (comision_val / 100.0), 2)
                ganancia_emp = round(precio_directo - monto_moto, 2)
                estado_val = "Validado"
            else:
                monto_moto = 0.0
                ganancia_emp = 0.0
                estado_val = "Pendiente"

            nueva_fila = {
                'ID': nuevo_id,
                'Fecha': fecha_final,
                'Motorizado': moto_sel,
                'Cliente': cli_sel,
                'Origen': origen_final,
                'Destino': destino_final,
                'Detalle': "-",
                'Precio_Cliente': precio_directo,
                'Porcentaje_Comision': comision_val,
                'Monto_Motorizado': monto_moto,
                'Ganancia_Empresa': ganancia_emp,
                'Estado_Validacion': estado_val,
                'Estado_Cliente': 'Pendiente',
                'Estado_Motorizado': 'Pendiente'
            }
            df_servicios = pd.concat([df_servicios, pd.DataFrame([nueva_fila])], ignore_index=True)
            df_servicios.to_csv(FILE_SERVICIOS, index=False)
            
            # Notificaciones inmediatas en pantalla
            if estado_val == "Validado":
                st.success(f"✅ ¡Vuelta #{nuevo_id} guardada y VALIDADA por ${precio_directo:.2f}!")
            else:
                st.info(f"ℹ️ Vuelta #{nuevo_id} guardada (Pendiente por validar precio).")
                
            st.toast(f"✅ Vuelta #{nuevo_id} registrada con éxito", icon="🛵")
        else:
            st.error("⚠️ Debes ingresar al menos el destino de la carrera.")
            
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
# TAB 5: DIRECTORIO DE CLIENTES (REORGANIZADO)
# ---------------------------------------------------------
with tab5:
    st.subheader("Directorio de Clientes")

    # 1. AGREGAR NUEVO CLIENTE (PRIMERO)
    st.write("### ➕ Agregar Nuevo Cliente")
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        nuevo_cli_nombre = st.text_input("Nombre / Negocio", key="nuevo_cli_nom_key")
    with col_c2:
        nuevo_cli_tel = st.text_input("Teléfono / WhatsApp (ID Único)", key="nuevo_cli_tel_key")
    with col_c3:
        nuevo_cli_ubicacion = st.text_input("Ubicación / Dirección (Nuevo)", key="nuevo_cli_ubi_key")

    if st.button("Guardar Nuevo Cliente", type="primary", use_container_width=True):
        tel_limpio = nuevo_cli_tel.strip()
        nom_limpio = nuevo_cli_nombre.strip()

        if not nom_limpio or not tel_limpio:
            st.error("⚠️ Tanto el Nombre como el Teléfono son obligatorios.")
        else:
            # Validación anti-duplicados por número telefónico
            telefonos_existentes = df_clientes['Telefono'].astype(str).str.strip().tolist() if not df_clientes.empty else []
            if tel_limpio in telefonos_existentes:
                st.error(f"❌ Ya existe un cliente registrado con el teléfono {tel_limpio}. No se permiten duplicados.")
            else:
                nuevo_registro_cli = {
                    "Nombre": nom_limpio,
                    "Telefono": tel_limpio,
                    "Ubicacion": nuevo_cli_ubicacion.strip() if nuevo_cli_ubicacion.strip() else "-"
                }
                df_clientes = pd.concat([df_clientes, pd.DataFrame([nuevo_registro_cli])], ignore_index=True)
                df_clientes.to_csv(FILE_CLIENTES, index=False)

                # Notificación flotante de confirmación
                st.toast(f"✅ Cliente '{nom_limpio}' registrado con éxito", icon="👤")
                
                # Eliminación segura de las claves para que los campos vuelvan limpios
                del st.session_state["nuevo_cli_nom_key"]
                del st.session_state["nuevo_cli_tel_key"]
                del st.session_state["nuevo_cli_ubi_key"]

                st.rerun()

    # 2. EDITAR / ACTUALIZAR CLIENTE EXISTENTE (SEGUNDO)
    if not df_clientes.empty:
        st.write("---")
        st.write("### ✏️ Editar / Actualizar Cliente Existente")
        df_clientes['Select_Label'] = df_clientes['Nombre'] + " (" + df_clientes['Telefono'].astype(str) + ")"
        opciones_clientes = df_clientes['Select_Label'].tolist()
        cliente_sel_label = st.selectbox("Seleccionar Cliente a Modificar", opciones_clientes)

        idx_seleccionado = df_clientes[df_clientes['Select_Label'] == cliente_sel_label].index[0]
        datos_cli = df_clientes.loc[idx_seleccionado]

        col_e1, col_e2, col_e3 = st.columns(3)
        with col_e1:
            edit_nombre = st.text_input("Editar Nombre", value=str(datos_cli.get('Nombre', '')))
        with col_e2:
            edit_tel = st.text_input("Editar Teléfono", value=str(datos_cli.get('Telefono', '')))
        with col_e3:
            edit_ubicacion = st.text_input("Editar Ubicación", value=str(datos_cli.get('Ubicacion', '')))

        if st.button("Guardar Cambios del Cliente"):
            edit_tel_limpio = edit_tel.strip()
            otros_telefonos = df_clientes.drop(idx_seleccionado)['Telefono'].astype(str).str.strip().tolist()

            if edit_tel_limpio in otros_telefonos:
                st.error(f"❌ El número {edit_tel_limpio} ya pertenece a otro cliente registrado.")
            else:
                df_clientes.at[idx_seleccionado, 'Nombre'] = edit_nombre.strip()
                df_clientes.at[idx_seleccionado, 'Telefono'] = edit_tel_limpio
                df_clientes.at[idx_seleccionado, 'Ubicacion'] = edit_ubicacion.strip()

                if 'Select_Label' in df_clientes.columns:
                    df_clientes = df_clientes.drop(columns=['Select_Label'])

                df_clientes.to_csv(FILE_CLIENTES, index=False)
                st.toast("✅ Datos del cliente actualizados exitosamente", icon="✏️")
                st.rerun()

    # 3. BASE DE DATOS VISUAL (TERCERO)
    st.write("---")
    st.write("### 📊 Base de Datos de Clientes")
    st.dataframe(df_clientes[['Nombre', 'Telefono', 'Ubicacion']], use_container_width=True)

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
