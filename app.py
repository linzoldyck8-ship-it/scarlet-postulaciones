import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
import gspread
from google.oauth2.service_account import Credentials
import re  # Expresiones regulares para validar el correo electrónico

# --- FUNCIÓN DE VALIDACIÓN DE CORREO ELECTRÓNICO ---
def es_correo_valido(correo):
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(patron, correo) is not None

# --- CONFIGURACIÓN DE HORARIOS POR DIVISIÓN Y SUBDIVISIÓN ---
HORARIOS_DIVISIONES = {
    "Valorant": {
        "División A": "20:00 - 23:00 (Lun a Vie)"
        "Rango minimo": "inmortal",
        "División B": "18:00 - 21:00 (Lun a Vie)",
        "División C": "16:00 - 19:00 (Sáb y Dom)"
    },
    "CS GO": {
        "División A": "21:00 - 00:00 (Lun a Vie)",
        "División B": "19:00 - 22:00 (Mar a Sáb)",
        "División C": "17:00 - 20:00 (Fines de semana)"
    },
    "Overwatch": {
        "División A": "20:00 - 23:00 (Mar, Jue, Sáb)",
        "División B": "18:00 - 21:00 (Lun, Mié, Vie)",
        "División C": "16:00 - 19:00 (Sáb y Dom)"
    },
    "Valorant Femenino": {
        "División A": "19:00 - 22:00 (Lun a Jue)",
        "División B": "17:00 - 20:00 (Vie a Dom)"
    },
    "Fighting": {
        "División A": "20:00 - 22:00 (Mié y Vie)",
        "División B": "18:00 - 20:00 (Sáb y Dom)"
    }
}

# Configuración de la página
st.set_page_config(
    page_title="Scarlet Esports - Reclutamiento",
    page_icon="https://raw.githubusercontent.com/linzoldyck8-ship-it/valo-lino-/main/SCARLET.png",
    layout="wide"
)

# --- ESTILOS CSS AVANZADOS ---
st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-family: 'Arial Black', Arial, sans-serif !important;
    }
    .stApp {
        background-image: url("https://wallpapers.com/images/hd/pitch-black-leather-like-material-2w1vwucx1o9xzfvu.jpg");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        color: #f0f2f6;
    }
    [data-testid="stSidebar"] {
        background-color: rgba(18, 22, 31, 0.95);
        border-right: 2px solid #ff4655;
        box-shadow: 4px 0px 15px rgba(255, 70, 85, 0.2);
    }
    [data-testid="stMetric"] {
        background-color: rgba(22, 27, 34, 0.85);
        border: 1px solid rgba(255, 70, 85, 0.3);
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 0 10px rgba(255, 70, 85, 0.1);
    }
    [data-testid="stMetricLabel"] {
        color: #8b949e;
        font-size: 1.2rem !important;
        font-weight: 600;
    }
    [data-testid="stMetricValue"] {
        color: #ff4655 !important;
        text-shadow: 0 0 8px rgba(255, 70, 85, 0.4);
        font-size: 2.2rem !important;
    }
    h1, h2, h3 {
        font-family: 'Arial Black', Arial, sans-serif !important;
        letter-spacing: 1px;
    }
    h1 {
        color: #ffffff;
        text-shadow: 0 0 12px rgba(255, 70, 85, 0.5);
    }
    div[data-testid="stForm"] label p, div[data-testid="stSelectbox"] label p {
        font-size: 1.4rem !important;
        font-weight: bold;
    }
    div[data-testid="stForm"] div[data-baseweb="select"], 
    div[data-testid="stForm"] input {
        font-size: 1.3rem !important;
    }
    ul[role="listbox"] li {
        font-size: 1.3rem !important;
    }
    .stButton>button {
        background-color: #ff4655;
        color: white;
        border-radius: 6px;
        border: 1px solid #ff6b78;
        font-weight: bold;
        font-family: 'Arial Black', Arial, sans-serif !important;
        font-size: 1.3rem !important; 
        box-shadow: 0 0 10px rgba(255, 70, 85, 0.4);
        transition: 0.3s;
        padding: 10px 24px;
    }
    .stButton>button:hover {
        background-color: #fa5c68;
        box-shadow: 0 0 18px rgba(255, 70, 85, 0.8);
        color: white;
    }

    /* --- ESTILO GAMING PARA PESTAÑAS --- */
    [role="tablist"] {
        background-color: rgba(18, 22, 31, 0.6) !important;
        gap: 10px !important;
        padding: 8px 12px !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255, 70, 85, 0.2) !important;
    }

    [role="tab"] {
        background-color: transparent !important;
        border-radius: 6px !important;
        padding: 8px 20px !important;
        border: 1px solid transparent !important;
        transition: all 0.3s ease-in-out !important;
    }

    [role="tab"] p, [role="tab"] div {
        font-size: 1.15rem !important;
        font-weight: bold !important;
        color: #8b949e !important;
    }

    [role="tab"]:hover {
        background: linear-gradient(135deg, rgba(255, 70, 85, 0.2) 0%, rgba(255, 70, 85, 0.45) 100%) !important;
        border-color: rgba(255, 70, 85, 0.5) !important;
    }
    [role="tab"]:hover p, [role="tab"]:hover div {
        color: #ffffff !important;
    }

    [role="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, rgba(255, 70, 85, 0.4) 0%, rgba(255, 70, 85, 0.8) 100%) !important;
        border-color: #ff4655 !important;
        box-shadow: 0 0 15px rgba(255, 70, 85, 0.5) !important;
    }
    [role="tab"][aria-selected="true"] p, [role="tab"][aria-selected="true"] div {
        color: #ffffff !important;
        text-shadow: 0 0 8px rgba(0, 0, 0, 0.6);
    }

    [data-testid="stTabs"] [data-baseweb="tab-highlight"] {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# Configuración de Google Sheets API
SHEET_ID = "1a-D3wfr9XBwFIE34wAY-9-16eB3ABHndPsxq_6dbWqE"
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

@st.cache_resource(ttl=60)
def conectar_gsheets():
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        if "private_key" in creds_dict:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        workbook = client.open_by_key(SHEET_ID)
        return workbook
    except Exception as e:
        st.sidebar.error(f"❌ Error de conexión: {e}")
        return None

workbook = conectar_gsheets()

tab_formulario, tab_dashboard = st.tabs(["📝 Postularme al Roster", "📊 Panel Gerencial (Dashboard)"])

# --- APARTADO FORMULARIO ---
with tab_formulario:
    st.title("📝 Formulario de Postulación - Scarlet Esports")
    st.markdown("Selecciona la división y tu método de contacto preferido para completar tus datos.")

    # --- CONTROLES INTERACTIVOS (FUERA DEL FORMULARIO PARA ACTUALIZACIÓN EN TIEMPO REAL) ---
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        division = st.selectbox("🎮 Selecciona la División", ["Valorant", "Overwatch", "CS GO", "Valorant Femenino", "Fighting"])
    with col_sel2:
        tipo_contacto = st.selectbox("📞 Método de Contacto Preferido", ["Discord", "Instagram", "Número Telefónico", "Correo Electrónico"])

    # --- MOSTRAR HORARIOS SEGÚN LA DIVISIÓN SELECCIONADA ---
    if division in HORARIOS_DIVISIONES:
        sub_divs = HORARIOS_DIVISIONES[division]
        cols_horarios = st.columns(len(sub_divs))
        
        for idx, (sub_nombre, horario_txt) in enumerate(sub_divs.items()):
            with cols_horarios[idx]:
                st.markdown(f"""
                <div style="
                    background: rgba(22, 27, 34, 0.85);
                    border: 1px solid rgba(255, 70, 85, 0.4);
                    border-radius: 8px;
                    padding: 12px;
                    text-align: center;
                    box-shadow: 0 0 10px rgba(255, 70, 85, 0.15);
                    margin-bottom: 20px;
                ">
                    <span style="color: #ff4655; font-size: 1.1rem; font-weight: bold; display: block; margin-bottom: 4px;">
                        ⏰ {sub_nombre}
                    </span>
                    <span style="color: #f0f2f6; font-size: 0.95rem;">
                        {horario_txt}
                    </span>
                </div>
                """, unsafe_allow_html=True)

    with st.form("form_postulacion"):
        col_f1, col_f2 = st.columns(2)
        
        with col_f1:
            # Texto dinámico según la opción seleccionada afuera
            if tipo_contacto == "Discord":
                placeholder_txt = "Ej: usuario_discord o Scarlet#1234"
            elif tipo_contacto == "Instagram":
                placeholder_txt = "Ej: @mi_usuario_ig"
            elif tipo_contacto == "Número Telefónico":
                placeholder_txt = "Ej: +56912345678"
            else:
                placeholder_txt = "Ej: usuario@gmail.com"

            contacto_valor = st.text_input(f"Ingresa tu {tipo_contacto}", placeholder=placeholder_txt, autocomplete="off")
            edad = st.number_input("Edad", min_value=10, max_value=80, value=18, step=1)
            
            if division in ["Valorant", "Valorant Femenino"]:
                player_id = st.text_input("Riot ID (Ej: Scarlet#NA1)", autocomplete="off")
                rol = st.selectbox("Rol", ["Duelista", "Iniciador", "Controlador", "Centinela", "Flex"])
                rango_actual = st.selectbox("Rango Actual", ["Hierro-Plata", "Oro", "Platino", "Diamante", "Ascendente", "Inmortal", "Radiante"])
                peak_elo = st.selectbox("Peak Elo", ["Hierro-Plata", "Oro", "Platino", "Diamante", "Ascendente", "Inmortal", "Radiante"])
            
            elif division == "Overwatch":
                player_id = st.text_input("BattleTag (Ej: Scarlet#1234)", autocomplete="off")
                rol = st.selectbox("Rol", ["Tanque", "DPS", "Support", "Flex"])
                rango_actual = st.selectbox("Rango Actual", ["Bronce-Oro", "Platino", "Diamante", "Maestro", "Gran Maestro", "Champion"])
                peak_elo = st.selectbox("Peak Elo", ["Bronce-Oro", "Platino", "Diamante", "Maestro", "Gran Maestro", "Champion"])
            
            elif division == "CS GO":
                player_id = st.text_input("Steam ID o Link de Perfil", autocomplete="off")
                rol = st.selectbox("Rol", ["Entry Fragger", "AWPer", "IGL", "Lurker", "Support", "Flex"])
                rango_actual = st.text_input("Rango / Premier Rating Actual (Ej: Global, 15k)", autocomplete="off")
                peak_elo = st.text_input("Peak Elo / Max Rating", autocomplete="off")
                
            elif division == "Fighting":
                player_id = st.text_input("ID del Jugador (CFN, Tekken ID, etc.)", autocomplete="off")
                juego_esp = st.selectbox("Juego Específico", ["Street Fighter 6", "Tekken 8", "Mortal Kombat 1", "Guilty Gear", "Smash Bros", "Otro"])
                personaje = st.text_input("Personaje(s) Main", autocomplete="off")
                rango_actual = st.text_input("Rango Actual", autocomplete="off")
                peak_elo = st.text_input("Peak Elo", autocomplete="off")

        with col_f2:
            baneos = st.selectbox("Historial de Baneos / Toxicidad", ["Limpio", "Advertencia", "Chat Ban", "Ranked Ban", "Permanente/HWID"])
            notas = st.text_input("Link de Tracker / VODs / Notas adicionales", autocomplete="off")
            
            st.markdown("<br><br>", unsafe_allow_html=True) 
            submitted = st.form_submit_button("🚀 Enviar Postulación")

        if submitted:
            contacto_formateado = f"{tipo_contacto}: {contacto_valor.strip()}"
            
            if not contacto_valor.strip() or not player_id.strip():
                st.error(f"⚠️ Por favor ingresa tu {tipo_contacto} y tu ID de Jugador.")
            elif tipo_contacto == "Correo Electrónico" and not es_correo_valido(contacto_valor.strip()):
                st.error("⚠️ Por favor ingresa un correo electrónico válido (Ejemplo: usuario@dominio.com).")
            elif edad < 14:
                st.error("⚠️ Debes tener al menos 14 años para postularte a Scarlet Esports.")
            elif not workbook:
                st.error("⚠️ Error de conexión con Google Sheets.")
            else:
                try:
                    ws = workbook.worksheet(division)
                    
                    # --- COMPROBACIÓN DE DUPLICADOS ---
                    registros_existentes = ws.get_all_values()
                    duplicado = False
                    for fila in registros_existentes[1:]:
                        if len(fila) > 1 and (
                            fila[0].strip().lower() == player_id.strip().lower() or 
                            fila[1].strip().lower() == contacto_formateado.lower() or
                            fila[1].strip().lower() == contacto_valor.strip().lower()
                        ):
                            duplicado = True
                            break
                    
                    if duplicado:
                        st.error("⚠️ Ya existe una postulación registrada con este ID de Jugador o Contacto en esta división.")
                    else:
                        if division in ["Valorant", "Valorant Femenino"]:
                            nueva_fila = [player_id, contacto_formateado, str(edad), rango_actual, rol, peak_elo, baneos, "Tryout", notas]
                        elif division == "Overwatch":
                            nueva_fila = [player_id, contacto_formateado, str(edad), rango_actual, rol, peak_elo, baneos, "Tryout", notas]
                        elif division == "CS GO":
                            nueva_fila = [player_id, contacto_formateado, str(edad), rango_actual, rol, peak_elo, baneos, "Tryout", notas]
                        elif division == "Fighting":
                            nueva_fila = [player_id, contacto_formateado, str(edad), juego_esp, personaje, rango_actual, peak_elo, baneos, "Tryout", notas]
                        
                        ws.append_row(nueva_fila)
                        st.success(f"🎉 ¡Postulación a {division} enviada con éxito!")
                        
                except Exception as e:
                    st.error(f"Hubo un error al registrar tus datos: {e}")


# --- APARTADO DASHBOARD ---
with tab_dashboard:
    st.subheader("🔒 Acceso Restringido")
    clave_acceso = st.text_input("Ingrese la clave para ver el panel gerencial", type="password", autocomplete="off")
    
    if clave_acceso == "cazuela":
        count = st_autorefresh(interval=10000, limit=None, key="scarlet_autorefresh")

        st.title("🔥 PANEL GERENCIAL SCARLET ESPORTS")
        
        div_dashboard = st.sidebar.selectbox("📊 Analizar División", ["Valorant", "Overwatch", "CS GO", "Valorant Femenino", "Fighting"])
        st.markdown(f"### Mostrando métricas de: **{div_dashboard}**")

        st.sidebar.markdown("## ⚙️ Panel de Control")
        if st.sidebar.button("🔄 Sincronizar Datos"):
            st.cache_data.clear()
            st.success("¡Sincronizado correctamente!")
        st.sidebar.markdown("---")

        @st.cache_data(ttl=5)
        def load_data_from_sheet(sheet_name):
            try:
                ws = workbook.worksheet(sheet_name)
                data = ws.get_all_values()
                if len(data) > 1:
                    headers = data[0]
                    headers = [h if h.strip() != "" else f"Col_Extra_{i}" for i, h in enumerate(headers)]
                    df = pd.DataFrame(data[1:], columns=headers)
                    return df
                else:
                    return pd.DataFrame(columns=data[0] if data else [])
            except Exception as e:
                return pd.DataFrame()

        df = load_data_from_sheet(div_dashboard)

        if df.empty:
            st.warning(f"⚠️ Aún no hay datos de postulantes para la división {div_dashboard}.")
        else:
            df.columns = [str(c).strip() for c in df.columns]
            
            col_estado = next((c for c in df.columns if 'estado' in c.lower()), None)
            if not col_estado:
                df['Estado'] = 'Tryout'
                col_estado = 'Estado'

            col_contacto = next((c for c in df.columns if 'contacto' in c.lower() or 'discord' in c.lower()), df.columns[1])
            total_postulantes = len(df[df[col_contacto] != ''])
            tryouts_activos = len(df[df[col_estado].astype(str).str.strip().str.lower() == 'tryout']) 
            aceptados = len(df[df[col_estado].astype(str).str.strip().str.lower() == 'aceptado']) 

            col_baneos = next((c for c in df.columns if 'bano' in c.lower() or 'baneo' in c.lower() or 'historial' in c.lower()), None)
            baneos_alerta = len(df[df[col_baneos].astype(str).str.strip().isin(['Chat Ban', 'Ranked Ban', 'Permanente/HWID'])]) if col_baneos else 0

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Postulantes Totales", total_postulantes)
            col2.metric("Pruebas Activas", tryouts_activos, delta="En proceso")
            col3.metric("Plantel Aceptado", aceptados)
            col4.metric("Alertas de Baneos", baneos_alerta, delta_color="inverse" if baneos_alerta > 0 else "normal")

            st.markdown("---")

            col_g1, col_g2 = st.columns(2)

            with col_g1:
                st.subheader("📊 Distribución por Estado")
                if not df[col_estado].empty:
                    fig_estado = px.pie(df, names=col_estado, hole=0.5, color_discrete_sequence=px.colors.sequential.Reds)
                    fig_estado.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#f0f2f6')
                    st.plotly_chart(fig_estado, use_container_width=True)

            with col_g2:
                if div_dashboard == "Fighting":
                    st.subheader("🥊 Demanda por Juego")
                    col_juego = next((c for c in df.columns if 'juego' in c.lower()), None)
                    if col_juego and not df[col_juego].empty:
                        juego_counts = df[col_juego].value_counts().reset_index()
                        juego_counts.columns = ['Juego', 'Cantidad']
                        fig_roles = px.bar(juego_counts, x='Juego', y='Cantidad', color='Juego', color_discrete_sequence=['#ff4655', '#e94560', '#ff6b6b'])
                        fig_roles.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#f0f2f6', showlegend=False)
                        st.plotly_chart(fig_roles, use_container_width=True)
                else:
                    st.subheader("⚔️ Demanda por Rol")
                    col_rol = next((c for c in df.columns if 'rol' in c.lower()), None)
                    if col_rol and not df[col_rol].empty:
                        rol_counts = df[col_rol].value_counts().reset_index()
                        rol_counts.columns = ['Rol', 'Cantidad']
                        fig_roles = px.bar(rol_counts, x='Rol', y='Cantidad', color='Rol', color_discrete_sequence=['#ff4655', '#e94560', '#ff6b6b'])
                        fig_roles.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#f0f2f6', showlegend=False)
                        st.plotly_chart(fig_roles, use_container_width=True)

            st.subheader("📋 Registro Detallado")
            st.dataframe(df, use_container_width=True)
            
    elif clave_acceso:
        st.error("❌ Contraseña incorrecta. Acceso denegado.")
