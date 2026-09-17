import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh
import gspread
from google.oauth2.service_account import Credentials
import re
import datetime

# --- LISTAS DETALLADAS DE RANGOS POR JUEGO ---
RANGOS_VALORANT = [
    "Hierro 1", "Hierro 2", "Hierro 3",
    "Bronce 1", "Bronce 2", "Bronce 3",
    "Plata 1", "Plata 2", "Plata 3",
    "Oro 1", "Oro 2", "Oro 3",
    "Platino 1", "Platino 2", "Platino 3",
    "Diamante 1", "Diamante 2", "Diamante 3",
    "Ascendente 1", "Ascendente 2", "Ascendente 3",
    "Inmortal 1", "Inmortal 2", "Inmortal 3",
    "Radiante"
]

RANGOS_OVERWATCH = [
    "Bronce 5", "Bronce 4", "Bronce 3", "Bronce 2", "Bronce 1",
    "Plata 5", "Plata 4", "Plata 3", "Plata 2", "Plata 1",
    "Oro 5", "Oro 4", "Oro 3", "Oro 2", "Oro 1",
    "Platino 5", "Platino 4", "Platino 3", "Platino 2", "Platino 1",
    "Esmeralda 5","Esmeralda 4","Esmeralda 3","Esmeralda 2","Esmeralda 1",
    "Diamante 5", "Diamante 4", "Diamante 3", "Diamante 2", "Diamante 1",
    "Maestro 5", "Maestro 4", "Maestro 3", "Maestro 2", "Maestro 1",
    "Gran Maestro 5", "Gran Maestro 4", "Gran Maestro 3", "Gran Maestro 2", "Gran Maestro 1",
    "TOP 500"
]

ETIQUETAS_ID = {
    "Valorant": "Riot ID",
    "Valorant Femenino": "Riot ID",
    "Overwatch": "BattleTag",
    "CS": "Steam ID",
    "Fighting": "ID Jugador"
}

def es_correo_valido(correo):
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(patron, correo) is not None

HORARIOS_DIVISIONES = {
    "Valorant": {
        "División A": {"horario": "20:00 - 23:00 (Lun a Vie)", "rango": "Inmortal"},
        "División B": {"horario": "21:00 - 23:00 (Lun a Vie)", "rango": "plata"},
        "División C": {"horario": "16:00 - 19:00 (Sáb y Dom)", "rango": "Diamante"}
    },
    "CS": {
        "División A": {"horario": "22:00 - 01:00 (Lun a Vie)", "rango": "Nivel 5 Faceit/ 10 GC"},
    },
    "Overwatch": {
        "División A": {"horario": "20:00 - 23:00 (Mar, Jue, Sáb)", "rango": "Gran Maestro"},
        "División B": {"horario": "18:00 - 21:00 (Lun, Mié, Vie)", "rango": "Maestro"},
        "División C": {"horario": "16:00 - 19:00 (Sáb y Dom)", "rango": "Diamante"}
    },
    "Valorant Femenino": {
        "División A": {"horario": "21:00 - 23:00 (Lun a Vie)", "rango": "Ascendente"},
    },
    "Fighting": {
        "División A": {"horario": "20:00 - 22:00 (Mié y Vie)", "rango": "Master / High Rank"},
        "División B": {"horario": "18:00 - 20:00 (Sáb y Dom)", "rango": "Diamond+"}
    }
}

st.set_page_config(
    page_title="Scarlet Esports - Reclutamiento",
    page_icon="https://raw.githubusercontent.com/linzoldyck8-ship-it/valo-lino-/main/SCARLET.png",
    layout="wide"
)

components.html("""
<script>
function bloquearPopups() {
    const doc = window.parent.document;
    
    if (!doc.getElementById('extension-blocker-style')) {
        const style = doc.createElement('style');
        style.id = 'extension-blocker-style';
        style.innerHTML = `
            [data-protonpass-icon],
            [data-lastpass-icon-root],
            [data-bw-icon],
            iframe[src*="relay"],
            iframe[src*="firefox"],
            div[class*="relay-input"],
            div[id*="relay"],
            div[class*="protonpass"],
            div[data-1password-type],
            div[class*="passwords-"] {
                display: none !important;
                visibility: hidden !important;
                opacity: 0 !important;
                pointer-events: none !important;
            }
        `;
        doc.head.appendChild(style);
    }

    const inputs = doc.querySelectorAll('input, textarea');
    inputs.forEach(input => {
        input.setAttribute('autocomplete', 'off');
        input.setAttribute('data-bwignore', 'true');
        input.setAttribute('data-lpignore', 'true');
        input.setAttribute('data-1p-ignore', 'true');
        input.setAttribute('data-protonpass-ignore', 'true');
        input.setAttribute('data-dashlane-ignore', 'true');
        input.setAttribute('data-nordpass-ignore', 'true');
        input.setAttribute('data-form-type', 'other');
        input.setAttribute('aria-autocomplete', 'none');
        input.setAttribute('spellcheck', 'false');
    });
}
setTimeout(bloquearPopups, 100);
setInterval(bloquearPopups, 500);
</script>
""", height=0)

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

    div[data-testid="stFormSubmitButton"] button,
    button[kind="primaryFormSubmit"],
    button[data-testid="stBaseButton-primaryFormSubmit"] {
        background-color: #ff4655 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        border: 2px solid #ff6b78 !important;
        font-weight: 900 !important;
        font-family: 'Arial Black', Arial, sans-serif !important;
        padding: 16px 24px !important;
        min-height: 65px !important;
        box-shadow: 0 0 20px rgba(255, 70, 85, 0.6) !important;
        transition: all 0.3s ease-in-out !important;
    }

    div[data-testid="stFormSubmitButton"] button *,
    button[kind="primaryFormSubmit"] *,
    button[data-testid="stBaseButton-primaryFormSubmit"] * {
        font-size: 1.9rem !important;
        font-weight: 900 !important;
    }

    div[data-testid="stFormSubmitButton"] button:hover,
    button[kind="primaryFormSubmit"]:hover,
    button[data-testid="stBaseButton-primaryFormSubmit"]:hover {
        background-color: #fa5c68 !important;
        box-shadow: 0 0 35px rgba(255, 70, 85, 1) !important;
        transform: scale(1.02);
        color: white !important;
    }

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

@st.cache_data(ttl=10)
def obtener_password_admin():
    if not workbook:
        return "cazuela"
    try:
        ws = workbook.worksheet("Configuracion")
        val = ws.acell("A2").value
        return val.strip() if val and val.strip() != "" else "cazuela"
    except gspread.exceptions.WorksheetNotFound:
        try:
            ws = workbook.add_worksheet(title="Configuracion", rows="10", cols="2")
            ws.update_acell("A1", "Password")
            ws.update_acell("A2", "cazuela")
            return "cazuela"
        except Exception:
            return "cazuela"
    except Exception:
        return "cazuela"

def actualizar_password_admin(nueva_clave):
    try:
        ws = workbook.worksheet("Configuracion")
        ws.update_acell("A2", nueva_clave)
        st.cache_data.clear()
        return True
    except Exception:
        return False

def obtener_hoja_lista_negra(wb):
    try:
        return wb.worksheet("Lista Negra")
    except gspread.exceptions.WorksheetNotFound:
        ws = wb.add_worksheet(title="Lista Negra", rows="1000", cols="5")
        ws.append_row(["ID_Jugador", "Contacto", "Fecha_Vetado", "Motivo", "División_Origen"])
        return ws
    except Exception:
        return None

tab_formulario, tab_dashboard = st.tabs(["📝 Postularme al Roster", "📊 Panel Gerencial (Dashboard)"])

with tab_formulario:
    st.title("📝 Formulario de Postulación - Scarlet Esports")
    st.markdown("Selecciona la división y tu método de contacto preferido para completar tus datos.")

    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        division = st.selectbox("🎮 Selecciona la División", ["Valorant", "Overwatch", "CS", "Valorant Femenino", "Fighting"])
    with col_sel2:
        tipo_contacto = st.selectbox("📞 Método de Contacto Preferido", ["Discord", "Instagram", "Número Telefónico", "Correo Electrónico"])

    if division in HORARIOS_DIVISIONES:
        sub_divs = HORARIOS_DIVISIONES[division]
        cols_horarios = st.columns(len(sub_divs))
        
        for idx, (sub_nombre, info) in enumerate(sub_divs.items()):
            with cols_horarios[idx]:
                st.markdown(f"""
                <div style="
                    background: rgba(22, 27, 34, 0.85);
                    border: 2px solid rgba(255, 70, 85, 0.5);
                    border-radius: 10px;
                    padding: 14px 10px;
                    text-align: center;
                    box-shadow: 0 0 15px rgba(255, 70, 85, 0.2);
                    margin-bottom: 20px;
                ">
                    <span style="color: #ff4655; font-size: 1.35rem; font-weight: 900; display: block; margin-bottom: 6px;">
                        ⏰ {sub_nombre}
                    </span>
                    <span style="color: #ffffff; font-size: 1.65rem; font-weight: 900; display: block; margin-bottom: 4px; text-shadow: 0 0 10px rgba(255, 255, 255, 0.2);">
                        {info['horario']}
                    </span>
                    <span style="color: #a3b1c2; font-size: 1.05rem; font-weight: bold; display: block; margin-bottom: 10px;">
                        (Hora Chile)
                    </span>
                    <span style="color: #ff4655; font-size: 1.15rem; font-weight: bold; display: block; letter-spacing: 0.5px;">
                        RANGO MÍNIMO: <span style="color: #ffffff;">{info['rango']}</span>
                    </span>
                </div>
                """, unsafe_allow_html=True)

    with st.form("form_postulacion"):
        col_f1, col_f2 = st.columns(2)
        
        with col_f1:
            if tipo_contacto == "Discord":
                placeholder_txt = "Ej: usuario_discord o Scarlet#1234"
            elif tipo_contacto == "Instagram":
                placeholder_txt = "Ej: @mi_usuario_ig"
            elif tipo_contacto == "Número Telefónico":
                placeholder_txt = "Ej: +56912345678"
            else:
                placeholder_txt = "Ej: usuario@dominio.com"

            contacto_valor = st.text_input(f"Ingresa tu {tipo_contacto}", placeholder=placeholder_txt)
            edad = st.number_input("Edad", min_value=10, max_value=80, value=18, step=1)
            
            if division in ["Valorant", "Valorant Femenino"]:
                player_id = st.text_input("Riot ID (Ej: Scarlet#NA1)")
                rol = st.selectbox("Rol", ["Duelista", "Iniciador", "Controlador", "Centinela", "Flex"])
                rango_actual = st.selectbox("Rango Actual", RANGOS_VALORANT)
                peak_elo = st.selectbox("Peak Elo", RANGOS_VALORANT)
            
            elif division == "Overwatch":
                player_id = st.text_input("BattleTag (Ej: Scarlet#1234)")
                rol = st.selectbox("Rol", ["Tanque", "DPS", "Support", "Flex"])
                rango_actual = st.selectbox("Rango Actual", RANGOS_OVERWATCH)
                peak_elo = st.selectbox("Peak Elo", RANGOS_OVERWATCH)
            
            elif division == "CS":
                player_id = st.text_input("Steam ID o Link de Perfil")
                rol = st.selectbox("Rol", ["Entry Fragger", "AWPer", "IGL", "Lurker", "Support", "Rifler"])
                rango_actual = st.text_input("Rango / Premier Rating Actual (Ej: Global, 15k, FACEIT Lvl 10)")
                peak_elo = st.text_input("Peak Elo / Max Rating")
                
            elif division == "Fighting":
                player_id = st.text_input("ID del Jugador (CFN, Tekken ID, etc.)")
                juego_esp = st.selectbox("Juego Específico", ["Street Fighter 6", "Tekken 8", "Mortal Kombat 1", "Guilty Gear", "Smash Bros", "Otro"])
                personaje = st.text_input("Personaje(s) Main")
                rango_actual = st.text_input("Rango Actual")
                peak_elo = st.text_input("Peak Elo")

        with col_f2:
            baneos = st.selectbox("Historial de Baneos / Toxicidad", ["Limpio", "Advertencia", "Chat Ban", "Ranked Ban", "Permanente/HWID"])
            notas = st.text_input("Link de Tracker / VODs / Notas adicionales")

        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        col_espacio, col_boton = st.columns([1, 1])
        with col_boton:
            submitted = st.form_submit_button("🚀 Enviar Postulación", use_container_width=True)

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
                    ws_bl = obtener_hoja_lista_negra(workbook)
                    registros_bl = ws_bl.get_all_values() if ws_bl else []
                    esta_vetado = False
                    
                    for fila_bl in registros_bl[1:]:
                        if len(fila_bl) > 1:
                            id_vetado = fila_bl[0].strip().lower()
                            contacto_vetado = fila_bl[1].strip().lower()
                            
                            if (id_vetado and id_vetado == player_id.strip().lower()) or \
                               (contacto_vetado and (contacto_vetado == contacto_formateado.lower() or contacto_vetado == contacto_valor.strip().lower())):
                                esta_vetado = True
                                break
                    
                    if esta_vetado:
                        st.error("❌ Tu postulación ha sido rechazada automáticamente. No cumples con los requisitos de ingreso para Scarlet Esports.")
                    else:
                        ws = workbook.worksheet(division)
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
                            elif division == "CS":
                                nueva_fila = [player_id, contacto_formateado, str(edad), rango_actual, rol, peak_elo, baneos, "Tryout", notas]
                            elif division == "Fighting":
                                nueva_fila = [player_id, contacto_formateado, str(edad), juego_esp, personaje, rango_actual, peak_elo, baneos, "Tryout", notas]
                            
                            ws.append_row(nueva_fila)
                            st.success(f"🎉 ¡Postulación a {division} enviada con éxito!")
                            
                except Exception as e:
                    st.error(f"Hubo un error al registrar tus datos: {e}")

with tab_dashboard:
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if "del_count" not in st.session_state:
        st.session_state["del_count"] = 0
    if "wipe_count" not in st.session_state:
        st.session_state["wipe_count"] = 0
    if "bl_count" not in st.session_state:
        st.session_state["bl_count"] = 0
    if "unbl_count" not in st.session_state:
        st.session_state["unbl_count"] = 0

    admin_password = obtener_password_admin()

    if not st.session_state["autenticado"]:
        st.subheader("🔒 Acceso Restringido")
        with st.form("login_gerencia"):
            clave_acceso = st.text_input("Ingrese la clave para ver el panel gerencial", type="password")
            btn_login = st.form_submit_button("🔓 Iniciar Sesión")
            
            if btn_login:
                if clave_acceso == admin_password:
                    st.session_state["autenticado"] = True
                    st.success("✅ Acceso concedido.")
                    st.rerun()
                else:
                    st.error("❌ Contraseña incorrecta. Acceso denegado.")
                    
    else:
        count = st_autorefresh(interval=10000, limit=None, key="scarlet_autorefresh")

        st.title("🔥 PANEL GERENCIAL SCARLET ESPORTS")
        
        if st.sidebar.button("🚪 Cerrar Sesión Admin"):
            st.session_state["autenticado"] = False
            st.rerun()

        div_dashboard = st.sidebar.selectbox("📊 Analizar División", ["Valorant", "Overwatch", "CS", "Valorant Femenino", "Fighting"])
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
            except Exception:
                return pd.DataFrame()

        df = load_data_from_sheet(div_dashboard)

        with st.sidebar.expander("🔑 Cambiar Contraseña Gerencial"):
            with st.form("form_cambio_pass", clear_on_submit=True):
                pwd_actual = st.text_input("Contraseña Actual:", type="password")
                pwd_nueva = st.text_input("Nueva Contraseña:", type="password")
                pwd_conf = st.text_input("Confirmar Nueva Contraseña:", type="password")
                
                btn_cambiar_pass = st.form_submit_button("🔑 Guardar Nueva Contraseña")
                
                if btn_cambiar_pass:
                    if pwd_actual != admin_password:
                        st.error("❌ La contraseña actual es incorrecta.")
                    elif not pwd_nueva.strip():
                        st.error("⚠️ La nueva contraseña no puede estar vacía.")
                    elif pwd_nueva != pwd_conf:
                        st.error("⚠️ Las nuevas contraseñas no coinciden.")
                    else:
                        if actualizar_password_admin(pwd_nueva.strip()):
                            st.success("✅ ¡Contraseña actualizada exitosamente!")
                            admin_password = pwd_nueva.strip() 
                        else:
                            st.error("❌ Error al guardar la nueva contraseña en Google Sheets.")

        with st.sidebar.expander("🚫 Vetar / Mover a Lista Negra"):
            if not df.empty:
                col_id_name = df.columns[0]
                col_contact_name = df.columns[1] if len(df.columns) > 1 else col_id_name
                tipo_id_actual = ETIQUETAS_ID.get(div_dashboard, "ID Jugador")
                
                opciones_postulantes_bl = {}
                for idx, row in df.iterrows():
                    val_id = row[col_id_name]
                    val_contacto = row[col_contact_name]
                    etiqueta = f"🎮 {tipo_id_actual}: {val_id} ({val_contacto})"
                    opciones_postulantes_bl[etiqueta] = (idx + 2, val_id, val_contacto)
                
                postulante_bl_sel = st.selectbox("Selecciona al postulante a vetar", list(opciones_postulantes_bl.keys()), key="sb_vetar")
                motivo_bl = st.text_input("Motivo del veto (Opcional):", placeholder="Ej: Comportamiento tóxico / Incumplimiento")
                
                key_bl = f"pwd_bl_{st.session_state['bl_count']}"
                pwd_bl = st.text_input("Confirma contraseña gerencial:", type="password", key=key_bl)
                
                if st.button("🚫 Vetar y Enviar a Lista Negra"):
                    if pwd_bl == admin_password:
                        try:
                            fila_a_borrar, val_id, val_contacto = opciones_postulantes_bl[postulante_bl_sel]
                            
                            ws_bl = obtener_hoja_lista_negra(workbook)
                            fecha_hoy = datetime.date.today().strftime("%Y-%m-%d")
                            ws_bl.append_row([val_id, val_contacto, fecha_hoy, motivo_bl if motivo_bl.strip() else "Sin motivo especificado", div_dashboard])
                            
                            ws_del = workbook.worksheet(div_dashboard)
                            ws_del.delete_rows(fila_a_borrar)
                            
                            st.cache_data.clear()
                            st.session_state["bl_count"] += 1
                            
                            st.sidebar.success(f"✅ Postulante vetado con éxito y añadido a la Lista Negra.")
                            st.rerun()
                        except Exception as e:
                            st.sidebar.error(f"❌ Error al vetar postulante: {e}")
                    else:
                        st.sidebar.error("❌ Contraseña incorrecta.")
            else:
                st.info("No hay postulantes registrados en esta división.")

        with st.sidebar.expander("🟢 Desvetar / Quitar de Lista Negra"):
            df_bl_data = load_data_from_sheet("Lista Negra")
            if not df_bl_data.empty:
                opciones_desvetar = {}
                for idx, row in df_bl_data.iterrows():
                    val_id = row[df_bl_data.columns[0]]
                    val_contacto = row[df_bl_data.columns[1]] if len(df_bl_data.columns) > 1 else ""
                    div_orig = row[df_bl_data.columns[4]] if len(df_bl_data.columns) > 4 else "Desconocida"
                    etiqueta = f"🎮 {val_id} ({val_contacto}) - [{div_orig}]"
                    opciones_desvetar[etiqueta] = idx + 2
                
                player_to_unvet = st.selectbox("Selecciona jugador a desvetar", list(opciones_desvetar.keys()), key="sb_desvetar")
                
                key_unbl = f"pwd_unbl_{st.session_state['unbl_count']}"
                pwd_unbl = st.text_input("Confirma contraseña gerencial para desvetar:", type="password", key=key_unbl)
                
                if st.button("🟢 Desvetar y Permitir Postulaciones"):
                    if pwd_unbl == admin_password:
                        try:
                            fila_a_borrar_bl = opciones_desvetar[player_to_unvet]
                            ws_bl_del = obtener_hoja_lista_negra(workbook)
                            ws_bl_del.delete_rows(fila_a_borrar_bl)
                            
                            st.cache_data.clear()
                            st.session_state["unbl_count"] += 1
                            
                            st.sidebar.success("✅ Jugador retirado de la Lista Negra con éxito. Ahora puede volver a postularse.")
                            st.rerun()
                        except Exception as e:
                            st.sidebar.error(f"❌ Error al desvetar jugador: {e}")
                    else:
                        st.sidebar.error("❌ Contraseña incorrecta.")
            else:
                st.info("No hay jugadores actualmente en la Lista Negra.")

        with st.sidebar.expander("👤 Borrar Postulante (Sin Vetar)"):
            if not df.empty:
                col_id_name = df.columns[0]
                col_contact_name = df.columns[1] if len(df.columns) > 1 else col_id_name
                tipo_id_actual = ETIQUETAS_ID.get(div_dashboard, "ID Jugador")
                
                opciones_postulantes = {}
                for idx, row in df.iterrows():
                    val_id = row[col_id_name]
                    val_contacto = row[col_contact_name]
                    etiqueta = f"🎮 {tipo_id_actual}: {val_id} ({val_contacto})"
                    opciones_postulantes[etiqueta] = idx + 2
                
                postulante_sel = st.selectbox("Selecciona al postulante a eliminar", list(opciones_postulantes.keys()))
                
                key_del = f"pwd_del_indiv_{st.session_state['del_count']}"
                pwd_del_indiv = st.text_input("Confirma contraseña para eliminar:", type="password", key=key_del)
                
                if st.button("❌ Eliminar Postulante Seleccionado"):
                    if pwd_del_indiv == admin_password:
                        try:
                            fila_a_borrar = opciones_postulantes[postulante_sel]
                            ws_del = workbook.worksheet(div_dashboard)
                            ws_del.delete_rows(fila_a_borrar)
                            st.cache_data.clear()
                            
                            st.session_state["del_count"] += 1
                            st.sidebar.success(f"✅ Postulante eliminado con éxito.")
                            st.rerun()
                        except Exception as e:
                            st.sidebar.error(f"❌ Error al eliminar postulante: {e}")
                    else:
                        st.sidebar.error("❌ Contraseña incorrecta. Borrado cancelado.")
            else:
                st.info("No hay postulantes registrados en esta división.")

        with st.sidebar.expander("🚨 Zona de Peligro (Limpiar DB)"):
            st.warning(f"⚠️ Estás a punto de BORRAR TODOS los postulantes de: **{div_dashboard}**")
            st.caption("Esta acción no afectará a las otras divisiones y conservará los encabezados.")
            
            key_wipe = f"confirm_pwd_wipe_{st.session_state['wipe_count']}"
            pwd_confirm = st.text_input("Confirma contraseña gerencial para borrar toda la DB:", type="password", key=key_wipe)
            
            if st.button(f"🗑️ Limpiar DB de {div_dashboard}", type="primary"):
                if pwd_confirm == admin_password:
                    try:
                        ws_clean = workbook.worksheet(div_dashboard)
                        ws_clean.batch_clear(["A2:Z1000"])
                        st.cache_data.clear()
                        
                        st.session_state["wipe_count"] += 1
                        st.sidebar.success(f"✅ Base de datos de {div_dashboard} limpiada correctamente.")
                        st.rerun()
                    except Exception as e:
                        st.sidebar.error(f"❌ Error al intentar borrar: {e}")
                else:
                    st.sidebar.error("❌ Contraseña incorrecta. Borrado cancelado.")

        st.sidebar.markdown("---")

        subtab_general, subtab_estado = st.tabs(["📊 Visión General", "📝 Modificar Estado"])

        with subtab_general:
            if df.empty:
                st.warning(f"⚠️ Aún no hay datos de postulantes para la división {div_dashboard}.")
            else:
                df.columns = [str(c).strip() for c in df.columns]
                
                col_estado = next((c for c in df.columns if 'estado' in c.lower()), None)
                if not col_estado:
                    df['Estado'] = 'Tryout'
                    col_estado = 'Estado'

                col_contacto = next((c for c in df.columns if 'contacto' in c.lower() or 'discord' in c.lower()), df.columns[1])
                
                # --- NUEVOS CÁLCULOS DE MÉTRICAS ---
                total_postulantes = len(df[df[col_contacto] != ''])
                tryouts_activos = len(df[df[col_estado].astype(str).str.strip().str.lower() == 'tryout']) 
                aceptados = len(df[df[col_estado].astype(str).str.strip().str.lower() == 'aceptado']) 
                rechazados = len(df[df[col_estado].astype(str).str.strip().str.lower() == 'rechazado'])
                
                # Extraer la cuenta de la hoja global de Lista Negra
                df_bl_metric = load_data_from_sheet("Lista Negra")
                en_lista_negra = len(df_bl_metric) if not df_bl_metric.empty else 0

                col_baneos = next((c for c in df.columns if 'bano' in c.lower() or 'baneo' in c.lower() or 'historial' in c.lower()), None)
                baneos_alerta = len(df[df[col_baneos].astype(str).str.strip().isin(['Chat Ban', 'Ranked Ban', 'Permanente/HWID'])]) if col_baneos else 0

                # --- FILA 1 DE MÉTRICAS ---
                col1, col2, col3 = st.columns(3)
                col1.metric("Postulantes Totales", total_postulantes)
                col2.metric("Pruebas Activas", tryouts_activos, delta="En proceso")
                col3.metric("Plantel Aceptado", aceptados)
                
                st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
                
                # --- FILA 2 DE MÉTRICAS ---
                col4, col5, col6 = st.columns(3)
                col4.metric("Postulantes Rechazados", rechazados)
                col5.metric("En Lista Negra (Total)", en_lista_negra)
                col6.metric("Alertas de Baneos", baneos_alerta, delta_color="inverse" if baneos_alerta > 0 else "normal")

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

            st.markdown("---")
            with st.expander("👀 Ver Registro General de Jugadores Vetados (Lista Negra)"):
                df_bl = load_data_from_sheet("Lista Negra")
                if not df_bl.empty:
                    st.dataframe(df_bl, use_container_width=True)
                else:
                    st.info("Actualmente no hay jugadores vetados en la Lista Negra.")

        with subtab_estado:
            st.subheader(f"📝 Modificar Estado en {div_dashboard}")
            
            if not df.empty:
                col_estado_mod = next((c for c in df.columns if 'estado' in c.lower()), None)
                if not col_estado_mod:
                    col_estado_mod = df.columns[-2]
                
                col_id_name_mod = df.columns[0]
                
                opciones_estado = {}
                for idx, row in df.iterrows():
                    val_id = row[col_id_name_mod]
                    estado_actual = str(row[col_estado_mod]).strip() if pd.notna(row[col_estado_mod]) else "Desconocido"
                    etiqueta = f"🎮 {val_id} | Estado: {estado_actual}"
                    opciones_estado[etiqueta] = (idx + 2, estado_actual)
                
                postulante_sel_estado = st.selectbox("Selecciona al postulante", list(opciones_estado.keys()), key="sb_modificar_estado_tab")
                
                estado_previo = opciones_estado[postulante_sel_estado][1]
                lista_estados = ["Tryout", "Aceptado", "Rechazado", "Vetado"]
                
                index_defecto = lista_estados.index(estado_previo.capitalize()) if estado_previo.capitalize() in lista_estados else 0
                nuevo_estado = st.selectbox("Nuevo Estado", lista_estados, index=index_defecto)
                
                if st.button("💾 Guardar Nuevo Estado", use_container_width=True):
                    try:
                        fila_a_modificar = opciones_estado[postulante_sel_estado][0]
                        col_idx = df.columns.tolist().index(col_estado_mod) + 1
                        
                        ws_estado = workbook.worksheet(div_dashboard)
                        ws_estado.update_cell(fila_a_modificar, col_idx, nuevo_estado)
                        
                        st.cache_data.clear()
                        
                        st.success(f"✅ Estado actualizado a '{nuevo_estado}' con éxito.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error al actualizar el estado: {e}")
            else:
                st.info("No hay postulantes registrados en esta división.")
