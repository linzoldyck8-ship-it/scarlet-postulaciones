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
    try:
        tabla_nombre = limpiar_nombre_tabla(division)
        if tabla_nombre not in TABLAS_PERMITIDAS:
            return jsonify({'error': f'División no válida: {division}'}), 400
        if not supabase:
            return jsonify({'error': 'Base de datos no conectada'}), 500
        
        data = request.get_json() or {}
        player_id = str(data.get('player_id', '')).strip()
        contacto = str(data.get('contacto', '')).strip()

        if not player_id or not contacto:
            return jsonify({'error': 'Faltan campos obligatorios (ID o Contacto)'}), 400

        # Verificar lista negra
        try:
            res_bl = supabase.table('lista_negra').select('*').execute()
            for fila in (res_bl.data or []):
                if str(fila.get('id_jugador', '')).strip().lower() == player_id.lower() or \
                   str(fila.get('contacto', '')).strip().lower() == contacto.lower():
                    return jsonify({'error': 'Tu postulación ha sido rechazada automáticamente por políticas del club.'}), 400
        except Exception as e:
            print("Aviso lista negra:", e)

        # Verificar duplicados
        try:
            res_exist = supabase.table(tabla_nombre).select('*').execute()
            for fila in (res_exist.data or []):
                if str(fila.get('player_id', '')).strip().lower() == player_id.lower() or \
                   str(fila.get('contacto', '')).strip().lower() == contacto.lower():
                    return jsonify({'error': 'Ya existe una postulación registrada con este ID o Contacto.'}), 400
        except Exception as e:
            print("Aviso duplicados:", e)

        nueva_data = {
            "player_id": player_id,
            "contacto": contacto,
            "edad": str(data.get('edad', '18')),
            "rango_actual": str(data.get('rango_actual', '')),
            "rol": str(data.get('rol', 'Flex')),
            "peak_elo": str(data.get('peak_elo', '')),
            "baneos": str(data.get('baneos', 'Limpio')),
            "estado": "Tryout",
            "notas": str(data.get('notas', '')),
            "motivo_rechazo": ""
        }
        
        if tabla_nombre == "fighting":
            nueva_data["juego_especifico"] = str(data.get('juego_especifico', ''))
            nueva_data["personaje"] = str(data.get('personaje', ''))

        supabase.table(tabla_nombre).insert(nueva_data).execute()
        return jsonify({'status': 'success', 'message': 'Postulación enviada con éxito'})
        
    except Exception as e:
        print("=== ERROR CRÍTICO EN POSTULAR ===")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

# --- RUTAS DE ADMINISTRACIÓN ---

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

@app.route('/api/admin/eliminar_postulante', methods=['POST'])
@admin_required
def admin_eliminar_postulante():
    """Elimina permanentemente a un postulante de una división"""
    data = request.get_json() or {}
    division = data.get('division')
    row_id = data.get('id')
    tabla = limpiar_nombre_tabla(division)
    
    if tabla not in TABLAS_PERMITIDAS:
        return jsonify({'error': 'División no válida'}), 400
        
    try:
        supabase.table(tabla).delete().eq('id', row_id).execute()
        return jsonify({'status': 'success', 'message': 'Postulante eliminado correctamente'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/agregar_blacklist', methods=['POST'])
@admin_required
def admin_agregar_blacklist():
    """Agrega un postulante a la lista negra y lo elimina de la división activa"""
    data = request.get_json() or {}
    player_id = data.get('player_id', '').strip()
    contacto = data.get('contacto', '').strip()
    motivo = data.get('motivo', 'Agregado desde panel gerencial').strip()
    division = data.get('division')
    row_id = data.get('id')
    
    if not player_id and not contacto:
        return jsonify({'error': 'Debe proporcionar Player ID o Contacto'}), 400
        
    try:
        # 1. Registrar en la lista negra
        supabase.table('lista_negra').insert({
            'id_jugador': player_id,
            'contacto': contacto,
            'motivo': motivo
        }).execute()

        # 2. Si venía de una tabla activa, borrarlo de esa división
        if division and row_id:
            tabla = limpiar_nombre_tabla(division)
            if tabla in TABLAS_PERMITIDAS:
                supabase.table(tabla).delete().eq('id', row_id).execute()

        return jsonify({'status': 'success', 'message': 'Jugador enviado a Lista Negra correctamente'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/obtener_blacklist', methods=['GET'])
@admin_required
def admin_obtener_blacklist():
    """Obtiene la lista de jugadores baneados"""
    if not supabase:
        return jsonify([]), 500
    try:
        res = supabase.table('lista_negra').select('*').execute()
        return jsonify(res.data if res.data else [])
    except Exception as e:
        return jsonify([]), 500

@app.route('/api/admin/eliminar_blacklist', methods=['POST'])
@admin_required
def admin_eliminar_blacklist():
    """Desbloquea a un jugador quitándolo de la lista negra"""
    data = request.get_json() or {}
    row_id = data.get('id')
    try:
        supabase.table('lista_negra').delete().eq('id', row_id).execute()
        return jsonify({'status': 'success', 'message': 'Jugador quitado de la Lista Negra'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ... (código previo de tus rutas existentes) ...

@app.route('/api/admin/vaciar/<division>', methods=['POST'])
def vaciar_division(division):
    data = request.get_json() or {}
    password = data.get('password')
    
    if password != "cazuela":  # Contraseña del panel
        return jsonify({'error': 'Contraseña de administrador incorrecta'}), 401
        
    tablas_validas = ["valorant", "overwatch", "cs", "valorant_femenino", "fighting"]
    if division not in tablas_validas:
        return jsonify({'error': 'División no válida'}), 400
        
    try:
        supabase.table(division).delete().neq('id', -1).execute()
        return jsonify({'message': f'La base de datos de {division.upper()} ha sido vaciada por completo.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
