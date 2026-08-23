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
# TAB 1: REGISTRAR VUELTA (FECHA, MOTORIZADO Y COMISIÓN ARRIBA)
# ---------------------------------------------------------
with tab1:
    st.subheader("Agregar Vuelta")
    
    # 1. Fila superior fija: Fecha, Motorizado y Porcentaje de Comisión
    col_top1, col_top2, col_top3 = st.columns(3)
    
    with col_top1:
        fecha_operativa = st.date_input("Fecha de las carreras", key="fecha_carreras_fija", format="DD/MM/YYYY")
        
    with col_top2:
        lista_motos = df_motorizados['Nombre'].tolist()
        moto_sel = st.selectbox("Motorizado", lista_motos, key="moto_carreras_fija")
        
    with col_top3:
        # Obtener la comisión por defecto registrada del motorizado seleccionado
        com_base_sug = df_motorizados.loc[df_motorizados['Nombre'] == moto_sel, 'Comision_Base'].values
        val_default = float(com_base_sug[0]) if len(com_base_sug) > 0 else 66.67
        
        # Campo porcentual ajustable manualmente
        porcentaje_actual = st.number_input(
            "Comisión Motorizado (%)", 
            min_value=0.0, 
            max_value=100.0, 
            value=val_default, 
            step=0.5,
            key=f"comision_input_{moto_sel}"
        )

    # 2. Formulario de la carrera (se limpia tras guardar)
    with st.form("form_agregar_vuelta", clear_on_submit=True):
        lista_cli = [""] + df_clientes['Nombre'].tolist()
        cli_sel = st.selectbox("Seleccionar Cliente", lista_cli, index=0)
        
        col1, col2 = st.columns(2)
        with col1:
            origen = st.text_input("Desde", placeholder="Local")
        with col2:
            destino = st.text_input("Hasta", placeholder="Local")

        precio_directo = st.number_input("Precio Cliente ($) (Opcional - Valida de inmediato si > 0)", min_value=0.0, value=0.0, step=0.50)

        guardar_btn = st.form_submit_button("Guardar Vuelta", type="primary", use_container_width=True)

    if guardar_btn:
        if destino.strip() or origen.strip():
            nuevo_id = len(df_servicios) + 1
            fecha_final = f"{fecha_operativa} {datetime.now().strftime('%H:%M')}"
            
            origen_final = origen.strip() if origen.strip() else "Local"
            destino_final = destino.strip() if destino.strip() else "Local"
            cliente_final = cli_sel if cli_sel else "Cliente General"
            
            # Usar el porcentaje definido en el campo superior
            comision_val = round(float(porcentaje_actual), 2)
            
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
                'Cliente': cliente_final,
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
            
            if estado_val == "Validado":
                st.success(f"✅ ¡Vuelta #{nuevo_id} guardada al {comision_val}% y VALIDADA por ${precio_directo:.2f}!")
            else:
                st.info(f"ℹ️ Vuelta #{nuevo_id} guardada al {comision_val}% (Pendiente por precio).")
                
            st.toast(f"✅ Vuelta #{nuevo_id} registrada con éxito", icon="🛵")
        else:
            st.error("⚠️ Debes ingresar al menos el destino de la carrera.") 
            
# ---------------------------------------------------------
# TAB 2: VALIDAR PRECIOS Y EDITAR VUELTAS (3 FILTROS INCLUIDOS)
# ---------------------------------------------------------
with tab2:
    st.subheader("Validación y Corrección de Vueltas")
    
    # 1. VUELTAS PENDIENTES POR VALIDAR
    st.write("### 📋 Vueltas Pendientes por Validar")
    vueltas_pendientes = df_servicios[df_servicios['Estado_Validacion'] == 'Pendiente']
    if not vueltas_pendientes.empty:
        for idx, row in vueltas_pendientes.iterrows():
            with st.expander(f"Vuelta #{row['ID']} - {row['Motorizado']} -> {row['Cliente']} ({row['Origen']} a {row['Destino']})", expanded=True):
                st.write(f"**Fecha:** {row['Fecha']} | **Detalle:** {row['Detalle']}")
                com_base = df_motorizados.loc[df_motorizados['Nombre'] == row['Motorizado'], 'Comision_Base'].values
                com_val = float(com_base[0]) if len(com_base) > 0 else 66.67
                
                col_v1, col_v2 = st.columns(2)
                with col_v1:
                    precio = st.number_input(f"Precio Cliente ($) [ID #{row['ID']}]", min_value=0.0, value=0.0, step=0.50, key=f"p_{row['ID']}")
                with col_v2:
                    comision = st.number_input(f"% Comisión [ID #{row['ID']}]", min_value=0.0, max_value=100.0, value=com_val, step=0.5, key=f"c_{row['ID']}")
                
                monto_moto = round(precio * (comision / 100.0), 2)
                ganancia_emp = round(precio - monto_moto, 2)
                st.write(f"Pago Chofer: **${monto_moto:.2f}** | Ganancia MotoVueltas: **${ganancia_emp:.2f}**")
                
                if st.button(f"Validar Vuelta #{row['ID']}", type="primary", key=f"btn_{row['ID']}"):
                    if precio > 0:
                        df_servicios.loc[df_servicios['ID'] == row['ID'], ['Precio_Cliente', 'Porcentaje_Comision', 'Monto_Motorizado', 'Ganancia_Empresa', 'Estado_Validacion']] = [precio, comision, monto_moto, ganancia_emp, 'Validado']
                        df_servicios.to_csv(FILE_SERVICIOS, index=False)
                        st.success(f"Vuelta #{row['ID']} validada correctamente.")
                        st.rerun()
                    else:
                        st.error("Ingresa un precio mayor a $0 para validar.")
    else:
        st.info("No hay vueltas pendientes por validar.")

    # 2. EDITAR VUELTAS YA REGISTRADAS (FILTROS POR MOTORIZADO, CLIENTE Y FECHA)
    if not df_servicios.empty:
        st.write("---")
        st.write("### ✏️ Corregir/Editar Vueltas Ya Registradas")
        
        # Filtros de búsqueda en 3 columnas
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            lista_mots_filtro = ["Todos"] + sorted(df_servicios['Motorizado'].dropna().unique().tolist())
            filtro_moto = st.selectbox("Filtrar por Motorizado", lista_mots_filtro, key="f_moto_tab2")
        with col_f2:
            lista_clis_filtro = ["Todos"] + sorted(df_servicios['Cliente'].dropna().unique().tolist())
            filtro_cliente = st.selectbox("Filtrar por Cliente", lista_clis_filtro, key="f_cli_tab2")
        with col_f3:
            filtro_fecha = st.date_input("Filtrar por Fecha", value=None, key="f_fecha_tab2")

        # Aplicar filtros acumulativos sobre el DataFrame
        df_filtrado = df_servicios.copy()
        
        if filtro_moto != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Motorizado'] == filtro_moto]
            
        if filtro_cliente != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Cliente'] == filtro_cliente]
            
        if filtro_fecha is not None:
            fecha_str = filtro_fecha.strftime("%Y-%m-%d")
            df_filtrado = df_filtrado[df_filtrado['Fecha'].astype(str).str.startswith(fecha_str)]

        if not df_filtrado.empty:
            df_filtrado['Label_Edit'] = "Vuelta #" + df_filtrado['ID'].astype(str) + " - " + df_filtrado['Motorizado'] + " (" + df_filtrado['Cliente'] + ") - $" + df_filtrado['Precio_Cliente'].astype(str) + " [" + df_filtrado['Fecha'].astype(str) + "]"
            lista_opciones = df_filtrado['Label_Edit'].tolist()
            
            vuelta_sel_label = st.selectbox("Selecciona la Vuelta a Modificar", lista_opciones, key="sel_vuelta_edit")
            idx_edit = df_filtrado[df_filtrado['Label_Edit'] == vuelta_sel_label].index[0]
            row_edit = df_servicios.loc[idx_edit]
            
            # Formulario de edición
            col_ed1, col_ed2 = st.columns(2)
            with col_ed1:
                # Modificar Motorizado
                lista_motos_edit = df_motorizados['Nombre'].tolist()
                idx_m = lista_motos_edit.index(row_edit['Motorizado']) if row_edit['Motorizado'] in lista_motos_edit else 0
                edit_moto = st.selectbox("Cambiar Motorizado", lista_motos_edit, index=idx_m, key=f"edit_m_{row_edit['ID']}")
                
                # Modificar Cliente
                lista_cli_edit = df_clientes['Nombre'].tolist()
                idx_c = lista_cli_edit.index(row_edit['Cliente']) if row_edit['Cliente'] in lista_cli_edit else 0
                edit_cliente = st.selectbox("Cambiar Cliente", lista_cli_edit, index=idx_c, key=f"edit_cli_{row_edit['ID']}")

            with col_ed2:
                edit_precio = st.number_input("Precio Cliente ($)", min_value=0.0, value=float(row_edit['Precio_Cliente']), step=0.50, key=f"edit_p_{row_edit['ID']}")
                edit_comision = st.number_input("% Comisión Motorizado", min_value=0.0, max_value=100.0, value=float(row_edit['Porcentaje_Comision']), step=0.5, key=f"edit_c_{row_edit['ID']}")

            nuevo_monto_moto = round(edit_precio * (edit_comision / 100.0), 2)
            nueva_ganancia = round(edit_precio - nuevo_monto_moto, 2)
            
            st.caption(f"💡 Nuevo Pago Chofer: **${nuevo_monto_moto:.2f}** | Nueva Ganancia Empresa: **${nueva_ganancia:.2f}**")

            if st.button("Guardar Cambios de esta Vuelta", type="primary", key=f"btn_save_{row_edit['ID']}"):
                df_servicios.at[idx_edit, 'Motorizado'] = edit_moto
                df_servicios.at[idx_edit, 'Cliente'] = edit_cliente
                df_servicios.at[idx_edit, 'Precio_Cliente'] = edit_precio
                df_servicios.at[idx_edit, 'Porcentaje_Comision'] = edit_comision
                df_servicios.at[idx_edit, 'Monto_Motorizado'] = nuevo_monto_moto
                df_servicios.at[idx_edit, 'Ganancia_Empresa'] = nueva_ganancia
                
                if 'Label_Edit' in df_servicios.columns:
                    df_servicios = df_servicios.drop(columns=['Label_Edit'])
                    
                df_servicios.to_csv(FILE_SERVICIOS, index=False)
                st.toast(f"✅ Vuelta #{row_edit['ID']} actualizada correctamente", icon="✏️")
                st.rerun()
        else:
            st.info("No se encontraron vueltas que coincidan con los filtros seleccionados.")

# ---------------------------------------------------------
# TAB 3: CORTE CLIENTES Y WHATSAPP CON FILTRO DE FECHAS
# ---------------------------------------------------------
with tab3:
    st.subheader("Corte de Cuenta Clientes")
    
    validados_cli = df_servicios[(df_servicios['Estado_Validacion'] == 'Validado') & (df_servicios['Estado_Cliente'] == 'Pendiente')]
    
    if not validados_cli.empty:
        # 1. Filtros principales: Cliente y Rango de Fechas
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            cli_corte = st.selectbox("Seleccionar Cliente", validados_cli['Cliente'].unique(), key="sel_cli_tab3")
        with col_c2:
            f_inicio = st.date_input("Fecha Desde", value=None, key="f_ini_tab3")
        with col_c3:
            f_fin = st.date_input("Fecha Hasta", value=None, key="f_fin_tab3")

        # 2. Filtrar DataFrame por cliente
        df_c = validados_cli[validados_cli['Cliente'] == cli_corte].copy()
        
        # Convertir columna Fecha a objeto datetime para filtrado preciso
        df_c['Fecha_dt'] = pd.to_datetime(df_c['Fecha'].astype(str).str[:10], errors='coerce')

        # Aplicar filtro por rango de fechas
        if f_inicio is not None:
            df_c = df_c[df_c['Fecha_dt'] >= pd.to_datetime(f_inicio)]
        if f_fin is not None:
            df_c = df_c[df_c['Fecha_dt'] <= pd.to_datetime(f_fin)]

        if not df_c.empty:
            total_deuda = df_c['Precio_Cliente'].sum()
            st.metric("Total Deuda Período", f"${total_deuda:.2f}")

            # 3. Cuadro / Tabla en tiempo real (Fecha, Motorizado, Origen, Destino, Precio)
            st.write("##### 📋 Carreras del Período")
            st.dataframe(
                df_c[['Fecha', 'Motorizado', 'Origen', 'Destino', 'Precio_Cliente']], 
                use_container_width=True
            )

            # 4. Generación del mensaje para WhatsApp
            msj = f"*MOTOVUELTAS - Resumen de Cuenta*\nCliente: *{cli_corte}*\n---\n"
            for _, r in df_c.iterrows():
                try:
                    fecha_corta = pd.to_datetime(str(r['Fecha']).split()[0]).strftime('%d/%m')
                except:
                    fecha_corta = str(r['Fecha'])[:5]
                msj += f"• [{fecha_corta}] {r['Motorizado']} | {r['Origen']} -> {r['Destino']}: ${r['Precio_Cliente']:.2f}\n"

            msj += f"---\n*TOTAL A PAGAR: ${total_deuda:.2f}*"

            st.text_area("Mensaje de WhatsApp para enviar:", msj, height=180)

            # 5. Marcar como pagadas únicamente las vueltas filtradas
            if st.button(f"Marcar {len(df_c)} Vueltas de {cli_corte} como PAGADAS", type="primary"):
                ids_a_pagar = df_c['ID'].tolist()
                df_servicios.loc[df_servicios['ID'].isin(ids_a_pagar), 'Estado_Cliente'] = 'Pagado'
                df_servicios.to_csv(FILE_SERVICIOS, index=False)
                st.success("Corte del período registrado y guardado.")
                st.rerun()
        else:
            st.warning("No hay vueltas registradas para este cliente en el rango de fechas seleccionado.")
    else:
        st.info("Sin cuentas pendientes por cobrar a clientes.")

# ---------------------------------------------------------
# TAB 4: LIQUIDACIÓN MOTORIZADOS CON GESTIÓN DE AVANCES
# ---------------------------------------------------------
with tab4:
    st.subheader("Liquidación a Choferes")
    
    FILE_AVANCES = "avances.csv"
    
    # Cargar o crear el DataFrame de avances en memoria
    if os.path.exists(FILE_AVANCES):
        df_avances = pd.read_csv(FILE_AVANCES)
    else:
        df_avances = pd.DataFrame(columns=['ID', 'Fecha', 'Motorizado', 'Monto', 'Concepto', 'Estado'])
        df_avances.to_csv(FILE_AVANCES, index=False)

    validados_mot = df_servicios[(df_servicios['Estado_Validacion'] == 'Validado') & (df_servicios['Estado_Motorizado'] == 'Pendiente')]
    
    if not validados_mot.empty:
        lista_motorizados_pendientes = validados_mot['Motorizado'].unique().tolist()
        mot_corte = st.selectbox("Seleccionar Motorizado", lista_motorizados_pendientes, key="mot_sel_liq")
        
        # 1. FORMULARIO PARA REGISTRAR AVANCE/ADELANTO
        with st.expander(f"➕ Registrar Avance / Adelanto a {mot_corte}", expanded=False):
            with st.form("form_nuevo_avance", clear_on_submit=True):
                col_a1, col_a2, col_a3 = st.columns(3)
                with col_a1:
                    f_avance = st.date_input("Fecha del Avance", key="f_av_input", format="DD/MM/YYYY")
                with col_a2:
                    monto_av = st.number_input("Monto Avance ($)", min_value=0.0, step=0.50, key="m_av_input")
                with col_a3:
                    concepto_av = st.text_input("Concepto (ej. Gasolina)", placeholder="Detalle corto", key="c_av_input")
                
                guardar_av_btn = st.form_submit_button("Guardar Avance", type="primary", use_container_width=True)
            
            if guardar_av_btn:
                if monto_av > 0:
                    nuevo_id_av = len(df_avances) + 1
                    nuevo_reg_av = {
                        'ID': nuevo_id_av,
                        'Fecha': f_avance.strftime("%d/%m/%Y"),
                        'Motorizado': mot_corte,
                        'Monto': float(monto_av),
                        'Concepto': concepto_av.strip() if concepto_av.strip() else "Adelanto",
                        'Estado': 'Pendiente'
                    }
                    df_avances = pd.concat([df_avances, pd.DataFrame([nuevo_reg_av])], ignore_index=True)
                    df_avances.to_csv(FILE_AVANCES, index=False)
                    st.toast(f"✅ Avance de ${monto_av:.2f} registrado a {mot_corte}", icon="💵")
                    st.rerun()
                else:
                    st.error("⚠️ El monto del avance debe ser mayor a $0.")

        # 2. CÁLCULOS Y MÉTRICAS
        df_m = validados_mot[validados_mot['Motorizado'] == mot_corte]
        total_vueltas = df_m['Monto_Motorizado'].sum()
        
        # Filtrar avances pendientes del motorizado
        df_av_mot = df_avances[(df_avances['Motorizado'] == mot_corte) & (df_avances['Estado'] == 'Pendiente')] if not df_avances.empty else pd.DataFrame()
        total_avances = df_av_mot['Monto'].sum() if not df_av_mot.empty else 0.0
        
        total_neto = total_vueltas - total_avances

        # Mostrar métricas agrupadas
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("Acumulado Vueltas", f"${total_vueltas:.2f}")
        m_col2.metric("Total Avances", f"-${total_avances:.2f}")
        m_col3.metric("Neto a Pagar", f"${total_neto:.2f}")

        # 3. TABLA DE AVANCES ENTREGADOS
        if not df_av_mot.empty:
            st.write("##### 💵 Avances Registrados en este Período")
            st.dataframe(df_av_mot[['Fecha', 'Monto', 'Concepto']], use_container_width=True)

        # 4. TABLA DE VUELTAS PENDIENTES
        st.write("##### 🛵 Vueltas del Período")
        st.dataframe(df_m[['ID', 'Fecha', 'Cliente', 'Origen', 'Destino', 'Monto_Motorizado']], use_container_width=True)

        # 5. BOTÓN DE LIQUIDACIÓN
        if st.button(f"Liquidar a {mot_corte} (${total_neto:.2f})", type="primary", use_container_width=True):
            # Marcar vueltas como Pagadas
            df_servicios.loc[(df_servicios['Motorizado'] == mot_corte) & (df_servicios['Estado_Motorizado'] == 'Pendiente'), 'Estado_Motorizado'] = 'Pagado'
            df_servicios.to_csv(FILE_SERVICIOS, index=False)
            
            # Marcar avances como Pagados
            if not df_avances.empty:
                df_avances.loc[(df_avances['Motorizado'] == mot_corte) & (df_avances['Estado'] == 'Pendiente'), 'Estado'] = 'Pagado'
                df_avances.to_csv(FILE_AVANCES, index=False)
                
            st.success(f"✅ Liquidación completada para {mot_corte}.")
            st.rerun()
    else:
        st.info("Sin liquidaciones pendientes a choferes.")
        
# ---------------------------------------------------------
# TAB 5: DIRECTORIO DE CLIENTES (FORMULARIO CON RESET NATIVO)
# ---------------------------------------------------------
with tab5:
    st.subheader("Directorio de Clientes")

    # 1. AGREGAR NUEVO CLIENTE (FORMULARIO DE RESET AUTOMÁTICO)
    st.write("### ➕ Agregar Nuevo Cliente")
    with st.form("form_agregar_cliente", clear_on_submit=True):
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            nuevo_cli_nombre = st.text_input("Nombre / Negocio")
        with col_c2:
            nuevo_cli_tel = st.text_input("Teléfono / WhatsApp (ID Único)")
        with col_c3:
            nuevo_cli_ubicacion = st.text_input("Ubicación / Dirección (Nuevo)")

        guardar_cli_btn = st.form_submit_button("Guardar Nuevo Cliente", type="primary", use_container_width=True)

    if guardar_cli_btn:
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

                st.success(f"✅ Cliente '{nom_limpio}' registrado con éxito.")
                st.toast(f"✅ Cliente '{nom_limpio}' registrado con éxito", icon="👤")
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
