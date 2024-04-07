"""Vista que gestiona la lógica de los métodos HTTP para la tabla empleado de la base de datos"""

# Se importa la clase Flask y la función jsonify
from flask import jsonify, request
# Se importa la clase OperationalError de MySQLdb
from MySQLdb import OperationalError, IntegrityError
from werkzeug.security import generate_password_hash

#! MÉTODOS HTTP PARA TABLA EMPLEADO

# * GET


def obtener_empleado(id_empleado, cursor):
    """Función GET para obtener un empleado específico o todos los empleados de la base de datos"""
    try:
        # Se ejecuta una consulta SQL
        if id_empleado == 'todos':
            cursor.execute(
                'SELECT * FROM empleado')
        else:
            cursor.execute(
                'SELECT * FROM empleado WHERE idEmpleado = %s', (id_empleado,))
        empleados = cursor.fetchall()  # Se obtienen todos los registros de la consulta
        diccionario = []  # Se crea un diccionario vacío
        for registro in empleados:  # Se recorren los registros obtenidos
            arreglo = {  # Se crea un arreglo con los datos de un registro
                'idEmpleado': registro[0],
                'nombre': registro[1],
                'apellidoPaterno': registro[2],
                'apellidoMaterno': registro[3],
                'telefono': registro[4],
                'correo': registro[5],
                'esAdministrador': registro[6]
            }
            diccionario.append(arreglo)  # Se agrega el arreglo al diccionario
            # Se retorna un objeto JSON con el diccionario obtenido
        return jsonify({'success': True, 'status': 200, 'message': 'Consulta exitosa', 'data': diccionario})
    except OperationalError as e:
        # Se retorna un objeto JSON con un error 500
        return jsonify({'error': {'code': 500, 'type': 'Error del servidor', 'message': 'Error en la base de datos', 'details': str(e)}})

# * POST


def registrar_empleado(cursor, conexion):
    """Función POST para registrar un empleado en la base de datos"""
    try:
        body = request.json  # Se obtiene el cuerpo de la petición
        # Se ejecuta una consulta SQL con parámetros
        cursor.execute('INSERT INTO empleado VALUES (%s, %s, %s, %s, %s, %s, MD5(%s), %s)', (body['idEmpleado'].upper(), body['nombre'].upper(), body['apellidoPaterno'].upper(), body['apellidoMaterno'].upper(), body['telefono'], body['correo'].upper(), body['contrasenia'], body['esAdministrador']))
        conexion.connection.commit()  # Se confirma la transacción
        # Se retorna un objeto JSON con un mensaje de éxito
        return jsonify({'success': True, 'status': 201, 'message': 'Registro exitoso'})
    except IntegrityError as e:
        # Se retorna un objeto JSON con un error 500
        return jsonify({'error': {'code': 400, 'type': 'Error del cliente', 'message': 'Error de integridad MySQL', 'details': str(e)}})

# *PUT


def actualizar_empleado(id_empleado, cursor, conexion):
    """Función PUT para actualizar un empleado específico en la base de datos"""
    try:
        empleado = request.json
        contrasenia_encriptada = generate_password_hash(
            empleado['contrasenia'], method='pbkdf2:sha256')
        cursor.execute(
            'SELECT nombre, apellidoPaterno, apellidoMaterno, telefono, correo, contrasenia, esAdministrador FROM empleado WHERE idEmpleado = %s', (id_empleado,))
        if cursor.fetchone() is not None:
            cursor.execute('UPDATE empleado SET nombre = %s, apellidoPaterno = %s, apellidoMaterno = %s, telefono = %s, correo = %s, contrasenia = %s, esAdministrador = %s WHERE idEmpleado = %s', (empleado['nombre'].upper(), empleado['apellidoPaterno'].upper(), empleado['apellidoMaterno'].upper(), empleado['telefono'], empleado['correo'].upper(), contrasenia_encriptada, empleado['esAdministrador'], id_empleado,))
            conexion.connection.commit()
            return jsonify({'success': True, 'status': 202, 'message': 'Actualización exitosa', 'data': empleado})
        else:
            # Se retorna un objeto JSON con un error 404
            return jsonify({'error': {'code': 404, 'type': 'Error del cliente', 'message': 'Empleado no encontrado', 'details': f'No se encontró el empleado {id_empleado} en la base de datos'}})
    except OperationalError as e:
        # Se retorna un objeto JSON con un error 500
        return jsonify({'success': False, 'status': 500, 'message': 'Error en la base de datos', 'error': str(e)})

# * DELETE


def eliminar_empleado(id_empleado, cursor, conexion):
    """Función DELETE para eliminar un empleado específico o todos los empleados de la base de datos"""
    try:
        # Se ejecuta una consulta SQL
        cursor.execute(
            'DELETE FROM empleado WHERE idEmpleado = %s', (id_empleado,))
        conexion.connection.commit()
        return jsonify({'success': True, 'status': 200, 'message': 'Empleado eliminado'})
    except OperationalError as e:
        # Se retorna un objeto JSON con un error 500
        return jsonify({'error': {'code': 500, 'type': 'Error del servidor', 'message': 'Error en la base de datos', 'details': str(e)}})

# * PATCH


def cambiar_contrasenia_empleado(id_empleado, cursor, conexion):
    """Función PATCH para cambiar la contraseña de un empleado específico en la base de datos"""
    try:
        body = request.json
        cursor.execute(f'SELECT idEmpleado FROM empleado WHERE idEmpleado = {id_empleado}')
        if cursor.fetchone() is not None:
            if 'contrasenia' in body:
                cursor.execute('UPDATE empleado SET contrasenia = MD5(%s) WHERE idEmpleado = %s', (body['contrasenia'], id_empleado,))
                conexion.connection.commit()
                return jsonify({'success': True, 'status': 200, 'message': f'Se ha actualizado la contraseña del empleado {id_empleado} exitosamente'})
            # Se retorna un objeto JSON con un error 400
            return jsonify({'error': {'code': 400, 'type': 'Error del cliente', 'message': 'Petición incorrecta', 'details': 'Falta la clave contrasenia en el body de la petición'}})
        # Se retorna un objeto JSON con un error 404
        return jsonify({'error': {'code': 404, 'type': 'Error del cliente', 'message': 'Empleado no encontrado', 'details': f'No se encontró el empleado {id_empleado} en la base de datos'}})
    except KeyError as e:
        # Se retorna un objeto JSON con un error 400
        return jsonify({'error': {'code': 400, 'type': 'Error del cliente', 'message': 'Petición inválida', 'details': f'Falta la clave {str(e)} en el body de la petición'}})
    except IntegrityError as e:
        # Se retorna un objeto JSON con un error 400
        return jsonify({'error': {'code': 400, 'type': 'Error del cliente', 'message': 'Error de integridad MySQL', 'details': str(e)}})
    except OperationalError as e:
        # Se retorna un objeto JSON con un error 500
        return jsonify({'success': False, 'status': 500, 'message': 'Error en la base de datos', 'error': str(e)})

# * POST (Iniciar sesión)


def iniciar_sesion_empleado(cursor):
    """Función POST para iniciar sesión de un empleado"""
    try:
        body = request.json  # Se obtiene el cuerpo de la petición
        cursor.execute('SELECT COUNT(idEmpleado) > 0 WHERE correo = %s AND contrasenia = MD5(%s)', (body['correo'], body['contrasenia']))
        if cursor.fetchone()[0]:
            return jsonify({'success': True, 'status': 200, 'message': 'Inicio de sesión exitoso'})
        # Se retorna un objeto JSON con un error 404
        return jsonify({'error': {'code': 404, 'type': 'Error del cliente', 'message': 'Empleado no encontrado', 'details': 'No se encontró el empleado en la base de datos'}})
    except KeyError as e:
        # Se retorna un objeto JSON con un error 400
        return jsonify({'error': {'code': 400, 'type': 'Error del cliente', 'message': 'Petición inválida', 'details': f'Falta la clave {str(e)} en el body de la petición'}})
    except OperationalError as e:
        # Se retorna un objeto JSON con un error 500
        return jsonify({'error': {'code': 500, 'type': 'Error del servidor', 'message': 'Error en la base de datos', 'details': str(e)}})
