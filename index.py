from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui' # ¡Es importante cambiar esto!

# --- 1. CONEXIÓN A LA BASE DE DATOS ---
# Se actualizó el nombre de la base de datos a 'Bd_Automoviles'.
def connect_to_db():
    """Función para conectar a la base de datos MariaDB."""
    try:
        return pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='Bd_Automoviles', # CAMBIO CLAVE: Nombre de la nueva BD
            cursorclass=pymysql.cursors.DictCursor,
            ssl_disabled=True 
        )
    except pymysql.MySQLError as e:
        flash(f'Error de conexión a la base de datos: {e}', 'error')
        return None

# --- 2. RUTA PRINCIPAL ---
# La ruta principal ahora redirige a la página de clientes, que es más útil.
@app.route("/")
def index():
    return redirect(url_for('clientes'))

# --- 3. RUTAS PARA CLIENTES ---
# Se unificaron y renombraron todas las rutas relacionadas a 'pacientes' por 'clientes'.
@app.route('/clientes', methods=['GET', 'POST'])
def clientes():
    """Muestra la lista de clientes y maneja la creación de nuevos clientes."""
    conn = connect_to_db()
    if not conn:
        return render_template('clientes.html', clientes=[])

    # Maneja la creación de un nuevo cliente (método POST)
    if request.method == 'POST':
        try:
            # Obtenemos los datos del formulario con los nombres nuevos
            nif = request.form.get('NIF')
            nombre = request.form.get('nombre')
            direccion = request.form.get('direccion')
            telefono = request.form.get('telefono')

            with conn.cursor() as cur:
                # Consulta SQL actualizada para la tabla 'clientes'
                cur.execute(
                    "INSERT INTO clientes (NIF, nombre, direccion, telefono) VALUES (%s, %s, %s, %s)",
                    (nif, nombre, direccion, telefono)
                )
            conn.commit()
            flash('Cliente agregado correctamente.', 'success')
        except pymysql.MySQLError as e:
            flash(f'Error al agregar cliente: {e}', 'error')
        finally:
            conn.close()
        return redirect(url_for('clientes'))

    # Muestra la lista de clientes (método GET)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM clientes ORDER BY nombre")
            lista_clientes = cur.fetchall()
        return render_template('clientes.html', clientes=lista_clientes)
    except pymysql.MySQLError as e:
        flash(f'Error al obtener clientes: {e}', 'error')
        return render_template('clientes.html', clientes=[])
    finally:
        if conn:
            conn.close()

@app.route('/clientes/editar/<string:NIF>', methods=['GET', 'POST'])
def editar_cliente(NIF):
    """Muestra el formulario para editar un cliente y maneja la actualización."""
    conn = connect_to_db()
    if not conn:
        return redirect(url_for('clientes'))

    # Maneja la actualización del cliente (método POST)
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            direccion = request.form['direccion']
            telefono = request.form['telefono']

            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE clientes
                    SET nombre=%s, direccion=%s, telefono=%s
                    WHERE NIF=%s
                """, (nombre, direccion, telefono, NIF))
            conn.commit()
            flash('Cliente actualizado correctamente.', 'success')
        except pymysql.MySQLError as e:
            flash(f'Error al actualizar cliente: {e}', 'error')
        finally:
            conn.close()
        return redirect(url_for('clientes'))

    # Muestra el formulario con los datos del cliente a editar (método GET)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM clientes WHERE NIF = %s", (NIF,))
            cliente_data = cur.fetchone()
        if not cliente_data:
            flash('Cliente no encontrado.', 'warning')
            return redirect(url_for('clientes'))
        return render_template('editar_cliente.html', cliente=cliente_data)
    except pymysql.MySQLError as e:
        flash(f'Error al obtener datos del cliente: {e}', 'error')
        return redirect(url_for('clientes'))
    finally:
        if conn:
            conn.close()

@app.route('/clientes/eliminar/<string:NIF>', methods=['POST'])
def eliminar_cliente(NIF):
    """Maneja la eliminación de un cliente."""
    conn = connect_to_db()
    if not conn:
        return redirect(url_for('clientes'))
        
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM clientes WHERE NIF = %s", (NIF,))
        conn.commit()
        flash('Cliente eliminado correctamente.', 'success')
    except pymysql.MySQLError as e:
        # Manejo de error si el cliente tiene coches asociados
        if e.args[0] == 1451: # Código de error de restricción de clave foránea
             flash('No se puede eliminar el cliente porque tiene coches asociados.', 'error')
        else:
             flash(f'Error al eliminar cliente: {e}', 'error')
    finally:
        conn.close()
    return redirect(url_for('clientes'))


# --- 4. RUTAS PARA COCHES ---
# Se adaptaron las rutas de 'medicos' para 'coches'.
@app.route('/coches', methods=['GET', 'POST'])
def coches():
    """Muestra la lista de coches y maneja la creación de nuevos coches."""
    conn = connect_to_db()
    if not conn:
        return render_template('coches.html', coches=[], clientes=[])

    if request.method == 'POST':
        try:
            matricula = request.form['matricula']
            marca = request.form['marca']
            modelo = request.form['modelo']
            color = request.form['color']
            precio = request.form['precio']
            nif_cliente = request.form['NIF_cliente']

            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO coches (matricula, marca, modelo, color, precio, NIF_cliente) VALUES (%s, %s, %s, %s, %s, %s)",
                    (matricula, marca, modelo, color, precio, nif_cliente)
                )
            conn.commit()
            flash('Coche agregado correctamente.', 'success')
        except pymysql.MySQLError as e:
            flash(f'Error al agregar coche: {e}', 'error')
        finally:
            conn.close()
        return redirect(url_for('coches'))

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM coches ORDER BY marca, modelo")
            lista_coches = cur.fetchall()
            # Necesitamos la lista de clientes para el formulario
            cur.execute("SELECT NIF, nombre FROM clientes ORDER BY nombre")
            lista_clientes = cur.fetchall()
        return render_template('coches.html', coches=lista_coches, clientes=lista_clientes)
    except pymysql.MySQLError as e:
        flash(f'Error al obtener datos: {e}', 'error')
        return render_template('coches.html', coches=[], clientes=[])
    finally:
        if conn:
            conn.close()

@app.route('/coches/editar/<string:matricula>', methods=['GET', 'POST'])
def editar_coche(matricula):
    """Muestra el formulario para editar un coche y maneja la actualización."""
    conn = connect_to_db()
    if not conn:
        return redirect(url_for('coches'))

    if request.method == 'POST':
        try:
            marca = request.form['marca']
            modelo = request.form['modelo']
            color = request.form['color']
            precio = request.form['precio']
            nif_cliente = request.form['NIF_cliente']
            
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE coches
                    SET marca=%s, modelo=%s, color=%s, precio=%s, NIF_cliente=%s
                    WHERE matricula=%s
                """, (marca, modelo, color, precio, nif_cliente, matricula))
            conn.commit()
            flash('Coche actualizado correctamente.', 'success')
        except pymysql.MySQLError as e:
            flash(f'Error al actualizar coche: {e}', 'error')
        finally:
            conn.close()
        return redirect(url_for('coches'))
        
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM coches WHERE matricula = %s", (matricula,))
            coche_data = cur.fetchone()
            cur.execute("SELECT NIF, nombre FROM clientes ORDER BY nombre")
            lista_clientes = cur.fetchall()
        
        if not coche_data:
            flash('Coche no encontrado.', 'warning')
            return redirect(url_for('coches'))
            
        return render_template('editar_coche.html', coche=coche_data, clientes=lista_clientes)
    except pymysql.MySQLError as e:
        flash(f'Error al obtener datos del coche: {e}', 'error')
        return redirect(url_for('coches'))
    finally:
        if conn:
            conn.close()

@app.route('/coches/eliminar/<string:matricula>', methods=['POST'])
def eliminar_coche(matricula):
    """Maneja la eliminación de un coche."""
    conn = connect_to_db()
    if not conn:
        return redirect(url_for('coches'))
        
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM coches WHERE matricula = %s", (matricula,))
        conn.commit()
        flash('Coche eliminado correctamente.', 'success')
    except pymysql.MySQLError as e:
        if e.args[0] == 1451:
            flash('No se puede eliminar el coche porque tiene revisiones asociadas.', 'error')
        else:
            flash(f'Error al eliminar coche: {e}', 'error')
    finally:
        conn.close()
    return redirect(url_for('coches'))


# --- 5. RUTAS PARA REVISIONES ---
# Se adaptaron las rutas de 'consultorios' para 'revisiones'.
@app.route('/revisiones', methods=['GET', 'POST'])
def revisiones():
    """Muestra la lista de revisiones y maneja la creación de nuevas revisiones."""
    conn = connect_to_db()
    if not conn:
        return render_template('revisiones.html', revisiones=[], coches=[])

    if request.method == 'POST':
        try:
            codigo = request.form['codigo']
            filtro = request.form['filtro']
            aceite = request.form['aceite']
            frenos = request.form['frenos']
            matricula_coche = request.form['matricula_coche']

            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO revisiones (codigo, filtro, aceite, frenos, matricula_coche) VALUES (%s, %s, %s, %s, %s)",
                    (codigo, filtro, aceite, frenos, matricula_coche)
                )
            conn.commit()
            flash('Revisión agregada correctamente.', 'success')
        except pymysql.MySQLError as e:
            flash(f'Error al agregar revisión: {e}', 'error')
        finally:
            conn.close()
        return redirect(url_for('revisiones'))

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM revisiones ORDER BY codigo")
            lista_revisiones = cur.fetchall()
            # Necesitamos la lista de coches para el formulario
            cur.execute("SELECT matricula, marca, modelo FROM coches ORDER BY marca")
            lista_coches = cur.fetchall()
        return render_template('revisiones.html', revisiones=lista_revisiones, coches=lista_coches)
    except pymysql.MySQLError as e:
        flash(f'Error al obtener datos: {e}', 'error')
        return render_template('revisiones.html', revisiones=[], coches=[])
    finally:
        if conn:
            conn.close()

@app.route('/revisiones/editar/<int:codigo>', methods=['GET', 'POST'])
def editar_revision(codigo):
    """Muestra el formulario para editar una revisión y maneja la actualización."""
    conn = connect_to_db()
    if not conn:
        return redirect(url_for('revisiones'))

    if request.method == 'POST':
        try:
            filtro = request.form['filtro']
            aceite = request.form['aceite']
            frenos = request.form['frenos']
            matricula_coche = request.form['matricula_coche']
            
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE revisiones
                    SET filtro=%s, aceite=%s, frenos=%s, matricula_coche=%s
                    WHERE codigo=%s
                """, (filtro, aceite, frenos, matricula_coche, codigo))
            conn.commit()
            flash('Revisión actualizada correctamente.', 'success')
        except pymysql.MySQLError as e:
            flash(f'Error al actualizar revisión: {e}', 'error')
        finally:
            conn.close()
        return redirect(url_for('revisiones'))
        
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM revisiones WHERE codigo = %s", (codigo,))
            revision_data = cur.fetchone()
            cur.execute("SELECT matricula, marca, modelo FROM coches ORDER BY marca")
            lista_coches = cur.fetchall()
        
        if not revision_data:
            flash('Revisión no encontrada.', 'warning')
            return redirect(url_for('revisiones'))
            
        return render_template('editar_revision.html', revision=revision_data, coches=lista_coches)
    except pymysql.MySQLError as e:
        flash(f'Error al obtener datos de la revisión: {e}', 'error')
        return redirect(url_for('revisiones'))
    finally:
        if conn:
            conn.close()

@app.route('/revisiones/eliminar/<int:codigo>', methods=['POST'])
def eliminar_revision(codigo):
    """Maneja la eliminación de una revisión."""
    conn = connect_to_db()
    if not conn:
        return redirect(url_for('revisiones'))
        
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM revisiones WHERE codigo = %s", (codigo,))
        conn.commit()
        flash('Revisión eliminada correctamente.', 'success')
    except pymysql.MySQLError as e:
        flash(f'Error al eliminar revisión: {e}', 'error')
    finally:
        conn.close()
    return redirect(url_for('revisiones'))

if __name__ == '__main__':
    app.run(debug=True)
