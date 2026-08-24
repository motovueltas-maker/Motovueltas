import streamlit as st
import pandas as pd
import os
from datetime import datetime
import urllib.parse

st.set_page_config(page_title="MotoVueltas - Control Operativo", layout="wide", page_icon="🛵")

# ---------------------------------------------------------
# OCULTAR BARRA SUPERIOR Y MENÚ DE STREAMLIT
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

# ---------------------------------------------------------
# LECTURA DE DATOS DESDE ARCHIVOS CSV LOCALES
# ---------------------------------------------------------
def cargar_datos():
    # Clientes
    if os.path.exists("clientes.csv"):
        df_cli = pd.read_csv("clientes.csv")
    else:
        df_cli = pd.DataFrame([{"Nombre": "Cliente General", "Telefono": "04140000000", "Ubicacion": "Centro"}])
        df_cli.to_csv("clientes.csv", index=False)

    # Motorizados
    if os.path.exists("motorizados.csv"):
        df_mot = pd.read_csv("motorizados.csv")
    else:
        df_mot = pd.DataFrame([
            {"Nombre": "Omar", "Comision_Base": 66.67},
            {"Nombre": "Jhoiner", "Comision_Base": 66.67},
            {"Nombre": "Deiby", "Comision_Base": 66.67},
            {"Nombre": "Génesis", "Comision_Base": 66.67},
            {"Nombre": "Esneyder", "Comision_Base": 100.0}
        ])
        df_mot.to_csv("motorizados.csv", index=False)

    # Servicios
    if os.path.exists("servicios.csv"):
        df_ser = pd.read_csv("servicios.csv")
    else:
        df_ser = pd.DataFrame(columns=[
            'ID', 'Fecha', 'Motorizado', 'Cliente', 'Origen', 'Destino', 
            'Detalle', 'Precio_Cliente', 'Porcentaje_Comision', 
            'Monto_Motorizado', 'Ganancia_Empresa', 'Estado_Validacion', 
            'Estado_Cliente', 'Estado_Motorizado'
        ])
        df_ser.to_csv("servicios.csv", index=False)

    # Usuarios
    if os.path.exists("usuarios.csv"):
        df_usr = pd.read_csv("usuarios.csv")
    else:
        df_usr = pd.DataFrame([
            {"Usuario": "esneyder", "Clave": "339733", "Nombre": "Esneyder", "Rol": "Admin"},
            {"Usuario": "omar", "Clave": "5068", "Nombre": "Omar", "Rol": "Chofer"},
            {"Usuario": "jhoiner", "Clave": "8139", "Nombre": "Jhoiner", "Rol": "Chofer"},
            {"Usuario": "deiby", "Clave": "8455", "Nombre": "Deiby", "Rol": "Chofer"},
            {"Usuario": "genesis", "Clave": "7852", "Nombre": "Génesis", "Rol": "Chofer"}
        ])
        df_usr.to_csv("usuarios.csv", index=False)

    return df_cli, df_mot, df_ser, df_usr

df_clientes, df_motorizados, df_servicios, df_usuarios = cargar_datos()

st.title("🛵 MotoVueltas - Sistema de Gestión")

# ---------------------------------------------------------
# CONTROL DE SESIÓN Y LOGIN
# ---------------------------------------------------------
if "usuario_logueado" not in st.session_state:
    st.session_state["usuario_logueado"] = None
    st.session_state["rol_usuario"] = None
    st.session_state["nombre_usuario"] = None

if st.session_state["usuario_logueado"] is None:
    st.subheader("🔐 Iniciar Sesión")
    with st.form("form_login"):
        user_input = st.text_input("Usuario").strip().lower()
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
# BARRA LATERAL Y BOTONES DE RESPALDO DIRECTO
# ---------------------------------------------------------
if st.sidebar.button("Cerrar Sesión", type="secondary"):
    st.session_state["usuario_logueado"] = None
    st.session_state["rol_usuario"] = None
    st.session_state["nombre_usuario"] = None
    st.rerun()

def ir_a_liquidacion():
    st.session_state["opcion_menu"] = "🏍️ Liquidación Motorizados"

if st.session_state["rol_usuario"] == "Chofer":
    opciones_disponibles = ["🛵 Registrar Vuelta", "🏍️ Liquidación Motorizados"]
else:
    opciones_disponibles = [
        "🛵 Registrar Vuelta", "✅ Validar Precios", "💵 Corte Clientes", 
        "🏍️ Liquidación Motorizados", "👥 Directorio Clientes", "⚙️ Perfiles Motorizados"
    ]

opcion_menu = st.sidebar.radio("📌 Menú de Navegación", opciones_disponibles, key="opcion_menu")

st.sidebar.write("---")
st.sidebar.write("💾 **Respaldar Base de Datos**")
if os.path.exists("clientes.csv"):
    with open("clientes.csv", "rb") as f_cli:
        st.sidebar.download_button("📥 Descargar Clientes.csv", data=f_cli, file_name="clientes_backup.csv", mime="text/csv")
if os.path.exists("servicios.csv"):
    with open("servicios.csv", "rb") as f_ser:
        st.sidebar.download_button("📥 Descargar Servicios.csv", data=f_ser, file_name="servicios_backup.csv", mime="text/csv")

# ---------------------------------------------------------
# TAB 1: REGISTRAR VUELTA
# ---------------------------------------------------------
if opcion_menu == "🛵 Registrar Vuelta":
    if st.session_state.get("rol_usuario") == "Chofer":
        st.button("📊 Ver mi Balance y Avances", type="secondary", use_container_width=True, on_click=ir_a_liquidacion)

    es_admin = (st.session_state.get("rol_usuario") == "Admin")
    nombre_sesion = st.session_state.get("nombre_usuario", "")

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
            porcentaje_actual = st.number_input("Comisión Motorizado (%)", min_value=0.0, max_value=100.0, value=val_default, step=0.5, key=f"comision_input_{moto_sel}")
    else:
        moto_sel = nombre_sesion
        com_base_sug = df_motorizados.loc[df_motorizados['Nombre'] == moto_sel, 'Comision_Base'].values
        porcentaje_actual = float(com_base_sug[0]) if len(com_base_sug) > 0 else 66.67
        st.info(f"🛵 Registrando vuelta para el chofer: **{moto_sel}**")

    with st.form("form_agregar_vuelta", clear_on_submit=True):
        lista_cli = [""] + df_clientes['Nombre'].tolist()
        cli_sel = st.selectbox("Seleccionar Cliente", lista_cli, index=0)
        col1, col2 = st.columns(2)
        with col1:
            origen = st.text_input("Desde", value="Local")
        with col2:
            destino = st.text_input("Hasta", value="Local")
        
        precio_directo = st.number_input("Precio Cliente ($)", min_value=0.0, value=0.0, step=0.50) if es_admin else 0.0
        guardar_btn = st.form_submit_button("Precargar Vuelta", type="primary", use_container_width=True)

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
                'ID': nuevo_id, 'Fecha': fecha_final, 'Motorizado': moto_sel, 
                'Cliente': cliente_final, 'Origen': origen_final, 'Destino': destino_final, 
                'Detalle': "-", 'Precio_Cliente': precio_directo, 'Porcentaje_Comision': comision_val, 
                'Monto_Motorizado': monto_moto, 'Ganancia_Empresa': ganancia_emp, 
                'Estado_Validacion': estado_val, 'Estado_Cliente': 'Pendiente', 'Estado_Motorizado': 'Pendiente'
            }
            
            df_servicios = pd.concat([df_servicios, pd.DataFrame([nueva_fila])], ignore_index=True)
            df_servicios.to_csv("servicios.csv", index=False)
            st.success(f"✅ ¡Vuelta #{nuevo_id} guardada con éxito!")
            st.rerun()
        else:
            st.error("⚠️ Debes ingresar al menos el destino.")

# ---------------------------------------------------------
# TAB 2: VALIDAR Y EDITAR PRECIOS
# ---------------------------------------------------------
elif opcion_menu == "✅ Validar Precios":
    st.subheader("Validación y Corrección de Vueltas")
    vueltas_pendientes = df_servicios[df_servicios['Estado_Validacion'] == 'Pendiente']
    
    if not vueltas_pendientes.empty:
        for idx, row in vueltas_pendientes.iterrows():
            with st.expander(f"Vuelta #{row['ID']} - {row['Motorizado']} -> {row['Cliente']} ({row['Origen']} a {row['Destino']})", expanded=True):
                com_base = df_motorizados.loc[df_motorizados['Nombre'] == row['Motorizado'], 'Comision_Base'].values
                com_val = float(com_base[0]) if len(com_base) > 0 else 66.67
                col_v1, col_v2 = st.columns(2)
                with col_v1:
                    precio = st.number_input(f"Precio ($) [ID #{row['ID']}]", min_value=0.0, value=0.0, step=0.50, key=f"p_{row['ID']}")
                with col_v2:
                    comision = st.number_input(f"% Comisión [ID #{row['ID']}]", min_value=0.0, max_value=100.0, value=com_val, step=0.5, key=f"c_{row['ID']}")
                
                monto_moto = round(precio * (comision / 100.0), 2)
                ganancia_emp = round(precio - monto_moto, 2)
                
                if st.button(f"Validar Vuelta #{row['ID']}", type="primary", key=f"btn_{row['ID']}"):
                    if precio > 0:
                        df_servicios.loc[df_servicios['ID'] == row['ID'], ['Precio_Cliente', 'Porcentaje_Comision', 'Monto_Motorizado', 'Ganancia_Empresa', 'Estado_Validacion']] = [precio, comision, monto_moto, ganancia_emp, 'Validado']
                        df_servicios.to_csv("servicios.csv", index=False)
                        st.success(f"Vuelta #{row['ID']} validada.")
                        st.rerun()
                    else:
                        st.error("El precio debe ser mayor a $0.")
    else:
        st.info("No hay vueltas pendientes por validar.")

    if not df_servicios.empty:
        st.write("---")
        st.write("### ✏️ Corregir/Editar Vueltas Ya Registradas")
        st.dataframe(df_servicios[['ID', 'Fecha', 'Motorizado', 'Cliente', 'Origen', 'Destino', 'Precio_Cliente']], use_container_width=True)

# ---------------------------------------------------------
# TAB 3: CORTE CLIENTES Y ABONOS
# ---------------------------------------------------------
elif opcion_menu == "💵 Corte Clientes":
    st.subheader("Corte de Cuenta Clientes")
    df_abonos = pd.read_csv("abonos.csv") if os.path.exists("abonos.csv") else pd.DataFrame(columns=['ID', 'Fecha', 'Cliente', 'Monto', 'Concepto', 'Estado'])
    
    validados_cli = df_servicios[(df_servicios['Estado_Validacion'] == 'Validado') & (df_servicios['Estado_Cliente'] == 'Pendiente')]
    if not validados_cli.empty:
        cli_corte = st.selectbox("Seleccionar Cliente", sorted(validados_cli['Cliente'].unique().tolist()))
        
        with st.expander(f"➕ Registrar Abono de {cli_corte}"):
            with st.form("form_abono_cliente"):
                f_abono = st.date_input("Fecha")
                monto_ab = st.number_input("Monto ($)", min_value=0.0, step=0.50)
                concepto_ab = st.text_input("Concepto")
                guardar_ab_btn = st.form_submit_button("Guardar Abono")
            
            if guardar_ab_btn and monto_ab > 0:
                nuevo_reg_ab = {'ID': len(df_abonos) + 1, 'Fecha': f_abono.strftime("%d/%m/%Y"), 'Cliente': cli_corte, 'Monto': float(monto_ab), 'Concepto': concepto_ab, 'Estado': 'Pendiente'}
                df_abonos = pd.concat([df_abonos, pd.DataFrame([nuevo_reg_ab])], ignore_index=True)
                df_abonos.to_csv("abonos.csv", index=False)
                st.toast("✅ Abono registrado.")
                st.rerun()

        df_c = validados_cli[validados_cli['Cliente'] == cli_corte]
        st.dataframe(df_c[['Fecha', 'Origen', 'Destino', 'Precio_Cliente']], use_container_width=True)

# ---------------------------------------------------------
# TAB 4: LIQUIDACIÓN MOTORIZADOS Y AVANCES
# ---------------------------------------------------------
elif opcion_menu == "🏍️ Liquidación Motorizados":
    st.subheader("Liquidación y Balance de Motorizados")
    df_avances = pd.read_csv("avances.csv") if os.path.exists("avances.csv") else pd.DataFrame(columns=['ID', 'Fecha', 'Motorizado', 'Monto', 'Concepto', 'Estado'])
    
    mot_corte = st.selectbox("Seleccionar Motorizado", df_motorizados['Nombre'].tolist())
    
    with st.expander(f"➕ Registrar Avance a {mot_corte}"):
        with st.form("form_avance_motorizado"):
            f_av = st.date_input("Fecha")
            monto_av = st.number_input("Monto ($)", min_value=0.0, step=0.50)
            concepto_av = st.text_input("Concepto")
            btn_av = st.form_submit_button("Guardar Avance")
        
        if btn_av and monto_av > 0:
            nuevo_reg_av = {'ID': len(df_avances) + 1, 'Fecha': f_av.strftime("%d/%m/%Y"), 'Motorizado': mot_corte, 'Monto': float(monto_av), 'Concepto': concepto_av, 'Estado': 'Pendiente'}
            df_avances = pd.concat([df_avances, pd.DataFrame([nuevo_reg_av])], ignore_index=True)
            df_avances.to_csv("avances.csv", index=False)
            st.toast("✅ Avance registrado.")
            st.rerun()

    df_m = df_servicios[(df_servicios['Motorizado'] == mot_corte) & (df_servicios['Estado_Validacion'] == 'Validado')]
    st.dataframe(df_m[['Fecha', 'Cliente', 'Origen', 'Destino', 'Monto_Motorizado']], use_container_width=True)

import streamlit as st
import pandas as pd
import os
from datetime import datetime
import urllib.parse

st.set_page_config(page_title="MotoVueltas - Control Operativo", layout="wide", page_icon="🛵")

# ---------------------------------------------------------
# OCULTAR BARRA SUPERIOR Y MENÚ DE STREAMLIT
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

# ---------------------------------------------------------
# LECTURA DE DATOS DESDE ARCHIVOS CSV LOCALES
# ---------------------------------------------------------
def cargar_datos():
    # Clientes
    if os.path.exists("clientes.csv"):
        df_cli = pd.read_csv("clientes.csv")
    else:
        df_cli = pd.DataFrame([{"Nombre": "Cliente General", "Telefono": "04140000000", "Ubicacion": "Centro"}])
        df_cli.to_csv("clientes.csv", index=False)

    # Motorizados
    if os.path.exists("motorizados.csv"):
        df_mot = pd.read_csv("motorizados.csv")
    else:
        df_mot = pd.DataFrame([
            {"Nombre": "Omar", "Comision_Base": 66.67},
            {"Nombre": "Jhoiner", "Comision_Base": 66.67},
            {"Nombre": "Deiby", "Comision_Base": 66.67},
            {"Nombre": "Génesis", "Comision_Base": 66.67},
            {"Nombre": "Esneyder", "Comision_Base": 100.0}
        ])
        df_mot.to_csv("motorizados.csv", index=False)

    # Servicios
    if os.path.exists("servicios.csv"):
        df_ser = pd.read_csv("servicios.csv")
    else:
        df_ser = pd.DataFrame(columns=[
            'ID', 'Fecha', 'Motorizado', 'Cliente', 'Origen', 'Destino', 
            'Detalle', 'Precio_Cliente', 'Porcentaje_Comision', 
            'Monto_Motorizado', 'Ganancia_Empresa', 'Estado_Validacion', 
            'Estado_Cliente', 'Estado_Motorizado'
        ])
        df_ser.to_csv("servicios.csv", index=False)

    # Usuarios
    if os.path.exists("usuarios.csv"):
        df_usr = pd.read_csv("usuarios.csv")
    else:
        df_usr = pd.DataFrame([
            {"Usuario": "esneyder", "Clave": "339733", "Nombre": "Esneyder", "Rol": "Admin"},
            {"Usuario": "omar", "Clave": "5068", "Nombre": "Omar", "Rol": "Chofer"},
            {"Usuario": "jhoiner", "Clave": "8139", "Nombre": "Jhoiner", "Rol": "Chofer"},
            {"Usuario": "deiby", "Clave": "8455", "Nombre": "Deiby", "Rol": "Chofer"},
            {"Usuario": "genesis", "Clave": "7852", "Nombre": "Génesis", "Rol": "Chofer"}
        ])
        df_usr.to_csv("usuarios.csv", index=False)

    return df_cli, df_mot, df_ser, df_usr

df_clientes, df_motorizados, df_servicios, df_usuarios = cargar_datos()

st.title("🛵 MotoVueltas - Sistema de Gestión")

# ---------------------------------------------------------
# CONTROL DE SESIÓN Y LOGIN
# ---------------------------------------------------------
if "usuario_logueado" not in st.session_state:
    st.session_state["usuario_logueado"] = None
    st.session_state["rol_usuario"] = None
    st.session_state["nombre_usuario"] = None

if st.session_state["usuario_logueado"] is None:
    st.subheader("🔐 Iniciar Sesión")
    with st.form("form_login"):
        user_input = st.text_input("Usuario").strip().lower()
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
# BARRA LATERAL Y BOTONES DE RESPALDO DIRECTO
# ---------------------------------------------------------
if st.sidebar.button("Cerrar Sesión", type="secondary"):
    st.session_state["usuario_logueado"] = None
    st.session_state["rol_usuario"] = None
    st.session_state["nombre_usuario"] = None
    st.rerun()

def ir_a_liquidacion():
    st.session_state["opcion_menu"] = "🏍️ Liquidación Motorizados"

if st.session_state["rol_usuario"] == "Chofer":
    opciones_disponibles = ["🛵 Registrar Vuelta", "🏍️ Liquidación Motorizados"]
else:
    opciones_disponibles = [
        "🛵 Registrar Vuelta", "✅ Validar Precios", "💵 Corte Clientes", 
        "🏍️ Liquidación Motorizados", "👥 Directorio Clientes", "⚙️ Perfiles Motorizados"
    ]

opcion_menu = st.sidebar.radio("📌 Menú de Navegación", opciones_disponibles, key="opcion_menu")

st.sidebar.write("---")
st.sidebar.write("💾 **Respaldar Base de Datos**")
if os.path.exists("clientes.csv"):
    with open("clientes.csv", "rb") as f_cli:
        st.sidebar.download_button("📥 Descargar Clientes.csv", data=f_cli, file_name="clientes_backup.csv", mime="text/csv")
if os.path.exists("servicios.csv"):
    with open("servicios.csv", "rb") as f_ser:
        st.sidebar.download_button("📥 Descargar Servicios.csv", data=f_ser, file_name="servicios_backup.csv", mime="text/csv")

# ---------------------------------------------------------
# TAB 1: REGISTRAR VUELTA
# ---------------------------------------------------------
if opcion_menu == "🛵 Registrar Vuelta":
    if st.session_state.get("rol_usuario") == "Chofer":
        st.button("📊 Ver mi Balance y Avances", type="secondary", use_container_width=True, on_click=ir_a_liquidacion)

    es_admin = (st.session_state.get("rol_usuario") == "Admin")
    nombre_sesion = st.session_state.get("nombre_usuario", "")

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
            porcentaje_actual = st.number_input("Comisión Motorizado (%)", min_value=0.0, max_value=100.0, value=val_default, step=0.5, key=f"comision_input_{moto_sel}")
    else:
        moto_sel = nombre_sesion
        com_base_sug = df_motorizados.loc[df_motorizados['Nombre'] == moto_sel, 'Comision_Base'].values
        porcentaje_actual = float(com_base_sug[0]) if len(com_base_sug) > 0 else 66.67
        st.info(f"🛵 Registrando vuelta para el chofer: **{moto_sel}**")

    with st.form("form_agregar_vuelta", clear_on_submit=True):
        lista_cli = [""] + df_clientes['Nombre'].tolist()
        cli_sel = st.selectbox("Seleccionar Cliente", lista_cli, index=0)
        col1, col2 = st.columns(2)
        with col1:
            origen = st.text_input("Desde", value="Local")
        with col2:
            destino = st.text_input("Hasta", value="Local")
        
        precio_directo = st.number_input("Precio Cliente ($)", min_value=0.0, value=0.0, step=0.50) if es_admin else 0.0
        guardar_btn = st.form_submit_button("Precargar Vuelta", type="primary", use_container_width=True)

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
                'ID': nuevo_id, 'Fecha': fecha_final, 'Motorizado': moto_sel, 
                'Cliente': cliente_final, 'Origen': origen_final, 'Destino': destino_final, 
                'Detalle': "-", 'Precio_Cliente': precio_directo, 'Porcentaje_Comision': comision_val, 
                'Monto_Motorizado': monto_moto, 'Ganancia_Empresa': ganancia_emp, 
                'Estado_Validacion': estado_val, 'Estado_Cliente': 'Pendiente', 'Estado_Motorizado': 'Pendiente'
            }
            
            df_servicios = pd.concat([df_servicios, pd.DataFrame([nueva_fila])], ignore_index=True)
            df_servicios.to_csv("servicios.csv", index=False)
            st.success(f"✅ ¡Vuelta #{nuevo_id} guardada con éxito!")
            st.rerun()
        else:
            st.error("⚠️ Debes ingresar al menos el destino.")

# ---------------------------------------------------------
# TAB 2: VALIDAR Y EDITAR PRECIOS
# ---------------------------------------------------------
elif opcion_menu == "✅ Validar Precios":
    st.subheader("Validación y Corrección de Vueltas")
    vueltas_pendientes = df_servicios[df_servicios['Estado_Validacion'] == 'Pendiente']
    
    if not vueltas_pendientes.empty:
        for idx, row in vueltas_pendientes.iterrows():
            with st.expander(f"Vuelta #{row['ID']} - {row['Motorizado']} -> {row['Cliente']} ({row['Origen']} a {row['Destino']})", expanded=True):
                com_base = df_motorizados.loc[df_motorizados['Nombre'] == row['Motorizado'], 'Comision_Base'].values
                com_val = float(com_base[0]) if len(com_base) > 0 else 66.67
                col_v1, col_v2 = st.columns(2)
                with col_v1:
                    precio = st.number_input(f"Precio ($) [ID #{row['ID']}]", min_value=0.0, value=0.0, step=0.50, key=f"p_{row['ID']}")
                with col_v2:
                    comision = st.number_input(f"% Comisión [ID #{row['ID']}]", min_value=0.0, max_value=100.0, value=com_val, step=0.5, key=f"c_{row['ID']}")
                
                monto_moto = round(precio * (comision / 100.0), 2)
                ganancia_emp = round(precio - monto_moto, 2)
                
                if st.button(f"Validar Vuelta #{row['ID']}", type="primary", key=f"btn_{row['ID']}"):
                    if precio > 0:
                        df_servicios.loc[df_servicios['ID'] == row['ID'], ['Precio_Cliente', 'Porcentaje_Comision', 'Monto_Motorizado', 'Ganancia_Empresa', 'Estado_Validacion']] = [precio, comision, monto_moto, ganancia_emp, 'Validado']
                        df_servicios.to_csv("servicios.csv", index=False)
                        st.success(f"Vuelta #{row['ID']} validada.")
                        st.rerun()
                    else:
                        st.error("El precio debe ser mayor a $0.")
    else:
        st.info("No hay vueltas pendientes por validar.")

    if not df_servicios.empty:
        st.write("---")
        st.write("### ✏️ Corregir/Editar Vueltas Ya Registradas")
        st.dataframe(df_servicios[['ID', 'Fecha', 'Motorizado', 'Cliente', 'Origen', 'Destino', 'Precio_Cliente']], use_container_width=True)

# ---------------------------------------------------------
# TAB 3: CORTE CLIENTES Y ABONOS
# ---------------------------------------------------------
elif opcion_menu == "💵 Corte Clientes":
    st.subheader("Corte de Cuenta Clientes")
    df_abonos = pd.read_csv("abonos.csv") if os.path.exists("abonos.csv") else pd.DataFrame(columns=['ID', 'Fecha', 'Cliente', 'Monto', 'Concepto', 'Estado'])
    
    validados_cli = df_servicios[(df_servicios['Estado_Validacion'] == 'Validado') & (df_servicios['Estado_Cliente'] == 'Pendiente')]
    if not validados_cli.empty:
        cli_corte = st.selectbox("Seleccionar Cliente", sorted(validados_cli['Cliente'].unique().tolist()))
        
        with st.expander(f"➕ Registrar Abono de {cli_corte}"):
            with st.form("form_abono_cliente"):
                f_abono = st.date_input("Fecha")
                monto_ab = st.number_input("Monto ($)", min_value=0.0, step=0.50)
                concepto_ab = st.text_input("Concepto")
                guardar_ab_btn = st.form_submit_button("Guardar Abono")
            
            if guardar_ab_btn and monto_ab > 0:
                nuevo_reg_ab = {'ID': len(df_abonos) + 1, 'Fecha': f_abono.strftime("%d/%m/%Y"), 'Cliente': cli_corte, 'Monto': float(monto_ab), 'Concepto': concepto_ab, 'Estado': 'Pendiente'}
                df_abonos = pd.concat([df_abonos, pd.DataFrame([nuevo_reg_ab])], ignore_index=True)
                df_abonos.to_csv("abonos.csv", index=False)
                st.toast("✅ Abono registrado.")
                st.rerun()

        df_c = validados_cli[validados_cli['Cliente'] == cli_corte]
        st.dataframe(df_c[['Fecha', 'Origen', 'Destino', 'Precio_Cliente']], use_container_width=True)

# ---------------------------------------------------------
# TAB 4: LIQUIDACIÓN MOTORIZADOS Y AVANCES
# ---------------------------------------------------------
elif opcion_menu == "🏍️ Liquidación Motorizados":
    st.subheader("Liquidación y Balance de Motorizados")
    df_avances = pd.read_csv("avances.csv") if os.path.exists("avances.csv") else pd.DataFrame(columns=['ID', 'Fecha', 'Motorizado', 'Monto', 'Concepto', 'Estado'])
    
    mot_corte = st.selectbox("Seleccionar Motorizado", df_motorizados['Nombre'].tolist())
    
    with st.expander(f"➕ Registrar Avance a {mot_corte}"):
        with st.form("form_avance_motorizado"):
            f_av = st.date_input("Fecha")
            monto_av = st.number_input("Monto ($)", min_value=0.0, step=0.50)
            concepto_av = st.text_input("Concepto")
            btn_av = st.form_submit_button("Guardar Avance")
        
        if btn_av and monto_av > 0:
            nuevo_reg_av = {'ID': len(df_avances) + 1, 'Fecha': f_av.strftime("%d/%m/%Y"), 'Motorizado': mot_corte, 'Monto': float(monto_av), 'Concepto': concepto_av, 'Estado': 'Pendiente'}
            df_avances = pd.concat([df_avances, pd.DataFrame([nuevo_reg_av])], ignore_index=True)
            df_avances.to_csv("avances.csv", index=False)
            st.toast("✅ Avance registrado.")
            st.rerun()

    df_m = df_servicios[(df_servicios['Motorizado'] == mot_corte) & (df_servicios['Estado_Validacion'] == 'Validado')]
    st.dataframe(df_m[['Fecha', 'Cliente', 'Origen', 'Destino', 'Monto_Motorizado']], use_container_width=True)

# ---------------------------------------------------------
# TAB 5: DIRECTORIO DE CLIENTES
# ---------------------------------------------------------
elif opcion_menu == "👥 Directorio Clientes":
    st.subheader("Directorio de Clientes")

    with st.form("form_agregar_cliente", clear_on_submit=True):
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            nuevo_cli_nombre = st.text_input("Nombre / Negocio")
        with col_c2:
            nuevo_cli_tel = st.text_input("Teléfono (ID Único)")
        with col_c3:
            nuevo_cli_ubicacion = st.text_input("Ubicación")

        guardar_cli_btn = st.form_submit_button("Guardar Nuevo Cliente", type="primary", use_container_width=True)

    if guardar_cli_btn:
        tel_limpio = nuevo_cli_tel.strip()
        nom_limpio = nuevo_cli_nombre.strip()
        
        if not nom_limpio or not tel_limpio:
            st.error("⚠️ Tanto Nombre como Teléfono son obligatorios.")
        else:
            nuevo_registro_cli = {
                "Nombre": nom_limpio,
                "Telefono": tel_limpio,
                "Ubicacion": nuevo_cli_ubicacion.strip() if nuevo_cli_ubicacion.strip() else "-"
            }
            df_clientes = pd.concat([df_clientes, pd.DataFrame([nuevo_registro_cli])], ignore_index=True)
            df_clientes.to_csv("clientes.csv", index=False)
            st.success(f"✅ Cliente '{nom_limpio}' registrado con éxito.")
            st.rerun()

    st.write("---")
    st.dataframe(df_clientes[['Nombre', 'Telefono', 'Ubicacion']], use_container_width=True)
