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
    # ... (toda la lógica que ya tenías para postular) ...
    pass


# ==========================================
# PEGA AQUÍ LAS NUEVAS RUTAS DE ADMINISTRACIÓN
# ==========================================

@app.route('/api/admin/obtener/<division>', methods=['GET'])
@admin_required
def admin_obtener_division(division):
    tabla = limpiar_nombre_tabla(division)
    if not supabase:
        return jsonify([]), 500
    try:
        res = supabase.table(tabla).select('*').execute()
        return jsonify(res.data if res.data else [])
    except Exception as e:
        return jsonify([]), 500

@app.route('/api/admin/actualizar_estado', methods=['POST'])
@admin_required
def admin_actualizar_estado():
    data = request.get_json()
    division = data.get('division')
    row_id = data.get('id')
    nuevo_estado = data.get('estado')
    tabla = limpiar_nombre_tabla(division)
    
    try:
        supabase.table(tabla).update({'estado': nuevo_estado}).eq('id', row_id).execute()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
