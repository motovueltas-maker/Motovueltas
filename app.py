import streamlit as st
import pandas as pd
import os
from datetime import datetime
import urllib.parse  # <--- Agrega esta línea aquí

st.set_page_config(page_title="MotoVueltas - Control Operativo", layout="wide", page_icon="🛵")

# ---------------------------------------------------------
# OCULTAR BARRA SUPERIOR, HEADER Y MENÚ DE STREAMLIT
# ---------------------------------------------------------
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden !important;}
header {visibility: hidden !important;}
footer {visibility: hidden !important;}
.stAppHeader {display: none !important;}
[data-testid="stHeader"] {display: none !important;}
[data-testid="stToolbar"] {display: none !important;}
[data-testid="stDecoration"] {display: none !important;}
button[title="View source"] {display: none !important;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ---------------------------------------------------------
# MANEJO DE ARCHIVOS CSV (PERSISTENCIA SEGURA EN GITHUB)
# ---------------------------------------------------------
FILE_CLIENTES = "clientes.csv"
FILE_MOTORIZADOS = "motorizados.csv"
FILE_SERVICIOS = "servicios.csv"
FILE_USUARIOS = "usuarios.csv"

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
            {"Nombre": "Génesis", "Comision_Base": 66.67},
            {"Nombre": "Esneyder", "Comision_Base": 100.0}
        ])
        df_mot.to_csv(FILE_MOTORIZADOS, index=False)

    if os.path.exists(FILE_SERVICIOS):
        df_ser = pd.read_csv(FILE_SERVICIOS)
    else:
        df_ser = pd.DataFrame(columns=[
            'ID', 'Fecha', 'Motorizado', 'Cliente', 'Origen', 'Destino', 'Detalle',
            'Precio_Cliente', 'Porcentaje_Comision', 'Monto_Motorizado',
            'Ganancia_Empresa', 'Estado_Validacion', 'Estado_Cliente', 'Estado_Motorizado'
        ])
        df_ser.to_csv(FILE_SERVICIOS, index=False)

    if os.path.exists(FILE_USUARIOS):
        df_usr = pd.read_csv(FILE_USUARIOS)
    else:
        df_usr = pd.DataFrame([
            {"Usuario": "esneyder", "Clave": "1234", "Nombre": "Esneyder", "Rol": "Admin"},
            {"Usuario": "omar", "Clave": "1234", "Nombre": "Omar", "Rol": "Chofer"},
            {"Usuario": "jhoiner", "Clave": "1234", "Nombre": "Jhoiner", "Rol": "Chofer"},
            {"Usuario": "deiby", "Clave": "1234", "Nombre": "Deiby", "Rol": "Chofer"},
            {"Usuario": "genesis", "Clave": "1234", "Nombre": "Génesis", "Rol": "Chofer"}
        ])
        df_usr.to_csv(FILE_USUARIOS, index=False)

    return df_cli, df_mot, df_ser, df_usr

df_clientes, df_motorizados, df_servicios, df_usuarios = cargar_datos()

st.title("🛵 MotoVueltas - Sistema de Gestión")

# ---------------------------------------------------------
# CONTROL DE SESIÓN PERSISTENTE (MANTENER LOGIN AL RECARGAR)
# ---------------------------------------------------------
# 1. Recuperar sesión desde los parámetros de la URL si el usuario recarga la página
query_params = st.query_params
usr_url = query_params.get("usr", None)

if "usuario_logueado" not in st.session_state:
    if usr_url and not df_usuarios.empty:
        match_url = df_usuarios[df_usuarios['Usuario'] == usr_url.lower()]
        if not match_url.empty:
            st.session_state["usuario_logueado"] = match_url.iloc[0]['Usuario']
            st.session_state["rol_usuario"] = match_url.iloc[0]['Rol']
            st.session_state["nombre_usuario"] = match_url.iloc[0]['Nombre']
        else:
            st.session_state["usuario_logueado"] = None
    else:
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
            
            # Guardar el usuario en la URL para que persista la sesión al refrescar
            st.query_params["usr"] = user_input
            st.toast(f"Bienvenido {match.iloc[0]['Nombre']}", icon="👋")
            st.rerun()
        else:
            st.error("⚠️ Usuario o contraseña incorrectos.")
    st.stop()

# Si hace clic en "Cerrar Sesión", limpiar también los parámetros de la URL

# ---------------------------------------------------------
# BARRA LATERAL CON INFORMACIÓN DEL USUARIO Y ROLES
# ---------------------------------------------------------
st.sidebar.markdown(f"👤 **{st.session_state['nombre_usuario']}**  \n*Rol: {st.session_state['rol_usuario']}*")
if st.sidebar.button("Cerrar Sesión", type="secondary"):
    st.session_state["usuario_logueado"] = None
    st.session_state["rol_usuario"] = None
    st.session_state["nombre_usuario"] = None
    st.query_params.clear()  # Borra la sesión retenida en la URL
    st.rerun()

st.sidebar.write("---")

# Definir opciones del menú según el Rol del usuario
if st.session_state["rol_usuario"] == "Chofer":
    opciones_disponibles = ["🛵 Registrar Vuelta"]
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

opcion_menu = st.sidebar.radio("📌 Menú de Navegación", opciones_disponibles)

# ---------------------------------------------------------
# TAB 1: REGISTRAR VUELTA (ADAPTATIVO SEGÚN ROL)
# ---------------------------------------------------------
if opcion_menu == "🛵 Registrar Vuelta":
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

    # Formulario para precargar la vuelta
    with st.form("form_agregar_vuelta", clear_on_submit=True):
        lista_cli = [""] + (df_clientes['Nombre'].astype(str).tolist() if not df_clientes.empty else [])
        cli_sel = st.selectbox("Seleccionar Cliente", lista_cli, index=0)
        
        col1, col2 = st.columns(2)
        with col1:
            origen = st.text_input("Desde", placeholder="Local")
        with col2:
            destino = st.text_input("Hasta", placeholder="Local")
        
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
                cliente_final = str(cli_sel).strip() if cli_sel else "Cliente General"

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
                df_servicios.to_csv(FILE_SERVICIOS, index=False)
                
                if estado_val == "Validado":
                    st.success(f"✅ ¡Vuelta #{nuevo_id} guardada y VALIDADA por ${precio_directo:.2f}!")
                else:
                    st.info(f"ℹ️ Vuelta #{nuevo_id} precargada con éxito (Pendiente por validación de precio).")
                st.toast(f"✅ Vuelta #{nuevo_id} precargada", icon="🛵")
            else:
                st.error("⚠️ Debes ingresar al menos el destino de la carrera.") 
                
# ---------------------------------------------------------
# TAB 2: VALIDAR PRECIOS Y EDITAR VUELTAS (COMPLETO)
# ---------------------------------------------------------
elif opcion_menu == "✅ Validar Precios":
    st.subheader("Validación y Corrección de Vueltas")

    # 1. VUELTAS PENDIENTES POR VALIDAR (TODAS EN UNA MISMA TABLA)
    st.write("### 📋 Vueltas Pendientes por Validar")
    vueltas_pendientes = df_servicios[df_servicios['Estado_Validacion'] == 'Pendiente']

    if not vueltas_pendientes.empty:
        # Encabezados de la Tabla
        h1, h2, h3, h4, h5, h6, h7, h8 = st.columns([1, 1.2, 1.5, 1.2, 1.2, 1, 1, 1.2])
        with h1: st.caption("**ID / Chofer**")
        with h2: st.caption("**Fecha**")
        with h3: st.caption("**Cliente**")
        with h4: st.caption("**Desde**")
        with h5: st.caption("**Hasta**")
        with h6: st.caption("**Precio ($)**")
        with h7: st.caption("**% Com.**")
        with h8: st.caption("**Acción**")

        st.markdown("---")

        lista_motos_val = df_motorizados['Nombre'].tolist() if not df_motorizados.empty else []
        lista_cli_val = df_clientes['Nombre'].tolist() if not df_clientes.empty else []

        for idx, row in vueltas_pendientes.iterrows():
            c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([1, 1.2, 1.5, 1.2, 1.2, 1, 1, 1.2])

            with c1:
                st.write(f"**#{row['ID']}**")
                st.caption(f"🛵 {row['Motorizado']}")

            with c2:
                try:
                    f_val_orig = datetime.strptime(str(row['Fecha'])[:10], "%Y-%m-%d").date()
                except:
                    f_val_orig = datetime.now().date()
                val_fecha = st.date_input("Fec", value=f_val_orig, format="DD/MM/YYYY", key=f"vf_{row['ID']}", label_visibility="collapsed")

            with c3:
                idx_c = lista_cli_val.index(row['Cliente']) if row['Cliente'] in lista_cli_val else 0
                val_cli = st.selectbox("Cli", lista_cli_val, index=idx_c, key=f"vc_{row['ID']}", label_visibility="collapsed")

            with c4:
                val_orig = st.text_input("Orig", value=str(row['Origen']), key=f"vo_{row['ID']}", label_visibility="collapsed")

            with c5:
                val_dest = st.text_input("Dest", value=str(row['Destino']), key=f"vd_{row['ID']}", label_visibility="collapsed")

            with c6:
                val_precio = st.number_input("P", min_value=0.0, value=float(row['Precio_Cliente']), step=0.50, key=f"vp_{row['ID']}", label_visibility="collapsed")

            with c7:
                com_base = df_motorizados.loc[df_motorizados['Nombre'] == row['Motorizado'], 'Comision_Base'].values
                com_def = float(com_base[0]) if len(com_base) > 0 else 66.67
                val_comision = st.number_input("C", min_value=0.0, max_value=100.0, value=com_def, step=0.5, key=f"vcom_{row['ID']}", label_visibility="collapsed")

            with c8:
                if st.button("✅ Validar", type="primary", key=f"vbtn_{row['ID']}", use_container_width=True):
                    if val_precio > 0:
                        m_moto = round(val_precio * (val_comision / 100.0), 2)
                        g_emp = round(val_precio - m_moto, 2)
                        
                        hora_str = str(row['Fecha'])[11:] if len(str(row['Fecha'])) > 10 else datetime.now().strftime('%H:%M')
                        f_final_val = f"{val_fecha} {hora_str}".strip()

                        df_servicios.loc[df_servicios['ID'] == row['ID'], [
                            'Fecha', 'Cliente', 'Origen', 'Destino', 
                            'Precio_Cliente', 'Porcentaje_Comision', 
                            'Monto_Motorizado', 'Ganancia_Empresa', 'Estado_Validacion'
                        ]] = [
                            f_final_val, val_cli, 
                            val_orig.strip() if val_orig.strip() else "Local", 
                            val_dest.strip() if val_dest.strip() else "Local", 
                            val_precio, val_comision, m_moto, g_emp, 'Validado'
                        ]

                        df_servicios.to_csv(FILE_SERVICIOS, index=False)
                        st.toast(f"✅ Vuelta #{row['ID']} validada por ${val_precio:.2f}", icon="🎉")
                        st.rerun()
                    else:
                        st.error("El precio debe ser mayor a $0.")
    else:
        st.info("No hay vueltas pendientes por validar.")

    # 2. CORREGIR / EDITAR VUELTAS YA REGISTRADAS (CON FILTROS)
    st.write("---")
    st.write("### ✏️ Corregir / Editar Vueltas Ya Registradas")

    if not df_servicios.empty:
        # Filtros de Búsqueda
        f_col1, f_col2, f_col3, f_col4 = st.columns(4)
        with f_col1:
            motos_lista_filtro = ["Todos"] + (df_motorizados['Nombre'].tolist() if not df_motorizados.empty else [])
            filtro_moto = st.selectbox("Filtrar por Motorizado", motos_lista_filtro, key="f_edit_moto")
        with f_col2:
            cli_lista_filtro = ["Todos"] + (df_clientes['Nombre'].tolist() if not df_clientes.empty else [])
            filtro_cli = st.selectbox("Filtrar por Cliente", cli_lista_filtro, key="f_edit_cli")
        with f_col3:
            filtro_f_ini = st.date_input("Desde Fecha", value=None, key="f_edit_ini")
        with f_col4:
            filtro_f_fin = st.date_input("Hasta Fecha", value=None, key="f_edit_fin")

        # Aplicar Filtros sobre el DataFrame
        df_editables = df_servicios.copy()
        df_editables['Fecha_dt'] = pd.to_datetime(df_editables['Fecha'].astype(str).str[:10], errors='coerce')

        if filtro_moto != "Todos":
            df_editables = df_editables[df_editables['Motorizado'] == filtro_moto]
        if filtro_cli != "Todos":
            df_editables = df_editables[df_editables['Cliente'] == filtro_cli]
        if filtro_f_ini is not None:
            df_editables = df_editables[df_editables['Fecha_dt'] >= pd.to_datetime(filtro_f_ini)]
        if filtro_f_fin is not None:
            df_editables = df_editables[df_editables['Fecha_dt'] <= pd.to_datetime(filtro_f_fin)]

        if not df_editables.empty:
            lista_opciones_edit = [
                f"ID #{r['ID']} - {r['Fecha'][:10]} | 🛵 {r['Motorizado']} | 👤 {r['Cliente']} (${r['Precio_Cliente']:.2f})" 
                for _, r in df_editables.sort_values(by='ID', ascending=False).iterrows()
            ]
            
            sel_vuelta_edit = st.selectbox("Seleccionar Vuelta a Modificar", lista_opciones_edit)
            
            id_sel_edit = int(sel_vuelta_edit.split(" - ")[0].replace("ID #", ""))
            row_edit = df_servicios[df_servicios['ID'] == id_sel_edit].iloc[0]

            with st.form("form_editar_vuelta_registrada"):
                st.write(f"**Modificando Vuelta #{id_sel_edit}**")
                
                col_e1, col_e2, col_e3 = st.columns(3)
                with col_e1:
                    try:
                        f_edit_orig = datetime.strptime(str(row_edit['Fecha'])[:10], "%Y-%m-%d").date()
                    except:
                        f_edit_orig = datetime.now().date()
                    edit_fecha = st.date_input("Fecha", value=f_edit_orig)
                with col_e2:
                    motos_list_ed = df_motorizados['Nombre'].tolist() if not df_motorizados.empty else [row_edit['Motorizado']]
                    idx_m = motos_list_ed.index(row_edit['Motorizado']) if row_edit['Motorizado'] in motos_list_ed else 0
                    edit_moto = st.selectbox("Motorizado", motos_list_ed, index=idx_m)
                with col_e3:
                    cli_list_ed = df_clientes['Nombre'].tolist() if not df_clientes.empty else [row_edit['Cliente']]
                    idx_c = cli_list_ed.index(row_edit['Cliente']) if row_edit['Cliente'] in cli_list_ed else 0
                    edit_cli = st.selectbox("Cliente", cli_list_ed, index=idx_c)

                col_e4, col_e5, col_e6, col_e7 = st.columns(4)
                with col_e4:
                    edit_orig = st.text_input("Desde", value=str(row_edit['Origen']))
                with col_e5:
                    edit_dest = st.text_input("Hasta", value=str(row_edit['Destino']))
                with col_e6:
                    edit_precio = st.number_input("Precio ($)", min_value=0.0, value=float(row_edit['Precio_Cliente']), step=0.50)
                with col_e7:
                    edit_comision = st.number_input("% Comisión", min_value=0.0, max_value=100.0, value=float(row_edit.get('Porcentaje_Comision', 66.67)), step=0.5)

                btn_guardar_edicion = st.form_submit_button("💾 Guardar Cambios de la Vuelta", type="primary", use_container_width=True)

            if btn_guardar_edicion:
                m_moto_ed = round(edit_precio * (edit_comision / 100.0), 2)
                g_emp_ed = round(edit_precio - m_moto_ed, 2)
                
                hora_str_ed = str(row_edit['Fecha'])[11:] if len(str(row_edit['Fecha'])) > 10 else datetime.now().strftime('%H:%M')
                f_final_ed = f"{edit_fecha} {hora_str_ed}".strip()

                df_servicios.loc[df_servicios['ID'] == id_sel_edit, [
                    'Fecha', 'Motorizado', 'Cliente', 'Origen', 'Destino', 
                    'Precio_Cliente', 'Porcentaje_Comision', 
                    'Monto_Motorizado', 'Ganancia_Empresa'
                ]] = [
                    f_final_ed, edit_moto, edit_cli, 
                    edit_orig.strip() if edit_orig.strip() else "Local", 
                    edit_dest.strip() if edit_dest.strip() else "Local", 
                    edit_precio, edit_comision, m_moto_ed, g_emp_ed
                ]

                df_servicios.to_csv(FILE_SERVICIOS, index=False)
                st.toast(f"✅ Vuelta #{id_sel_edit} actualizada correctamente", icon="💾")
                st.rerun()
        else:
            st.warning("No hay vueltas registradas que coincidan con los filtros seleccionados.")
    else:
        st.info("Aún no hay vueltas registradas en la base de datos.")
        
# ---------------------------------------------------------
# TAB 3: CORTE CLIENTES, ABONOS Y ENVÍO DIRECTO A WHATSAPP
# ---------------------------------------------------------
elif opcion_menu == "💵 Corte Clientes":
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
            f_corte_ini = st.date_input("Fecha Desde", value=None, format="DD/MM/YYYY", key="corte_f_ini")
        with col_c3:
            f_corte_fin = st.date_input("Fecha Hasta", value=None, format="DD/MM/YYYY", key="corte_f_fin")

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

        if f_corte_ini is not None:
            df_c = df_c[df_c['Fecha_dt'] >= pd.to_datetime(f_corte_ini)]
        if f_corte_fin is not None:
            df_c = df_c[df_c['Fecha_dt'] <= pd.to_datetime(f_corte_fin)]

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
# TAB 4: LIQUIDACIÓN MOTORIZADOS (ENVÍO Y RESET SEPARADOS)
# ---------------------------------------------------------
elif opcion_menu == "🏍️ Liquidación Motorizados":
    st.subheader("Liquidación y Resumen de Motorizados")

    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        lista_motos_liq = df_motorizados['Nombre'].tolist() if not df_motorizados.empty else []
        mot_corte = st.selectbox("Seleccionar Motorizado", lista_motos_liq, key="liq_mot_sel")
    with col_m2:
        f_liq_ini = st.date_input("Fecha Desde", value=None, format="DD/MM/YYYY", key="liq_f_ini")
    with col_m3:
        f_liq_fin = st.date_input("Fecha Hasta", value=None, format="DD/MM/YYYY", key="liq_f_fin")

    # Asegurar columna de estado de liquidación sin borrar nada de la base de datos
    if 'Estado_Liquidacion' not in df_servicios.columns:
        df_servicios['Estado_Liquidacion'] = 'Pendiente'

    # Filtrar solo vueltas validadas PENDIENTES DE LIQUIDAR AL CHOFER
    df_m = df_servicios[
        (df_servicios['Motorizado'] == mot_corte) & 
        (df_servicios['Estado_Validacion'] == 'Validado') & 
        (df_servicios['Estado_Liquidacion'] != 'Liquidado')
    ].copy()
    
    if not df_m.empty:
        df_m['Fecha_dt'] = pd.to_datetime(df_m['Fecha'].astype(str).str[:10], errors='coerce')
        if f_liq_ini is not None:
            df_m = df_m[df_m['Fecha_dt'] >= pd.to_datetime(f_liq_ini)]
        if f_liq_fin is not None:
            df_m = df_m[df_m['Fecha_dt'] <= pd.to_datetime(f_liq_fin)]

    if not df_m.empty:
        df_sorted = df_m.sort_values(by='Fecha_dt')
        
        # Agrupar por DÍA y MES (DD/MM)
        dias_agrupados = df_sorted.groupby(df_sorted['Fecha_dt'].dt.strftime('%d/%m'), sort=False)
        
        msj_wa = f"🛵 *LIQUIDACIÓN DE MOTOVUELTAS*\n"
        msj_wa += f"Chofer: *{mot_corte}*\n"
        msj_wa += "-----------------------------------\n\n"
        
        total_servicios_cliente = 0.0
        
        for fecha_corta, grupo in dias_agrupados:
            msj_wa += f"📅 *{fecha_corta}*\n"
            for _, r in grupo.iterrows():
                precio_c = float(r['Precio_Cliente'])
                total_servicios_cliente += precio_c
                msj_wa += f"• {r['Origen']} -> {r['Destino']}: ${precio_c:.2f}\n"
            msj_wa += "\n"
            
        com_base = df_motorizados.loc[df_motorizados['Nombre'] == mot_corte, 'Comision_Base'].values
        pct_comision = float(com_base[0]) if len(com_base) > 0 else 66.67
        
        ingreso_chofer = round(total_servicios_cliente * (pct_comision / 100.0), 2)
        
        if 'df_avances' in globals() and not df_avances.empty:
            avances_mot = df_avances[(df_avances['Motorizado'] == mot_corte) & (df_avances['Estado'] == 'Pendiente')]
            total_avances_periodo = float(avances_mot['Monto'].sum()) if not avances_mot.empty else 0.0
        else:
            total_avances_periodo = 0.0

        neto_final = round(ingreso_chofer - total_avances_periodo, 2)
        
        msj_wa += "-----------------------------------\n"
        msj_wa += f"📊 Total Servicios: *${total_servicios_cliente:.2f}*\n"
        msj_wa += f"💰 Tu Comisión ({pct_comision:.0f}%): *${ingreso_chofer:.2f}*\n"
        if total_avances_periodo > 0:
            msj_wa += f"🔻 Avances / Adelantos: *-${total_avances_periodo:.2f}*\n"
        msj_wa += f"✅ *NETO A PAGAR: ${neto_final:.2f}*"
        
        # Preparar enlace de WhatsApp
        row_moto = df_motorizados[df_motorizados['Nombre'] == mot_corte]
        num_tlf = ""
        if not row_moto.empty and 'Telefono' in row_moto.columns:
            num_tlf = str(row_moto['Telefono'].values[0]).replace("+", "").replace(" ", "").replace("-", "").strip()
            if num_tlf.startswith("0"):
                num_tlf = "58" + num_tlf[1:]

        msj_encoded = urllib.parse.quote(msj_wa)
        link_wa = f"https://wa.me/{num_tlf}?text={msj_encoded}"

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            # Botón 1: Abre WhatsApp directamente sin bloqueos de pop-up
            st.link_button("📲 1. Enviar Resumen por WhatsApp", link_wa, type="primary", use_container_width=True)
        
        with col_b2:
            # Botón 2: Procesa el reset y limpia la vista a $0.00
            if st.button("🔒 2. Confirmar Pago y Resetear Conteo", type="secondary", use_container_width=True):
                ids_a_cerrar = df_sorted['ID'].tolist()
                df_servicios.loc[df_servicios['ID'].isin(ids_a_cerrar), 'Estado_Liquidacion'] = 'Liquidado'
                df_servicios.to_csv(FILE_SERVICIOS, index=False)

                if 'df_avances' in globals() and not df_avances.empty:
                    df_avances.loc[
                        (df_avances['Motorizado'] == mot_corte) & (df_avances['Estado'] == 'Pendiente'), 
                        'Estado'
                    ] = 'Pagado'
                    df_avances.to_csv(FILE_AVANCES, index=False)

                st.toast(f"✅ Conteo de {mot_corte} reiniciado a $0.00.", icon="🎉")
                st.rerun()

        st.markdown("---")
        st.write("### 📄 Vista previa de servicios pendientes por liquidar")
        # Formatear la fecha a DD/MM para la vista previa
        df_display = df_sorted.copy()
        df_display['Fecha'] = df_display['Fecha_dt'].dt.strftime('%d/%m')
        st.dataframe(df_display[['Fecha', 'Origen', 'Destino', 'Precio_Cliente', 'Monto_Motorizado']], use_container_width=True)
    else:
        st.info(f"No hay vueltas pendientes por liquidar para **{mot_corte}**.")
        
# ---------------------------------------------------------
# TAB 5: DIRECTORIO DE CLIENTES (FORMULARIO CON RESET NATIVO)
# ---------------------------------------------------------
elif opcion_menu == "👥 Directorio Clientes":
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
# TAB 6: PERFILES DE MOTORIZADOS Y EDICIÓN
# ---------------------------------------------------------
elif opcion_menu == "⚙️ Perfiles Motorizados":
    st.subheader("Gestión de Motorizados y Comisiones Base")

    # Asegurar que la columna Telefono exista en el DataFrame
    if 'Telefono' not in df_motorizados.columns:
        df_motorizados['Telefono'] = "-"

    # 1. LISTA ACTUAL DE MOTORIZADOS
    st.write("### 🏍️ Motorizados Registrados")
    st.dataframe(df_motorizados[['Nombre', 'Telefono', 'Comision_Base']], use_container_width=True)

    # 2. AGREGAR NUEVO MOTORIZADO
    st.write("---")
    st.write("### ➕ Agregar Nuevo Motorizado")
    with st.form("form_agregar_motorizado", clear_on_submit=True):
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            nuevo_mot_nombre = st.text_input("Nombre del Chofer")
        with col_m2:
            nuevo_mot_tel = st.text_input("Teléfono / WhatsApp (ID Único)")
        with col_m3:
            nuevo_mot_comision = st.number_input("% Comisión Predeterminada", min_value=0.0, max_value=100.0, value=66.67, step=0.5)

        guardar_mot_btn = st.form_submit_button("Guardar Motorizado", type="primary", use_container_width=True)

    if guardar_mot_btn:
        nom_mot_limpio = nuevo_mot_nombre.strip()
        tel_mot_limpio = nuevo_mot_tel.strip()
        
        if not nom_mot_limpio or not tel_mot_limpio:
            st.error("⚠️ Tanto el Nombre como el Teléfono son obligatorios.")
        else:
            telefonos_existentes = df_motorizados['Telefono'].fillna("").astype(str).str.strip().tolist() if not df_motorizados.empty else []
            if tel_mot_limpio in telefonos_existentes:
                st.error(f"❌ Ya existe un motorizado registrado con el teléfono {tel_mot_limpio}.")
            else:
                nuevo_reg_mot = {
                    "Nombre": nom_mot_limpio, 
                    "Telefono": tel_mot_limpio, 
                    "Comision_Base": float(nuevo_mot_comision)
                }
                df_motorizados = pd.concat([df_motorizados, pd.DataFrame([nuevo_reg_mot])], ignore_index=True)
                df_motorizados.to_csv(FILE_MOTORIZADOS, index=False)
                st.success(f"✅ Motorizado '{nom_mot_limpio}' registrado con éxito.")
                st.rerun()

    # 3. EDITAR MOTORIZADO EXISTENTE
    if not df_motorizados.empty:
        st.write("---")
        st.write("### ✏️ Editar Motorizado Existente")
        
        df_temp_m = df_motorizados.copy()
        df_temp_m['Select_Label'] = df_temp_m['Nombre'].astype(str) + " (" + df_temp_m['Telefono'].fillna("").astype(str) + ")"
        opciones_mot = df_temp_m['Select_Label'].tolist()
        
        mot_sel_label = st.selectbox("Seleccionar Motorizado a Modificar", opciones_mot)

        idx_mot = df_temp_m[df_temp_m['Select_Label'] == mot_sel_label].index[0]
        row_mot_edit = df_motorizados.loc[idx_mot]

        with st.form("form_editar_motorizado"):
            col_ed_m1, col_ed_m2, col_ed_m3 = st.columns(3)
            with col_ed_m1:
                edit_nom_mot = st.text_input("Editar Nombre", value=str(row_mot_edit.get('Nombre', '')))
            with col_ed_m2:
                edit_tel_mot = st.text_input("Editar Teléfono", value=str(row_mot_edit.get('Telefono', '')))
            with col_ed_m3:
                com_val_act = float(row_mot_edit.get('Comision_Base', 66.67))
                edit_com_mot = st.number_input("Editar % Comisión Base", min_value=0.0, max_value=100.0, value=com_val_act, step=0.5)

            btn_update_mot = st.form_submit_button("Guardar Cambios del Motorizado", type="primary", use_container_width=True)

        if btn_update_mot:
            nom_edit_limpio = edit_nom_mot.strip()
            tel_edit_limpio = edit_tel_mot.strip()

            if not nom_edit_limpio or not tel_edit_limpio:
                st.error("⚠️ El nombre y el teléfono son obligatorios.")
            else:
                # Actualizar el registro en el DataFrame original
                df_motorizados.at[idx_mot, 'Nombre'] = nom_edit_limpio
                df_motorizados.at[idx_mot, 'Telefono'] = tel_edit_limpio
                df_motorizados.at[idx_mot, 'Comision_Base'] = float(edit_com_mot)

                df_motorizados.to_csv(FILE_MOTORIZADOS, index=False)
                st.toast("✅ Motorizado actualizado con éxito", icon="🏍️")
                st.rerun()
