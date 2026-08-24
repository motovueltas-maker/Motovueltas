import streamlit as st
import pandas as pd
import os
from datetime import datetime
import urllib.parse

st.set_page_config(page_title="MotoVueltas - Control Operativo", layout="wide", page_icon="🛵")

# ---------------------------------------------------------
# OCULTAR BARRA SUPERIOR, MENÚ DE STREAMLIT Y BOTÓN GITHUB
# ---------------------------------------------------------
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppHeader {display: none;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

from streamlit_gsheets import GSheetsConnection

# ---------------------------------------------------------
# CONEXIÓN PERSISTENTE A GOOGLE SHEETS
# ---------------------------------------------------------
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    try:
        df_cli = conn.read(worksheet="Clientes", ttl=0)
    except Exception:
        df_cli = pd.DataFrame([{"Nombre": "Cliente General", "Telefono": "04140000000", "Ubicacion": "Centro"}])
        
    try:
        df_mot = conn.read(worksheet="Motorizados", ttl=0)
    except Exception:
        df_mot = pd.DataFrame([
            {"Nombre": "Omar", "Comision_Base": 66.67},
            {"Nombre": "Jhoiner", "Comision_Base": 66.67},
            {"Nombre": "Deiby", "Comision_Base": 66.67},
            {"Nombre": "Génesis", "Comision_Base": 66.67},
            {"Nombre": "Esneyder", "Comision_Base": 100.0}
        ])
        
    try:
        df_ser = conn.read(worksheet="Servicios", ttl=0)
    except Exception:
        df_ser = pd.DataFrame(columns=['ID', 'Fecha', 'Motorizado', 'Cliente', 'Origen', 'Destino', 'Detalle', 'Precio_Cliente', 'Porcentaje_Comision', 'Monto_Motorizado', 'Ganancia_Empresa', 'Estado_Validacion', 'Estado_Cliente', 'Estado_Motorizado'])

    FILE_USUARIOS = "usuarios.csv"
    if os.path.exists(FILE_USUARIOS):
        df_usr = pd.read_csv(FILE_USUARIOS)
    else:
        df_usr = pd.DataFrame([
            {"Usuario": "esneyder", "Clave": "339733", "Nombre": "Esneyder", "Rol": "Admin"},
            {"Usuario": "omar", "Clave": "5068", "Nombre": "Omar", "Rol": "Chofer"},
            {"Usuario": "jhoiner", "Clave": "8139", "Nombre": "Jhoiner", "Rol": "Chofer"},
            {"Usuario": "deiby", "Clave": "8455", "Nombre": "Deiby", "Rol": "Chofer"},
            {"Usuario": "genesis", "Clave": "7852", "Nombre": "Génesis", "Rol": "Chofer"}
        ])
        
    return df_cli, df_mot, df_ser, df_usr

df_clientes, df_motorizados, df_servicios, df_usuarios = cargar_datos()

st.title("🛵 MotoVueltas - Sistema de Gestión")

# ---------------------------------------------------------
# CONTROL DE SESIÓN Y LOGIN DE USUARIOS
# ---------------------------------------------------------
if "usuario_logueado" not in st.session_state:
    st.session_state["usuario_logueado"] = None
    st.session_state["rol_usuario"] = None
    st.session_state["nombre_usuario"] = None

# Pantalla de Inicio de Sesión si no hay usuario activo
if st.session_state["usuario_logueado"] is None:
    st.subheader("🔐 Iniciar Sesión")
    with st.form("form_login"):
        user_input = st.text_input("Usuario (ej: esneyder, omar)").strip().lower()
        pass_input = st.text_input("Contraseña", type="password")
        btn_login = st.form_submit_button("Ingresar", type="primary", use_container_width=True)

        if btn_login:
            match = df_usuarios[(df_usuarios['Usuario'] == user_input) & (df_usuarios['Clave'].astype(str) == pass_input)]
            if not match.empty:
                st.session_state["usuario_logueado"] = user_input
                st.session_state["rol_usuario"] = match.iloc[0]['Rol']
                st.session_state["nombre_usuario"] = match.iloc[0]['Nombre']
                st.toast(f"Bienvenido {match.iloc[0]['Nombre']}", icon="👋")
                st.rerun()
            else:
                st.error("⚠️ Usuario o contraseña incorrectos.")
    st.stop()
    
# ---------------------------------------------------------
# BARRA LATERAL CON INFORMACIÓN DEL USUARIO Y ROLES
# ---------------------------------------------------------
if st.sidebar.button("Cerrar Sesión", type="secondary"):
    st.session_state["usuario_logueado"] = None
    st.session_state["rol_usuario"] = None
    st.session_state["nombre_usuario"] = None
    st.rerun()

st.sidebar.write("---")

# Función Callback para cambiar de ventana sin error
def ir_a_liquidacion():
    st.session_state["opcion_menu"] = "🏍️ Liquidación Motorizados"

# Definir opciones del menú según el Rol del usuario
if st.session_state["rol_usuario"] == "Chofer":
    opciones_disponibles = ["🛵 Registrar Vuelta", "🏍️ Liquidación Motorizados"]
else:
    # Opciones completas para Administrador
    opciones_disponibles = [
        "🛵 Registrar Vuelta",
        "✅ Validar Precios",
        "💵 Corte Clientes",
        "🏍️ Liquidación Motorizados",
        "👥 Directorio Clientes",
        "⚙️ Perfiles Motorizados"
    ]

# Menú de navegación con clave asignada
opcion_menu = st.sidebar.radio("📌 Menú de Navegación", opciones_disponibles, key="opcion_menu")

# ---------------------------------------------------------
# TAB 1: REGISTRAR VUELTA (ADAPTATIVO SEGÚN ROL)
# ---------------------------------------------------------
if opcion_menu == "🛵 Registrar Vuelta":
    # Botón de acceso directo a balance para choferes en teléfonos
    if st.session_state.get("rol_usuario") == "Chofer":
        st.button(
            "📊 Ver mi Balance y Avances",
            type="secondary",
            use_container_width=True,
            on_click=ir_a_liquidacion
        )

    es_admin = (st.session_state.get("rol_usuario") == "Admin")
    nombre_sesion = st.session_state.get("nombre_usuario", "")

    # Configuración de controles superiores (Solo visibles para Admin)
    col_top1, col_top2, col_top3 = st.columns(3)
    
    with col_top1:
        fecha_operativa = st.date_input("Fecha de la vuelta", key="fecha_carreras_fija", format="DD/MM/YYYY")
    
    if es_admin:
        with col_top2:
            lista_motos = df_motorizados['Nombre'].tolist()
            moto_sel = st.selectbox("Motorizado", lista_motos, key="moto_carreras_fija")
        with col_top3:
            com_base_sug = df_motorizados.loc[df_motorizados['Nombre'] == moto_sel, 'Comision_Base'].values
            val_default = float(com_base_sug[0]) if len(com_base_sug) > 0 else 66.67
            porcentaje_actual = st.number_input(
                "Comisión Motorizado (%)", min_value=0.0, max_value=100.0, 
                value=val_default, step=0.5, key=f"comision_input_{moto_sel}"
            )
    else:
        # Si es Chofer, se fijan sus datos de forma oculta
        moto_sel = nombre_sesion
        com_base_sug = df_motorizados.loc[df_motorizados['Nombre'] == moto_sel, 'Comision_Base'].values
        porcentaje_actual = float(com_base_sug[0]) if len(com_base_sug) > 0 else 66.67
        st.info(f"🛵 Registrando vuelta para el chofer: **{moto_sel}**")

    # Formulario para precargar la carrera
    with st.form("form_agregar_vuelta", clear_on_submit=True):
        lista_cli = [""] + df_clientes['Nombre'].tolist()
        cli_sel = st.selectbox("Seleccionar Cliente", lista_cli, index=0)
        
        col1, col2 = st.columns(2)
        with col1:
            origen = st.text_input("Desde", value="Local")
        with col2:
            destino = st.text_input("Hasta", value="Local")
        
        if es_admin:
            precio_directo = st.number_input("Precio Cliente ($) (Opcional - Valida de inmediato si > 0)", min_value=0.0, value=0.0, step=0.50)
        else:
            precio_directo = 0.0  # Para los choferes siempre entra como $0 (Pendiente de validación)
            
        guardar_btn = st.form_submit_button("Precargar Vuelta para Validación", type="primary", use_container_width=True)

        if guardar_btn:
            if destino.strip() or origen.strip():
                nuevo_id = len(df_servicios) + 1
                fecha_final = f"{fecha_operativa} {datetime.now().strftime('%H:%M')}"
                origen_final = origen.strip() if origen.strip() else "Local"
                destino_final = destino.strip() if destino.strip() else "Local"
                cliente_final = cli_sel if cli_sel else "Cliente General"

                comision_val = round(float(porcentaje_actual), 2)
                
                if precio_directo > 0 and es_admin:
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
                conn.update(worksheet="Servicios", data=df_servicios)
                
                if estado_val == "Validado":
                    st.success(f"✅ ¡Vuelta #{nuevo_id} guardada y VALIDADA por ${precio_directo:.2f}!")
                else:
                    st.info(f"ℹ️ Vuelta #{nuevo_id} precargada con éxito (Pendiente por validación de precio).")
                st.toast(f"✅ Vuelta #{nuevo_id} precargada", icon="🛵")
            else:
                st.error("⚠️ Debes ingresar al menos el destino de la carrera.") 
                
# ---------------------------------------------------------
# TAB 2: VALIDAR PRECIOS Y EDITAR VUELTAS CON VISUALIZACIÓN
# ---------------------------------------------------------
elif opcion_menu == "✅ Validar Precios":
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
                        conn.update(worksheet="Servicios", data=df_servicios)
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
                    
                conn.update(worksheet="Servicios", data=df_servicios)
                st.toast(f"✅ Vuelta #{row_edit['ID']} corregida completamente", icon="✏️")
                st.rerun()
        else:
            st.info("No se encontraron vueltas que coincidan con los filtros seleccionados.")

# ---------------------------------------------------------
# TAB 3: CORTE CLIENTES, ABONOS Y ENVÍO DIRECTO A WHATSAPP
# ---------------------------------------------------------
elif opcion_menu == "💵 Corte Clientes":
    st.subheader("Corte de Cuenta Clientes")
    
    try:
        df_abonos = conn.read(worksheet="Abonos", ttl=0)
    except Exception:
        df_abonos = pd.DataFrame(columns=['ID', 'Fecha', 'Cliente', 'Monto', 'Concepto', 'Estado'])

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
                    conn.update(worksheet="Abonos", data=df_abonos)
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
                            msj_encoded = urllib.parse.quote(msj)
                            link_wa = f"https://wa.me/{num_tlf_wa}?text={msj_encoded}"
                            st.link_button("📲 Enviar por WhatsApp", link_wa, type="secondary", use_container_width=True)
                        else:
                            st.warning("⚠️ Sin número registrado en Clientes para envío directo.")

# ---------------------------------------------------------
# TAB 4: LIQUIDACIÓN MOTORIZADOS CON GESTIÓN DE AVANCES
# ---------------------------------------------------------
elif opcion_menu == "🏍️ Liquidación Motorizados":
    st.subheader("Liquidación y Balance de Motorizados")

    try:
        df_avances = conn.read(worksheet="Avances", ttl=0)
    except Exception:
        df_avances = pd.DataFrame(columns=['ID', 'Fecha', 'Motorizado', 'Monto', 'Concepto', 'Estado'])

    validados_mot = df_servicios[(df_servicios['Estado_Validacion'] == 'Validado') & (df_servicios['Estado_Motorizado'] == 'Pendiente')].copy()
    
    # Definir el motorizado a consultar según el rol
    if es_admin:
        lista_motos_liq = sorted(list(set(validados_mot['Motorizado'].dropna().unique().tolist() + df_motorizados['Nombre'].dropna().tolist())))
        if lista_motos_liq:
            mot_corte = st.selectbox("Seleccionar Motorizado", lista_motos_liq, key="mot_sel_liq")
        else:
            mot_corte = None
    else:
        mot_corte = nombre_sesion
        st.info(f"📊 Consulta de saldo para: **{mot_corte}**")

    if mot_corte:
        # 1. FORMULARIO DE REGISTRAR AVANCE (Solo visible para Admin)
        if es_admin:
            with st.expander(f"➕ Registrar Avance / Adelanto a {mot_corte}", expanded=False):
                with st.form("form_avance_motorizado", clear_on_submit=True):
                    col_av1, col_av2, col_av3 = st.columns(3)
                    with col_av1:
                        f_avance = st.date_input("Fecha del Avance", key="f_av_input", format="DD/MM/YYYY")
                    with col_av2:
                        monto_av = st.number_input("Monto Avance ($)", min_value=0.0, step=0.50, key="m_av_input")
                    with col_av3:
                        concepto_av = st.text_input("Concepto / Observación", placeholder="Ej. Gasolina, Repuesto, Adelanto", key="c_av_input")
                    
                    guardar_av_btn = st.form_submit_button("Guardar Avance", type="primary", use_container_width=True)
                    if guardar_av_btn:
                        if monto_av > 0:
                            nuevo_id_av = len(df_avances) + 1
                            nuevo_reg_av = {
                                'ID': nuevo_id_av,
                                'Fecha': f_avance.strftime("%d/%m/%Y"),
                                'Motorizado': mot_corte,
                                'Monto': float(monto_av),
                                'Concepto': concepto_av.strip() if concepto_av.strip() else "Avance de efectivo",
                                'Estado': 'Pendiente'
                            }
                            df_avances = pd.concat([df_avances, pd.DataFrame([nuevo_reg_av])], ignore_index=True)
                            conn.update(worksheet="Avances", data=df_avances)
                            st.toast(f"✅ Avance de ${monto_av:.2f} registrado a {mot_corte}", icon="💵")
                            st.rerun()
                        else:
                            st.error("⚠️ El monto del avance debe ser mayor a $0.")

        # 2. CÁLCULO DE TOTALES DEL PERÍODO PENDIENTE
        df_m = validados_mot[validados_mot['Motorizado'] == mot_corte].copy()
        df_av_mot = df_avances[(df_avances['Motorizado'] == mot_corte) & (df_avances['Estado'] == 'Pendiente')].copy() if not df_avances.empty else pd.DataFrame()

        total_vueltas_mot = df_m['Monto_Motorizado'].sum() if not df_m.empty else 0.0
        total_avances_mot = df_av_mot['Monto'].sum() if not df_av_mot.empty else 0.0
        total_neto_mot = total_vueltas_mot - total_avances_mot

        # 3. TARJETAS DE RESUMEN (Adapta según Rol)
        st.write("---")
        if es_admin:
            m1, m2, m3 = st.columns(3)
            m1.metric("Acumulado Vueltas", f"${total_vueltas_mot:.2f}")
            m2.metric("Total Avances", f"-${total_avances_mot:.2f}")
            m3.metric("Neto a Pagar", f"${total_neto_mot:.2f}")
        else:
            # Para Chofer solo muestra Avances y Neto a Pagar
            m1, m2 = st.columns(2)
            m1.metric("Total Avances Recibidos", f"-${total_avances_mot:.2f}")
            m2.metric("Neto a Cobrar", f"${total_neto_mot:.2f}")

        # 4. TABLA DE AVANCES REGISTRADOS (Fecha simplificada a DD/MM)
        if not df_av_mot.empty:
            st.write("##### 💵 Avances Registrados en este Período")
            df_av_mot['Fecha_dt'] = pd.to_datetime(df_av_mot['Fecha'], format='%d/%m/%Y', errors='coerce')
            df_av_mot['Fecha_Corta'] = df_av_mot['Fecha_dt'].dt.strftime('%d/%m').fillna(df_av_mot['Fecha'].astype(str).str[:5])
            st.dataframe(df_av_mot[['Fecha_Corta', 'Monto', 'Concepto']].rename(columns={'Fecha_Corta': 'Fecha', 'Monto': 'Monto ($)'}), use_container_width=True)

        # 5. TABLA DE VUELTAS VALIDADAS (Fecha simplificada a DD/MM)
        if not df_m.empty:
            st.write("##### 📋 Vueltas Validadas del Período")
            df_m['Fecha_dt'] = pd.to_datetime(df_m['Fecha'].astype(str).str[:10], errors='coerce')
            df_m['Fecha_Corta'] = df_m['Fecha_dt'].dt.strftime('%d/%m').fillna(df_m['Fecha'].astype(str).str[5:10])
            st.dataframe(df_m[['Fecha_Corta', 'Cliente', 'Origen', 'Destino', 'Monto_Motorizado']].rename(columns={'Fecha_Corta': 'Fecha', 'Monto_Motorizado': 'Pago ($)'}), use_container_width=True)
        else:
            st.info("No hay vueltas validadas pendientes por liquidar en este período.")

        # 6. BOTÓN DE LIQUIDAR Y RESETEAR (Solo visible para Admin)
        if es_admin and (not df_m.empty or not df_av_mot.empty):
            st.write("---")
            if st.button(f"🏁 Liquidar Período de {mot_corte} (${total_neto_mot:.2f})", type="primary", use_container_width=True):
                # Marcar vueltas y avances como procesados
                df_servicios.loc[(df_servicios['Motorizado'] == mot_corte) & (df_servicios['Estado_Validacion'] == 'Validado'), 'Estado_Motorizado'] = 'Liquidado'
                df_servicios.to_csv(FILE_SERVICIOS, index=False)
                
                if not df_avances.empty:
                    df_avances.loc[(df_avances['Motorizado'] == mot_corte) & (df_avances['Estado'] == 'Pendiente'), 'Estado'] = 'Liquidado'
                    df_avances.to_csv(FILE_AVANCES, index=False)

                st.success(f"✅ ¡Período de {mot_corte} liquidado y reseteado exitosamente!")
                st.rerun()
                
# ---------------------------------------------------------
# TAB 5: DIRECTORIO DE CLIENTES
# ---------------------------------------------------------
elif opcion_menu == "👥 Directorio Clientes":
    st.subheader("Directorio de Clientes")

    # 1. AGREGAR NUEVO CLIENTE
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
            telefonos_existentes = df_clientes['Telefono'].astype(str).str.strip().tolist() if not df_clientes.empty else []
            if tel_limpio in telefonos_existentes:
                st.error(f"❌ Ya existe un cliente registrado con el teléfono {tel_limpio}.")
            else:
                nuevo_registro_cli = {
                    "Nombre": nom_limpio,
                    "Telefono": tel_limpio,
                    "Ubicacion": nuevo_cli_ubicacion.strip() if nuevo_cli_ubicacion.strip() else "-"
                }
                df_clientes = pd.concat([df_clientes, pd.DataFrame([nuevo_registro_cli])], ignore_index=True)
                
                # Guardar convirtiendo a registros limpios
                df_clean = df_clientes[['Nombre', 'Telefono', 'Ubicacion']].copy()
                conn.update(worksheet="Clientes", data=df_clean.to_dict(orient='records'))
                st.success(f"✅ Cliente '{nom_limpio}' registrado con éxito.")
                st.rerun()

    # 2. EDITAR CLIENTE EXISTENTE
    if not df_clientes.empty:
        st.write("---")
        st.write("### ✏️ Editar / Actualizar Cliente Existente")
        
        df_temp = df_clientes.copy()
        df_temp['Select_Label'] = df_temp['Nombre'].astype(str) + " (" + df_temp['Telefono'].astype(str) + ")"
        opciones_cli = df_temp['Select_Label'].tolist()
        
        cli_sel_label = st.selectbox("Seleccionar Cliente a Modificar", opciones_cli)

        idx_cli = df_temp[df_temp['Select_Label'] == cli_sel_label].index[0]
        row_cli_edit = df_clientes.loc[idx_cli]

        with st.form("form_editar_cliente"):
            c_ed1, c_ed2, c_ed3 = st.columns(3)
            with c_ed1:
                edit_nom_cli = st.text_input("Editar Nombre", value=str(row_cli_edit.get('Nombre', '')))
            with c_ed2:
                edit_tlf_cli = st.text_input("Editar Teléfono", value=str(row_cli_edit.get('Telefono', '')))
            with c_ed3:
                edit_ubi_cli = st.text_input("Editar Ubicación", value=str(row_cli_edit.get('Ubicacion', '')))

            btn_update_cli = st.form_submit_button("Guardar Cambios del Cliente", type="primary", use_container_width=True)

        if btn_update_cli:
            df_clientes.at[idx_cli, 'Nombre'] = edit_nom_cli.strip()
            df_clientes.at[idx_cli, 'Telefono'] = edit_tlf_cli.strip()
            df_clientes.at[idx_cli, 'Ubicacion'] = edit_ubi_cli.strip()

            # Guardar limpiando el formato para Google Sheets
            df_clean = df_clientes[['Nombre', 'Telefono', 'Ubicacion']].copy()
            conn.update(worksheet="Clientes", data=df_clean.to_dict(orient='records'))
            st.toast("✅ Cliente actualizado con éxito", icon="👤")
            st.rerun()

    # 3. MOSTRAR TABLA DE CLIENTES
    st.write("---")
    st.dataframe(df_clientes[['Nombre', 'Telefono', 'Ubicacion']], use_container_width=True)
    
# ---------------------------------------------------------
# TAB 6: PERFILES DE MOTORIZADOS
# ---------------------------------------------------------
elif opcion_menu == "⚙️ Perfiles Motorizados":
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
