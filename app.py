import streamlit as st
import pandas as pd
import os
from datetime import datetime
import urllib.parse  # <--- Agrega esta línea aquí

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

# 1. Menú lateral fijo
opcion_menu = st.sidebar.radio(
    "📌 Menú de Navegación",
    [
        "🛵 Registrar Vuelta",
        "✅ Validar Precios",
        "💵 Corte Clientes",
        "🏍️ Liquidación Motorizados",
        "👥 Directorio Clientes",
        "⚙️ Perfiles Motorizados"
    ]
)

# 2. Control de pantallas según la selección
if opcion_menu == "🛵 Registrar Vuelta":
    st.subheader("Agregar Vuelta")
    # Pega aquí todo el código que estaba dentro de 'with tab1:' (sin tab1)

elif opcion_menu == "✅ Validar Precios":
    st.subheader("Validación y Corrección de Vueltas")
    # Pega aquí todo el código de 'with tab2:'

elif opcion_menu == "💵 Corte Clientes":
    st.subheader("Corte de Cuenta Clientes")
    # Pega aquí todo el código de 'with tab3:'

elif opcion_menu == "🏍️ Liquidación Motorizados":
    # Pega aquí todo el código de 'with tab4:'

elif opcion_menu == "👥 Directorio Clientes":
    # Pega aquí todo el código de 'with tab5:'

elif opcion_menu == "⚙️ Perfiles Motorizados":
    # Pega aquí todo el código de 'with tab6:'

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
# TAB 2: VALIDAR PRECIOS Y EDITAR VUELTAS CON VISUALIZACIÓN
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

    # 2. EDITAR VUELTAS CON VISUALIZACIÓN EN TIEMPO REAL
    if not df_servicios.empty:
        st.write("---")
        st.write("### ✏️ Corregir/Editar Vueltas Ya Registradas")
        
        # Filtros de búsqueda (Motorizado, Cliente, Rango de Fechas)
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        with col_f1:
            lista_mots_filtro = ["Todos"] + sorted(df_servicios['Motorizado'].dropna().unique().tolist())
            filtro_moto = st.selectbox("Filtrar por Motorizado", lista_mots_filtro, key="f_moto_tab2")
        with col_f2:
            lista_clis_filtro = ["Todos"] + sorted(df_servicios['Cliente'].dropna().unique().tolist())
            filtro_cliente = st.selectbox("Filtrar por Cliente", lista_clis_filtro, key="f_cli_tab2")
        with col_f3:
            filtro_f_ini = st.date_input("Fecha Desde", value=None, key="f_ini_tab2")
        with col_f4:
            filtro_f_fin = st.date_input("Fecha Hasta", value=None, key="f_fin_tab2")

        # Aplicar filtros
        df_filtrado = df_servicios.copy()
        df_filtrado['Fecha_dt'] = pd.to_datetime(df_filtrado['Fecha'].astype(str).str[:10], errors='coerce')

        if filtro_moto != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Motorizado'] == filtro_moto]
        if filtro_cliente != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Cliente'] == filtro_cliente]
        if filtro_f_ini is not None:
            df_filtrado = df_filtrado[df_filtrado['Fecha_dt'] >= pd.to_datetime(filtro_f_ini)]
        if filtro_f_fin is not None:
            df_filtrado = df_filtrado[df_filtrado['Fecha_dt'] <= pd.to_datetime(filtro_f_fin)]

        if not df_filtrado.empty:
            # 📊 MOSTRAR TABLA EN TIEMPO REAL
            st.write(f"##### 📋 Vueltas encontradas ({len(df_filtrado)})")
            df_display = df_filtrado[['ID', 'Fecha', 'Motorizado', 'Cliente', 'Origen', 'Destino', 'Precio_Cliente', 'Porcentaje_Comision']].copy()
            df_display.columns = ['ID', 'Fecha', 'Motorizado', 'Cliente', 'Origen', 'Destino', 'Precio ($)', '% Com.']
            st.dataframe(df_display, use_container_width=True)

            # Selección de la vuelta a corregir
            df_filtrado['Label_Edit'] = "Vuelta #" + df_filtrado['ID'].astype(str) + " - " + df_filtrado['Motorizado'] + " (" + df_filtrado['Cliente'] + ") - $" + df_filtrado['Precio_Cliente'].astype(str) + " [" + df_filtrado['Fecha'].astype(str) + "]"
            lista_opciones = df_filtrado['Label_Edit'].tolist()
            
            vuelta_sel_label = st.selectbox("Selecciona la Vuelta a Modificar", lista_opciones, key="sel_vuelta_edit")
            idx_edit = df_filtrado[df_filtrado['Label_Edit'] == vuelta_sel_label].index[0]
            row_edit = df_servicios.loc[idx_edit]
            
            st.markdown(f"**Editando detalles de la Vuelta #{row_edit['ID']}**")

            # Formulario de edición
            c_e1, c_e2, c_e3 = st.columns(3)
            with c_e1:
                try:
                    fecha_orig = datetime.strptime(str(row_edit['Fecha'])[:10], "%Y-%m-%d").date()
                except:
                    fecha_orig = datetime.now().date()
                edit_fecha = st.date_input("Fecha", value=fecha_orig, key=f"edit_fec_{row_edit['ID']}", format="DD/MM/YYYY")

            with c_e2:
                lista_motos_edit = df_motorizados['Nombre'].tolist()
                idx_m = lista_motos_edit.index(row_edit['Motorizado']) if row_edit['Motorizado'] in lista_motos_edit else 0
                edit_moto = st.selectbox("Cambiar Motorizado", lista_motos_edit, index=idx_m, key=f"edit_m_{row_edit['ID']}")

            with c_e3:
                lista_cli_edit = df_clientes['Nombre'].tolist()
                idx_c = lista_cli_edit.index(row_edit['Cliente']) if row_edit['Cliente'] in lista_cli_edit else 0
                edit_cliente = st.selectbox("Cambiar Cliente", lista_cli_edit, index=idx_c, key=f"edit_cli_{row_edit['ID']}")

            c_e4, c_e5, c_e6, c_e7 = st.columns(4)
            with c_e4:
                edit_origen = st.text_input("Desde", value=str(row_edit.get('Origen', 'Local')), key=f"edit_orig_{row_edit['ID']}")
            with c_e5:
                edit_destino = st.text_input("Hasta", value=str(row_edit.get('Destino', 'Local')), key=f"edit_dest_{row_edit['ID']}")
            with c_e6:
                edit_precio = st.number_input("Precio ($)", min_value=0.0, value=float(row_edit['Precio_Cliente']), step=0.50, key=f"edit_p_{row_edit['ID']}")
            with c_e7:
                edit_comision = st.number_input("% Comisión", min_value=0.0, max_value=100.0, value=float(row_edit['Porcentaje_Comision']), step=0.5, key=f"edit_c_{row_edit['ID']}")

            nuevo_monto_moto = round(edit_precio * (edit_comision / 100.0), 2)
            nueva_ganancia = round(edit_precio - nuevo_monto_moto, 2)
            
            st.caption(f"💡 Nuevo Pago Chofer: **${nuevo_monto_moto:.2f}** | Nueva Ganancia Empresa: **${nueva_ganancia:.2f}**")

            if st.button("Guardar Cambios de esta Vuelta", type="primary", key=f"btn_save_{row_edit['ID']}"):
                hora_str = str(row_edit['Fecha'])[11:] if len(str(row_edit['Fecha'])) > 10 else datetime.now().strftime('%H:%M')
                fecha_actualizada = f"{edit_fecha} {hora_str}".strip()

                df_servicios.at[idx_edit, 'Fecha'] = fecha_actualizada
                df_servicios.at[idx_edit, 'Motorizado'] = edit_moto
                df_servicios.at[idx_edit, 'Cliente'] = edit_cliente
                df_servicios.at[idx_edit, 'Origen'] = edit_origen.strip() if edit_origen.strip() else "Local"
                df_servicios.at[idx_edit, 'Destino'] = edit_destino.strip() if edit_destino.strip() else "Local"
                df_servicios.at[idx_edit, 'Precio_Cliente'] = edit_precio
                df_servicios.at[idx_edit, 'Porcentaje_Comision'] = edit_comision
                df_servicios.at[idx_edit, 'Monto_Motorizado'] = nuevo_monto_moto
                df_servicios.at[idx_edit, 'Ganancia_Empresa'] = nueva_ganancia
                
                if 'Label_Edit' in df_servicios.columns:
                    df_servicios = df_servicios.drop(columns=['Label_Edit'])
                if 'Fecha_dt' in df_servicios.columns:
                    df_servicios = df_servicios.drop(columns=['Fecha_dt'])
                    
                df_servicios.to_csv(FILE_SERVICIOS, index=False)
                st.toast(f"✅ Vuelta #{row_edit['ID']} corregida completamente", icon="✏️")
                st.rerun()
        else:
            st.info("No se encontraron vueltas que coincidan con los filtros seleccionados.")

# ---------------------------------------------------------
# TAB 3: CORTE CLIENTES, ABONOS Y ENVÍO DIRECTO A WHATSAPP
# ---------------------------------------------------------
with tab3:
    st.subheader("Corte de Cuenta Clientes")
    
    FILE_ABONOS = "abonos_clientes.csv"
    
    if os.path.exists(FILE_ABONOS):
        df_abonos = pd.read_csv(FILE_ABONOS)
    else:
        df_abonos = pd.DataFrame(columns=['ID', 'Fecha', 'Cliente', 'Monto', 'Concepto', 'Estado'])
        df_abonos.to_csv(FILE_ABONOS, index=False)

    validados_cli = df_servicios[(df_servicios['Estado_Validacion'] == 'Validado') & (df_servicios['Estado_Cliente'] == 'Pendiente')]
    
    if not validados_cli.empty:
        # 1. Filtros principales: Cliente y Rango de Fechas
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            cli_corte = st.selectbox("Seleccionar Cliente", sorted(validados_cli['Cliente'].unique().tolist()), key="sel_cli_tab3")
        with col_c2:
            f_inicio = st.date_input("Fecha Desde", value=None, key="f_ini_tab3")
        with col_c3:
            f_fin = st.date_input("Fecha Hasta", value=None, key="f_fin_tab3")

        # 2. Registrar Abono del Cliente
        with st.expander(f"➕ Registrar Abono de {cli_corte}", expanded=False):
            with st.form("form_abono_cliente", clear_on_submit=True):
                col_ab1, col_ab2, col_ab3 = st.columns(3)
                with col_ab1:
                    f_abono = st.date_input("Fecha del Abono", key="f_ab_input", format="DD/MM/YYYY")
                with col_ab2:
                    monto_ab = st.number_input("Monto Abono ($)", min_value=0.0, step=0.50, key="m_ab_input")
                with col_ab3:
                    concepto_ab = st.text_input("Concepto / Observación", placeholder="Ej. Pago móvil, Transferencia", key="c_ab_input")
                
                guardar_ab_btn = st.form_submit_button("Guardar Abono", type="primary", use_container_width=True)
            
            if guardar_ab_btn:
                if monto_ab > 0:
                    nuevo_id_ab = len(df_abonos) + 1
                    nuevo_reg_ab = {
                        'ID': nuevo_id_ab,
                        'Fecha': f_abono.strftime("%d/%m/%Y"),
                        'Cliente': cli_corte,
                        'Monto': float(monto_ab),
                        'Concepto': concepto_ab.strip() if concepto_ab.strip() else "Abono a cuenta",
                        'Estado': 'Pendiente'
                    }
                    df_abonos = pd.concat([df_abonos, pd.DataFrame([nuevo_reg_ab])], ignore_index=True)
                    df_abonos.to_csv(FILE_ABONOS, index=False)
                    st.toast(f"✅ Abono de ${monto_ab:.2f} registrado a {cli_corte}", icon="💵")
                    st.rerun()
                else:
                    st.error("⚠️ El monto del abono debe ser mayor a $0.")

        # 3. Filtrar DataFrame por cliente
        df_c = validados_cli[validados_cli['Cliente'] == cli_corte].copy()
        df_c['Fecha_dt'] = pd.to_datetime(df_c['Fecha'].astype(str).str[:10], errors='coerce')

        if f_inicio is not None:
            df_c = df_c[df_c['Fecha_dt'] >= pd.to_datetime(f_inicio)]
        if f_fin is not None:
            df_c = df_c[df_c['Fecha_dt'] <= pd.to_datetime(f_fin)]

        if not df_c.empty:
            df_c['Fecha_Corta'] = df_c['Fecha_dt'].dt.strftime('%d/%m')

            # Obtener abonos pendientes
            df_ab_cli = df_abonos[(df_abonos['Cliente'] == cli_corte) & (df_abonos['Estado'] == 'Pendiente')] if not df_abonos.empty else pd.DataFrame()
            total_vueltas_cli = df_c['Precio_Cliente'].sum()
            total_abonos_cli = df_ab_cli['Monto'].sum() if not df_ab_cli.empty else 0.0
            total_neto_cli = total_vueltas_cli - total_abonos_cli

            # Métricas
            m1, m2, m3 = st.columns(3)
            m1.metric("Acumulado Vueltas", f"${total_vueltas_cli:.2f}")
            m2.metric("Total Abonos", f"-${total_abonos_cli:.2f}")
            m3.metric("Neto a Cobrar", f"${total_neto_cli:.2f}")

            # Tabla de Abonos
            if not df_ab_cli.empty:
                st.write("##### 💵 Abonos Recibidos")
                st.dataframe(df_ab_cli[['Fecha', 'Monto', 'Concepto']], use_container_width=True)

            # Tabla Vueltas Realizadas
            st.write("##### 📋 Vueltas Realizadas")
            st.dataframe(
                df_c[['Fecha_Corta', 'Origen', 'Destino', 'Precio_Cliente']].rename(columns={'Fecha_Corta': 'Fecha', 'Precio_Cliente': 'Precio ($)'}), 
                use_container_width=True
            )

            # 4. Generar mensaje de WhatsApp (Agrupado por fecha)
            msj = f"*MOTOVUELTAS - Resumen de Cuenta*\nCliente: *{cli_corte}*\n---\n"
            
            # Ordenar por fecha cronológica
            df_c_sorted = df_c.sort_values(by='Fecha_dt')
            
            # Agrupar servicios por cada fecha (usando formato compatible)
            for fecha_grupo, grupo in df_c_sorted.groupby('Fecha_Corta', sort=False):
                msj += f"\n*Fecha {fecha_grupo}*\n"
                for _, r in grupo.iterrows():
                    msj += f"• {r['Origen']} -> {r['Destino']}: ${r['Precio_Cliente']:.2f}\n"

            if total_abonos_cli > 0:
                msj += f"\n---\nSubtotal Vueltas: ${total_vueltas_cli:.2f}\nAbonos Recibidos: -${total_abonos_cli:.2f}\n"

            msj += f"\n---\n*TOTAL A PAGAR: ${total_neto_cli:.2f}*"

            st.text_area("Mensaje de WhatsApp preparado:", msj, height=180)

            # 5. Obtener teléfono del cliente y generar enlace codificado correctamente
            row_cli = df_clientes[df_clientes['Nombre'] == cli_corte]
            num_tlf = ""
            if not row_cli.empty:
                col_num = 'Telefono' if 'Telefono' in row_cli.columns else ('Contacto' if 'Contacto' in row_cli.columns else None)
                if col_num:
                    num_tlf = str(row_cli[col_num].values[0]).replace("+", "").replace(" ", "").replace("-", "").strip()

            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if num_tlf and num_tlf != "nan":
                    if num_tlf.startswith("0"):
                        num_tlf_wa = "58" + num_tlf[1:]
                    else:
                        num_tlf_wa = num_tlf
                    
                    # Codificación de URL segura
                    msj_encoded = urllib.parse.quote(msj)
                    link_wa = f"https://wa.me/{num_tlf_wa}?text={msj_encoded}"
                    
                    st.link_button("📲 Enviar por WhatsApp", link_wa, type="secondary", use_container_width=True)
                else:
                    st.warning("⚠️ Sin número registrado en Clientes para envío directo.")

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
