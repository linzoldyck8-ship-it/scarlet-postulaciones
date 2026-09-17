import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
import gspread
from google.oauth2.service_account import Credentials

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
    div[data-testid="stForm"] label p {
        font-size: 1.5rem !important;
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
    st.markdown("Selecciona la división a la que deseas aplicar y completa tus datos correctamente.")

    # Listas oficiales permitidas para validación posterior
    opciones_division = ["Valorant", "Overwatch", "CS GO", "Valorant Femenino", "Fighting"]
    division = st.selectbox("🎮 Selecciona la División", opciones_division)

    with st.form("form_postulacion"):
        col_f1, col_f2 = st.columns(2)
        
        with col_f1:
            contacto_discord = st.text_input("Contacto Discord (Usuario)", autocomplete="off")
            edad = st.number_input("Edad", min_value=10, max_value=80, value=18, step=1)
            
            if division in ["Valorant", "Valorant Femenino"]:
                player_id = st.text_input("Riot ID (Ej: Scarlet#NA1)", autocomplete="off")
                roles_validos = ["Duelista", "Iniciador", "Controlador", "Centinela", "Flex"]
                rol = st.selectbox("Rol", roles_validos)
                rangos_val = ["Hierro-Plata", "Oro", "Platino", "Diamante", "Ascendente", "Inmortal", "Radiante"]
                rango_actual = st.selectbox("Rango Actual", rangos_val)
                peak_elo = st.selectbox("Peak Elo", rangos_val)
            
            elif division == "Overwatch":
                player_id = st.text_input("BattleTag (Ej: Scarlet#1234)", autocomplete="off")
                roles_validos = ["Tanque", "DPS", "Support", "Flex"]
                rol = st.selectbox("Rol", roles_validos)
                rangos_val = ["Bronce-Oro", "Platino", "Diamante", "Maestro", "Gran Maestro", "Champion"]
                rango_actual = st.selectbox("Rango Actual", rangos_val)
                peak_elo = st.selectbox("Peak Elo", rangos_val)
            
            elif division == "CS GO":
                player_id = st.text_input("Steam ID o Link de Perfil", autocomplete="off")
                roles_validos = ["Entry Fragger", "AWPer", "IGL", "Lurker", "Support", "Flex"]
                rol = st.selectbox("Rol", roles_validos)
                rango_actual = st.text_input("Rango / Premier Rating Actual (Ej: Global, 15k)", autocomplete="off")
                peak_elo = st.text_input("Peak Elo / Max Rating", autocomplete="off")
                
            elif division == "Fighting":
                player_id = st.text_input("ID del Jugador (CFN, Tekken ID, etc.)", autocomplete="off")
                juegos_validos = ["Street Fighter 6", "Tekken 8", "Mortal Kombat 1", "Guilty Gear", "Smash Bros", "Otro"]
                juego_esp = st.selectbox("Juego Específico", juegos_validos)
                personaje = st.text_input("Personaje(s) Main", autocomplete="off")
                rango_actual = st.text_input("Rango Actual", autocomplete="off")
                peak_elo = st.text_input("Peak Elo", autocomplete="off")

        with col_f2:
            baneos_validos = ["Limpio", "Advertencia", "Chat Ban", "Ranked Ban", "Permanente/HWID"]
            baneos = st.selectbox("Historial de Baneos / Toxicidad", baneos_validos)
            
            horarios_validos = ["Mañana", "Tarde", "Noche", "Madrugada", "Flexible"]
            horario = st.selectbox("Horario Disponible", horarios_validos)
            
            notas = st.text_input("Link de Tracker / VODs / Notas adicionales", autocomplete="off")
            
            st.markdown("<br><br>", unsafe_allow_html=True) 
            submitted = st.form_submit_button("🚀 Enviar Postulación")

        if submitted:
            # Validación estricta para evitar que ingresen valores alterados manualmente en selects
            if division == "Fighting" and juego_esp not in ["Street Fighter 6", "Tekken 8", "Mortal Kombat 1", "Guilty Gear", "Smash Bros", "Otro"]:
                st.error("⚠️ Selecciona un juego válido de la lista desplegable.")
            elif division in ["Valorant", "Valorant Femenino", "Overwatch", "CS GO"] and rol not in roles_validos:
                st.error("⚠️ Selecciona un rol válido de la lista desplegable.")
            elif baneo_invalido := (baneos not in baneos_validos):
                st.error("⚠️ Selecciona un historial de baneos válido de la lista.")
            elif horario not in horarios_validos:
                st.error("⚠️ Selecciona un horario disponible válido de la lista.")
            elif not contacto_discord or not player_id:
                st.error("⚠️ Por favor completa tu Contacto de Discord y tu ID de Jugador.")
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
                        if len(fila) > 1 and (fila[0].strip().lower() == player_id.strip().lower() or fila[1].strip().lower() == contacto_discord.strip().lower()):
                            duplicado = True
                            break
                    
                    if duplicado:
                        st.error("⚠️ Ya existe una postulación registrada con este ID de Jugador o Usuario de Discord en esta división.")
                    else:
                        if division in ["Valorant", "Valorant Femenino"]:
                            nueva_fila = [player_id, contacto_discord, str(edad), rango_actual, rol, peak_elo, baneos, horario, "Tryout", notas]
                        elif division == "Overwatch":
                            nueva_fila = [player_id, contacto_discord, str(edad), rango_actual, rol, peak_elo, baneos, horario, "Tryout", notas]
                        elif division == "CS GO":
                            nueva_fila = [player_id, contacto_discord, str(edad), rango_actual, rol, peak_elo, baneos, horario, "Tryout", notas]
                        elif division == "Fighting":
                            nueva_fila = [player_id, contacto_discord, str(edad), juego_esp, personaje, rango_actual, peak_elo, baneos, horario, "Tryout", notas]
                        
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

            col_discord = next((c for c in df.columns if 'discord' in c.lower()), df.columns[1])
            total_postulantes = len(df[df[col_discord] != ''])
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
