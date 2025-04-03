from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import psycopg2
from psycopg2 import IntegrityError
from datetime import datetime
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'mi_llave_secreta')  # Clave para flash messages

# Configuración de la base de datos
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://negocio_54gh_user:lwclY7Am6oVOImETtdFwjbSRvRFXO6yr@dpg-cv8a1da3esus73ch8mrg-a.oregon-postgres.render.com/negocio_54gh')

# Horarios disponibles
HORARIOS_DISPONIBLES = [
    "09:00", "09:40", "10:20", "11:00", "11:40", "12:20",
    "13:00", "13:40", "17:00", "17:40", "18:20", "19:00", "19:40",
    "20:20", "21:00" ,"21:40" , "22:20"
]

def get_db_connection():
    # Conexión con SSL para Render
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn

@app.route('/')
def index():
    return render_template('index.html')

# ------------------- CLIENTES -------------------
@app.route('/clientes')
def clientes():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM clientes ORDER BY nombre;')
            clientes = cur.fetchall()
    return render_template('clientes.html', clientes=clientes)

@app.route('/clientes/agregar', methods=['POST'])
def agregar_cliente():
    nombre = request.form['nombre']
    dni = request.form['dni']
    telefono = request.form['telefono']
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'INSERT INTO clientes (nombre, dni, telefono) VALUES (%s, %s, %s)',
                    (nombre, dni, telefono)
                )
                conn.commit()
        flash("Cliente agregado correctamente", "success")
    except IntegrityError:
        flash("El DNI ya existe en el sistema", "error")
    except Exception as e:
        flash(f"Error al agregar cliente: {str(e)}", "error")
    return redirect(url_for('clientes'))

@app.route('/clientes/editar/<int:cliente_id>', methods=['GET', 'POST'])
def editar_cliente(cliente_id):
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'POST':
        nombre = request.form['nombre']
        dni = request.form['dni']
        telefono = request.form['telefono']
        try:
            cur.execute(
                'UPDATE clientes SET nombre = %s, dni = %s, telefono = %s WHERE id = %s',
                (nombre, dni, telefono, cliente_id)
            )
            conn.commit()
            flash("Cliente actualizado correctamente", "success")
        except Exception as e:
            conn.rollback()
            flash(f"Error al actualizar cliente: {str(e)}", "error")
        finally:
            cur.close()
            conn.close()
        return redirect(url_for('clientes'))
    else:
        cur.execute('SELECT * FROM clientes WHERE id = %s', (cliente_id,))
        cliente = cur.fetchone()
        cur.close()
        conn.close()
        if cliente is None:
            flash("Cliente no encontrado", "error")
            return redirect(url_for('clientes'))
        return render_template('editar_cliente.html', cliente=cliente)

@app.route('/clientes/eliminar/<int:cliente_id>')
def eliminar_cliente(cliente_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('DELETE FROM clientes WHERE id = %s', (cliente_id,))
        conn.commit()
        flash("Cliente eliminado correctamente", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error al eliminar cliente: {str(e)}", "error")
    finally:
        cur.close()
        conn.close()
    return redirect(url_for('clientes'))

# ------------------- BARBEROS -------------------
@app.route('/barberos')
def barberos():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM barberos ORDER BY nombre;')
            barberos = cur.fetchall()
    return render_template('barberos.html', barberos=barberos)

@app.route('/barberos/agregar', methods=['POST'])
def agregar_barbero():
    nombre = request.form['nombre']
    dni = request.form['dni']
    telefono = request.form['telefono']
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'INSERT INTO barberos (nombre, dni, telefono) VALUES (%s, %s, %s)',
                    (nombre, dni, telefono)
                )
                conn.commit()
        flash("Barbero agregado correctamente", "success")
    except IntegrityError:
        flash("El DNI ya existe en el sistema", "error")
    except Exception as e:
        flash(f"Error al agregar barbero: {str(e)}", "error")
    return redirect(url_for('barberos'))

@app.route('/barberos/editar/<int:barbero_id>', methods=['GET', 'POST'])
def editar_barbero(barbero_id):
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'POST':
        nombre = request.form['nombre']
        dni = request.form['dni']
        telefono = request.form['telefono']
        try:
            cur.execute(
                'UPDATE barberos SET nombre = %s, dni = %s, telefono = %s WHERE id = %s',
                (nombre, dni, telefono, barbero_id)
            )
            conn.commit()
            flash("Barbero actualizado correctamente", "success")
        except Exception as e:
            conn.rollback()
            flash(f"Error al actualizar barbero: {str(e)}", "error")
        finally:
            cur.close()
            conn.close()
        return redirect(url_for('barberos'))
    else:
        cur.execute('SELECT * FROM barberos WHERE id = %s', (barbero_id,))
        barbero = cur.fetchone()
        cur.close()
        conn.close()
        if barbero is None:
            flash("Barbero no encontrado", "error")
            return redirect(url_for('barberos'))
        return render_template('editar_barbero.html', barbero=barbero)

@app.route('/barberos/eliminar/<int:barbero_id>')
def eliminar_barbero(barbero_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('DELETE FROM barberos WHERE id = %s', (barbero_id,))
        conn.commit()
        flash("Barbero eliminado correctamente", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error al eliminar barbero: {str(e)}", "error")
    finally:
        cur.close()
        conn.close()
    return redirect(url_for('barberos'))

# ------------------- TURNOS -------------------
@app.route('/turnos')
def turnos():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Obtener barberos
            cur.execute('SELECT id, nombre FROM barberos ORDER BY nombre;')
            barberos = cur.fetchall()
            # Obtener clientes para el buscador
            cur.execute('SELECT id, nombre, dni, telefono FROM clientes ORDER BY nombre;')
            clientes = cur.fetchall()
    return render_template('turnos.html', 
                           barberos=barberos, 
                           clientes=clientes, 
                           horarios=[],  
                           fecha_actual=datetime.now().strftime('%Y-%m-%d'))

@app.route('/turnos/agregar', methods=['POST'])
def agregar_turno():
    fecha = request.form['fecha']
    hora = request.form['hora']
    cliente_id = request.form['cliente_id']
    barbero_id = request.form['barbero_id']
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Verificar si ya existe un turno para ese barbero en esa fecha y hora
                cur.execute('''
                    SELECT id FROM turnos 
                    WHERE fecha = %s AND hora = %s AND barbero_id = %s
                ''', (fecha, hora, barbero_id))
                if cur.fetchone() is not None:
                    raise Exception('El barbero ya tiene un turno asignado en ese horario')
                # Insertar el turno (monto se dejará en NULL o 0 según la definición)
                cur.execute(
                    'INSERT INTO turnos (fecha, hora, cliente_id, barbero_id) VALUES (%s, %s, %s, %s)',
                    (fecha, hora, cliente_id, barbero_id)
                )
                conn.commit()
        flash("Turno agregado correctamente", "success")
    except Exception as e:
        flash(f"Error al agregar turno: {str(e)}", "error")
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT id, nombre FROM barberos ORDER BY nombre;')
                barberos = cur.fetchall()
                cur.execute('SELECT id, nombre FROM clientes ORDER BY nombre;')
                clientes = cur.fetchall()
        return render_template('turnos.html', 
                               barberos=barberos, 
                               clientes=clientes, 
                               horarios=HORARIOS_DISPONIBLES,
                               fecha_actual=datetime.now().strftime('%Y-%m-%d'))
    return redirect(url_for('turnos'))

@app.route('/get_horarios_disponibles')
def get_horarios_disponibles():
    fecha = request.args.get('fecha')
    barbero_id = request.args.get('barbero_id')
    if not fecha or not barbero_id:
        return jsonify({'horarios': []})
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    SELECT hora FROM turnos 
                    WHERE fecha = %s AND barbero_id = %s
                ''', (fecha, barbero_id))
                horarios_ocupados = [hora[0] for hora in cur.fetchall()]
                horarios_disponibles = [h for h in HORARIOS_DISPONIBLES if h not in horarios_ocupados]
                return jsonify({'horarios': horarios_disponibles})
    except Exception as e:
        return jsonify({'horarios': []}), 500

@app.route('/turnos/hoy')
def turnos_hoy():
    # Obtener fecha del filtro o usar la fecha actual
    fecha_query = request.args.get('fecha') or datetime.now().strftime('%Y-%m-%d')
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('''
                SELECT t.id, t.hora, c.nombre as cliente_nombre, b.nombre as barbero_nombre, t.completado
                FROM turnos t
                JOIN clientes c ON t.cliente_id = c.id
                JOIN barberos b ON t.barbero_id = b.id
                WHERE t.fecha = %s
                ORDER BY t.hora;
            ''', (fecha_query,))
            turnos = cur.fetchall()
    return render_template('turnos_hoy.html', turnos=turnos, hoy=fecha_query)

@app.route('/turnos/eliminar/<int:turno_id>')
def eliminar_turno(turno_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('DELETE FROM turnos WHERE id = %s', (turno_id,))
        conn.commit()
        flash("Turno eliminado correctamente", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Error al eliminar turno: {str(e)}", "error")
    finally:
        cur.close()
        conn.close()
    return redirect(url_for('turnos_hoy'))

@app.route('/dashboard', methods=['GET'])
def dashboard():
    # Filtros de fecha (por defecto, hoy)
    start_date = request.args.get('start_date') or datetime.now().strftime('%Y-%m-%d')
    end_date = request.args.get('end_date') or datetime.now().strftime('%Y-%m-%d')

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Top 5 clientes
            cur.execute("""
                SELECT id, nombre, cortes
                FROM clientes
                ORDER BY cortes DESC
                LIMIT 5;
            """)
            top_clients = cur.fetchall()

            # Total ganado por método de pago
            cur.execute("""
                SELECT payment_method, SUM(monto) AS total_ganado
                FROM turnos
                WHERE completado = TRUE
                  AND fecha >= %s AND fecha <= %s
                GROUP BY payment_method;
            """, (start_date, end_date))
            payment_data = cur.fetchall()

            # Total de 
            cur.execute("""
                SELECT SUM(monto)
                FROM egresos_cristian
                WHERE fecha >= %s AND fecha <= %s;
            """, (start_date, end_date))
            total_egresos = cur.fetchone()[0] or 0

    # Calcular total ganado
    total_ganado = sum(row[1] or 0 for row in payment_data)
    neto = total_ganado - total_egresos

    return render_template('dashboard.html',
                           top_clients=top_clients,
                           payment_data=payment_data,
                           start_date=start_date,
                           end_date=end_date,
                           total_ganado=total_ganado,
                           total_egresos=total_egresos,
                           neto=neto)




@app.route('/egresos/eliminar/<int:egreso_id>')
def eliminar_egreso(egreso_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('DELETE FROM egresos_cristian WHERE id = %s', (egreso_id,))
                conn.commit()
        flash("Egreso eliminado correctamente", "success")
    except Exception as e:
        flash(f"Error al eliminar egreso: {str(e)}", "error")
    return redirect(url_for('egresos'))



@app.route('/egresos', methods=['GET', 'POST'])
def egresos():
    hoy = datetime.now().strftime('%Y-%m-%d')

    if request.method == 'POST':
        fecha = request.form['fecha']
        monto = request.form['monto']
        descripcion = request.form['descripcion']
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        'INSERT INTO egresos_cristian (fecha, monto, descripcion) VALUES (%s, %s, %s)',
                        (fecha, monto, descripcion)
                    )
                    conn.commit()
            flash("Egreso registrado correctamente", "success")
        except Exception as e:
            flash(f"Error al registrar egreso: {str(e)}", "error")
        return redirect(url_for('egresos'))

    # Filtro de fechas
    desde = request.args.get('desde') or hoy
    hasta = request.args.get('hasta') or hoy

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, fecha, monto, descripcion
                FROM egresos_cristian
                WHERE fecha BETWEEN %s AND %s
                ORDER BY fecha DESC;
            """, (desde, hasta))
            egresos = cur.fetchall()

    return render_template('egresos.html', egresos=egresos, desde=desde, hasta=hasta, hoy=hoy)



@app.route('/turnos/completar/<int:turno_id>', methods=['POST'])
def completar_turno(turno_id):
    payment_method = request.form.get('payment_method')
    monto = request.form.get('monto')
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Obtener el cliente del turno
                cur.execute('SELECT cliente_id FROM turnos WHERE id = %s', (turno_id,))
                result = cur.fetchone()
                if result is None:
                    raise Exception("Turno no encontrado")
                cliente_id = result[0]
                # Actualizar el turno como completado, registrar el método de pago y el monto cobrado
                cur.execute(
                    'UPDATE turnos SET completado = TRUE, payment_method = %s, monto = %s WHERE id = %s',
                    (payment_method, monto, turno_id)
                )
                # Incrementar el contador de cortes del cliente
                cur.execute(
                    'UPDATE clientes SET cortes = cortes + 1 WHERE id = %s',
                    (cliente_id,)
                )
                conn.commit()
        flash("Turno marcado como completado", "success")
    except Exception as e:
        flash(f"Error al completar turno: {str(e)}", "error")
    return redirect(url_for('turnos_hoy'))

if __name__ == '__main__':
    app.run(debug=True)
