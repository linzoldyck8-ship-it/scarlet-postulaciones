import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from functools import wraps
from supabase import create_client, Client
import re

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'clave_secreta_scarlet_esports')

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print("Error al conectar con Supabase:", e)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return jsonify({'error': 'No autorizado'}), 401
        return f(*args, **kwargs)
    return decorated_function

def limpiar_nombre_tabla(nombre):
    return nombre.lower().replace(" ", "_")

def es_correo_valido(correo):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', correo) is not None

# --- RUTAS DE VISTAS ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/postulaciones')
def postulaciones():
    return render_template('postulaciones.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    # Obtener contraseña desde Supabase o usar por defecto 'cazuela'
    admin_password = 'cazuela'
    if supabase:
        try:
            res = supabase.table("configuracion").select("valor").eq("clave", "Password").execute()
            if res.data and res.data[0]["valor"]:
                admin_password = res.data[0]["valor"].strip()
        except Exception:
            pass

    if request.method == 'POST':
        password = request.form.get('password')
        if password == admin_password:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        return render_template('admin_login.html', error='Contraseña incorrecta')
    
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))
        
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

# --- API DE POSTULACIONES Y CONFIGURACIÓN ---
TABLAS_PERMITIDAS = ['valorant', 'overwatch', 'cs', 'valorant_femenino', 'fighting', 'configuracion', 'lista_negra']

@app.route('/api/configuracion', methods=['GET'])
def get_config():
    if not supabase:
        return jsonify({})
    try:
        res = supabase.table('configuracion').select('*').execute()
        return jsonify(res.data if res.data else [])
    except Exception as e:
        return jsonify([]), 500

@app.route('/api/configuracion', methods=['POST'])
@admin_required
def update_config():
    data = request.get_json()
    try:
        clave = data.get('clave')
        valor = data.get('valor')
        res = supabase.table('configuracion').select('*').eq('clave', clave).execute()
        if res.data:
            supabase.table('configuracion').update({'valor': valor}).eq('clave', clave).execute()
        else:
            supabase.table('configuracion').insert({'clave': clave, 'valor': valor}).execute()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/postular/<division>', methods=['POST'])
def postular(division):
    if limpiar_nombre_tabla(division) not in TABLAS_PERMITIDAS:
        return jsonify({'error': 'División no válida'}), 400
    if not supabase:
        return jsonify({'error': 'Base de datos no conectada'}), 500
    
    try:
        data = request.get_json()
        tabla_nombre = limpiar_nombre_tabla(division)
        player_id = data.get('player_id', '').strip()
        contacto = data.get('contacto', '').strip()

        # Verificar lista negra
        res_bl = supabase.table('lista_negra').select('*').execute()
        for fila in (res_bl.data or []):
            if str(fila.get('id_jugador', '')).strip().lower() == player_id.lower() or \
               str(fila.get('contacto', '')).strip().lower() == contacto.lower():
                return jsonify({'error': 'Tu postulación ha sido rechazada automáticamente por políticas del club.'}), 400

        # Verificar duplicados
        res_exist = supabase.table(tabla_nombre).select('*').execute()
        for fila in (res_exist.data or []):
            if str(fila.get('player_id', '')).strip().lower() == player_id.lower() or \
               str(fila.get('contacto', '')).strip().lower() == contacto.lower():
                return jsonify({'error': 'Ya existe una postulación registrada con este ID o Contacto.'}), 400

        nueva_data = {
            "player_id": player_id,
            "contacto": contacto,
            "edad": str(data.get('edad')),
            "rango_actual": data.get('rango_actual'),
            "rol": data.get('rol', 'Fighting'),
            "peak_elo": data.get('peak_elo'),
            "baneos": data.get('baneos'),
            "estado": "Tryout",
            "notas": data.get('notas', ''),
            "motivo_rechazo": ""
        }
        if division == "Fighting":
            nueva_data["juego_especifico"] = data.get('juego_especifico', '')
            nueva_data["personaje"] = data.get('personaje', '')

        supabase.table(tabla_nombre).insert(nueva_data).execute()
        return jsonify({'status': 'success', 'message': 'Postulación enviada con éxito'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
