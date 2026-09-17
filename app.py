import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
import gspread
from google.oauth2.service_account import Credentials

# Configuración de la página con URL directa para el ícono
st.set_page_config(
    page_title="Scarlet Valorant - Reclutamiento",
    page_icon="https://raw.githubusercontent.com/linzoldyck8-ship-it/valo-lino-/main/SCARLET.png",  # <-- PEGA AQUÍ LA URL DIRECTA DE TU ÍCONO
    layout="wide"
)

# --- ESTILOS CSS AVANZADOS ---
st.markdown("""
    <style>
    /* CAMBIO A ARIAL BLACK */
    html, body, [class*="css"] {
        font-family: 'Arial Black', Arial, sans-serif !important;
    }

    .stApp {
        background-image: url("https://wallpapers.com/images/hd/pitch-black-leather-like-material-2w1vwucx1o9xzfvu.jpg"); /* <-- PEGA AQUÍ LA URL DE TU FONDO */
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

    /* --- AUMENTAR FUENTE DE LAS SELECCIONES Y FORMULARIO --- */
    div[data-testid="stForm"] label p {
        font-size: 1.5rem !important;
        font-weight: bold;
    }
    
    div[data-testid="stForm"] div[data-baseweb="select"], 
    div[data-testid="stForm"] input {
        font-size: 1.3rem !important;
    }

    /* Aumentar el tamaño de las opciones desplegables */
    ul[role="listbox"] li {
        font-size: 1.3rem !important;
    }
    /* ----------------------------------------------------------- */

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

# Configuración de Google Sheets API para escritura
SHEET_ID = "1TJAoGBPhpxKvzLR9iza1vCgFcBb8rq7EDNz8Fl7knCA"
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

@st.cache_resource(ttl=60)
def conectar_gsheets():
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        
        if "private_key" in creds_dict:
            creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SHEET_ID).sheet1
        return sheet
    except Exception as e:
        st.sidebar.error(f"❌ Error de conexión: {e}")
        return None

sheet_ws = conectar_gsheets()

# --- PESTAÑAS PRINCIPALES (Orden Invertido) ---
tab_formulario, tab_dashboard = st.tabs(["📝 Postularme al Roster", "📊 Panel Gerencial (Dashboard)"])

# --- APARTADO FORMULARIO (Se muestra primero por defecto) ---
with tab_formulario:
    st.title("📝 Formulario de Postulación - Scarlet Valorant")
    st.markdown("Completa tus datos correctamente para postularte al roster competitivo. Tu información se registrará de inmediato.")

    with st.form("form_postulacion"):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            contacto_discord = st.text_input("Contacto discord")
            riot_id = st.text_input("Riot ID (Ej: Scarlet#NA1)")
            rol_principal = st.selectbox("Rol Principal", ["Duelista", "Iniciador", "Controlador", "Centinela", "Flex"])
            rol_secundario = st.selectbox("Rol Secundario", ["Duelista", "Iniciador", "Controlador", "Centinela", "Flex"])
            rango_actual = st.selectbox("Rango Actual", ["Hierro-Plata", "Oro", "Platino", "Diamante", "Ascendente", "Inmortal 1", "Inmortal 2", "Inmortal 3", "Radiante"])

        with col_f2:
            peak_elo = st.selectbox("Peak Elo (Máximo Rango Histórico)", ["Hierro-Plata", "Oro", "Platino", "Diamante", "Ascendente", "Inmortal 1", "Inmortal 2", "Inmortal 3", "Radiante"])
            baneos = st.selectbox("Historial de Baneos / Toxicidad", ["Limpio", "Advertencia", "Chat Ban", "Ranked Ban", "Permanente/HWID"])
            horario = st.selectbox("Horario Disponible", ["Mañana", "Tarde", "Noche", "Madrugada", "Flexible"])
            notas = st.text_input("Link de Tracker.gg o VLR.gg / Notas")

        submitted = st.form_submit_button("🚀 Enviar Postulación")

        if submitted:
            if not contacto_discord or not riot_id:
                st.error("⚠️ Por favor completa al menos tu Contacto discord y tu Riot ID.")
            elif not sheet_ws:
                st.error("⚠️ Error de conexión con Google Sheets. Verifica el archivo credentials.json.")
            else:
                try:
                    data_rows = sheet_ws.get_all_values()
                    nuevo_id = len(data_rows)
                    
                    nueva_fila = [
                        str(nuevo_id),
                       contacto_discord,
                        riot_id,
                        rol_principal,
                        rol_secundario,
                        rango_actual,
                        peak_elo,
                        baneos,
                        horario,
                        "Nuevo",
                        notas
                    ]
                    
                    sheet_ws.append_row(nueva_fila)
                    st.success("🎉 ¡Postulación enviada con éxito! Ya estás registrado en la base de datos oficial de Scarlet.")
                except Exception as e:
                    st.error(f"Hubo un error al registrar tus datos: {e}")

# --- APARTADO DASHBOARD (Protegido con contraseña) ---
with tab_dashboard:
    st.subheader("🔒 Acceso Restringido")
    # Ingreso de contraseña
    clave_acceso = st.text_input("Ingrese la clave para ver el panel gerencial", type="password")
    
    # CAMBIA "scarletadmin" POR LA CONTRASEÑA QUE DESEES
    if clave_acceso == "cazuela":
        
        count = st_autorefresh(interval=5000, limit=None, key="scarlet_autorefresh")

        st.title("🔥 POSTULACIONES SCARLET VALORANT")
        st.markdown("Panel de control ejecutivo y monitoreo en tiempo real del roster competitivo.")

        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

        st.sidebar.markdown("## ⚙️ Panel de Control")
        if st.sidebar.button("🔄 Sincronizar Datos"):
            st.cache_data.clear()
            st.success("¡Sincronizado correctamente!")

        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🔍 Filtros de Búsqueda")

        @st.cache_data(ttl=2)
        def load_data():
            try:
                df = pd.read_csv(url)
                return df
            except Exception as e:
                return pd.DataFrame()

        df = load_data()

        if df.empty:
            st.warning("⚠️ No se pudieron cargar los datos. Verifica que el Google Sheet sea público.")
        else:
            df.columns = [str(c).strip() for c in df.columns]

            total_postulantes = len(df.dropna(subset=['Contacto discord'])) if 'Contacto discord' in df.columns else len(df)
            tryouts_activos = len(df[df['Estado'].astype(str).str.strip() == 'Tryout']) if 'Estado' in df.columns else 0
            aceptados = len(df[df['Estado'].astype(str).str.strip() == 'Aceptado']) if 'Estado' in df.columns else 0

            baneos_alerta = 0
            col_baneos = None
            for c in df.columns:
                if 'bano' in c.lower() or 'baneo' in c.lower() or 'toxicidad' in c.lower():
                    col_baneos = c
                    break
            if col_baneos:
                baneos_alerta = len(df[df[col_baneos].astype(str).str.strip().isin(['Chat Ban', 'Ranked Ban', 'Permanente/HWID'])])

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Postulantes Totales", total_postulantes)
            col2.metric("Pruebas Activas", tryouts_activos, delta="En proceso")
            col3.metric("Plantel Aceptado", aceptados)
            col4.metric("Alertas de Baneos", baneos_alerta, delta_color="inverse" if baneos_alerta > 0 else "normal")

            st.markdown("---")

            rol_opciones = ["Todos"] + list(df['Rol Principal'].dropna().unique()) if 'Rol Principal' in df.columns else ["Todos"]
            rol_filtro = st.sidebar.selectbox("Rol Principal", rol_opciones)
            
            estado_opciones = ["Todos"] + list(df['Estado'].dropna().unique()) if 'Estado' in df.columns else ["Todos"]
            estado_filtro = st.sidebar.selectbox("Estado del Proceso", estado_opciones)

            df_filtered = df.copy()
            if rol_filtro != "Todos" and 'Rol Principal' in df.columns:
                df_filtered = df_filtered[df_filtered['Rol Principal'] == rol_filtro]
            if estado_filtro != "Todos" and 'Estado' in df.columns:
                df_filtered = df_filtered[df_filtered['Estado'] == estado_filtro]

            col_g1, col_g2 = st.columns(2)

            with col_g1:
                st.subheader("📊 Distribución por Estado")
                if 'Estado' in df.columns and not df['Estado'].dropna().empty:
                    fig_estado = px.pie(df, names='Estado', hole=0.5, color_discrete_sequence=px.colors.sequential.Reds)
                    fig_estado.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#f0f2f6')
                    st.plotly_chart(fig_estado, use_container_width=True)

            with col_g2:
                st.subheader("⚔️ Demanda por Rol")
                if 'Rol Principal' in df.columns and not df['Rol Principal'].dropna().empty:
                    rol_counts = df['Rol Principal'].value_counts().reset_index()
                    rol_counts.columns = ['Rol', 'Cantidad']
                    fig_roles = px.bar(rol_counts, x='Rol', y='Cantidad', 
                                       color='Rol', color_discrete_sequence=['#ff4655', '#e94560', '#ff6b6b', '#c70039', '#900c3f'])
                    fig_roles.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#f0f2f6', showlegend=False)
                    st.plotly_chart(fig_roles, use_container_width=True)

            st.subheader("📋 Registro Detallado de Postulantes")
            possible_cols = ['Nº', 'Contacto discord', 'Riot ID (#TAG)', 'Rol Principal', 'Rango Actual', 'Peak Elo', 'Baneos / Toxicidad', 'Estado']
            cols_to_show = [c for c in possible_cols if c in df_filtered.columns]
            st.dataframe(df_filtered[cols_to_show], use_container_width=True)
            
    elif clave_acceso:
        st.error("❌ Contraseña incorrecta. Acceso denegado.")
