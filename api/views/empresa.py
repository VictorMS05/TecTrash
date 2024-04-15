"""Vista que gestiona la lógica de los métodos HTTP para la tabla empresa de la base de datos"""

# Se importa la clase Flask y la función jsonify
from flask import jsonify, request
# Se importa la clase OperationalError de MySQLdb
from MySQLdb import OperationalError, IntegrityError

#! MÉTODOS HTTP PARA TABLA EMPRESA

# *GET


def obtener_empresa(id_empresa, cursor):
    """Función GET para obtener una empresa específica o todas las empresas de la base de datos"""
    try:
        # Se ejecuta una consulta SQL
        if id_empresa == 'todos':
            cursor.execute('SELECT idEmpresa, nombre, calle, numeroExterior, colonia, ciudad, '
                            'estado, telefono, correo, contrasenia,  nombreEncargado, '
                            'apellidoPaternoE, apellidoMaternoE, esEntrega, pesoEstablecido FROM '
                            'empresa')
        else:
            cursor.execute(f'SELECT idEmpresa, nombre, calle, numeroExterior, colonia, ciudad, '
                            f'estado, telefono, correo, contrasenia,nombreEncargado, '
                            f'apellidoPaternoE, apellidoMaternoE, esEntrega, pesoEstablecido FROM '
                            f'empresa WHERE idEmpresa = {id_empresa}')
        empresas = cursor.fetchall()  # Se obtienen todos los registros de la consulta
        diccionario = []  # Se crea un diccionario vacío
        for registro in empresas:  # Se recorren los registros obtenidos
            arreglo = {  # Se crea un arreglo con los datos de un registro
                'idEmpresa': registro[0],
                'nombre': registro[1],
                'calle': registro[2],
                'numeroExterior': registro[3],
                'colonia': registro[4],
                'ciudad': registro[5],
                'estado': registro[6],
                'telefono': registro[7],
                'correo': registro[8],
                'contrasenia': registro[9],
                'nombreEncargado': registro[10],
                'apellidoPaternoE': registro[11],
                'apellidoMaternoE': registro[12],
                'esEntrega': registro[13],
                'pesoEstablecido': registro[14]
            }
            diccionario.append(arreglo)  # Se agrega el arreglo al diccionario
            # Se retorna un objeto JSON con el diccionario obtenido
        return jsonify({'success': True,
                        'status': 200, 
                        'message': 'Consulta exitosa', 
                        'data': diccionario})
    except OperationalError as e:
        # Se retorna un objeto JSON con un error 500
        return jsonify({'error': {'code': 500,
                                    'type': 'Error del servidor', 
                                    'message': 'Error en la base de datos', 
                                    'details': str(e)}})

# * POST


def registrar_empresa(cursor, conexion):
    """Función POST para registrar una empresa en la base de datos"""
    try:
        body = request.json  # Se obtiene el cuerpo de la petición
        # Se ejecuta una consulta SQL con parámetros
        cursor.execute('INSERT INTO empresa VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, MD5(%s), '
                        '%s, %s, %s, %s, %s)', (body['rfc'].upper(), body['nombre'].upper(), 
                                                body['calle'].upper(), body['numeroExterior'],
                                                body['colonia'].upper(), body['ciudad'].upper(),
                                                body['estado'].upper(), body['telefono'],
                                                body['correo'], body['contrasenia'],
                                                body['nombreEncargado'].upper(),
                                                body['apellidoPaternoE'].upper(),
                                                body['apellidoMaternoE'].upper(), body['esEntrega'],
                                                body['pesoEstablecido']))
        conexion.connection.commit()  # Se confirma la transacción
        # Se retorna un objeto JSON con un mensaje de éxito
        return jsonify({'success': True,
                        'status': 201, 
                        'message': 'Registro exitoso', 
                        'data': {'rfc': body['rfc'].upper(), 
                                'nombre': body['nombre'].upper(), 
                                'calle': body['calle'].upper(), 
                                'numeroExterior': body['numeroExterior'], 
                                'colonia': body['colonia'].upper(), 
                                'ciudad': body['ciudad'].upper(), 
                                'estado': body['estado'].upper(), 
                                'telefono': body['telefono'], 
                                'correo': body['correo'], 
                                'nombreEncargado': body['nombreEncargado'].upper(), 
                                'apellidoPaternoE': body['apellidoPaternoE'].upper(), 
                                'apellidoMaternoE': body['apellidoMaternoE'].upper(), 
                                'esEntrega': body['esEntrega'], 
                                'pesoEstablecido': body['pesoEstablecido']}})
    except KeyError as e:
        # Se retorna un objeto JSON con un error 400
        return jsonify({'error': {'code': 400,
                                    'type': 'Error del cliente', 
                                    'message': 'Petición inválida', 
                                    'details': f'Falta la clave {str(e)} en el body de la '
                                                f'petición'}})
    except IntegrityError as e:
        # Se retorna un objeto JSON con un error 400
        return jsonify({'error': {'code': 400,
                                    'type': 'Error del cliente', 
                                    'message': 'Error de integridad MySQL', 
                                    'details': str(e)}})
    except OperationalError as e:
        # Se retorna un objeto JSON con un error 500
        return jsonify({'error': {'code': 500,
                                    'type': 'Error del servidor', 
                                    'message': 'Error en la base de datos', 
                                    'details': str(e)}})


# * PUT


def actualizar_empresa(id_empresa, cursor, conexion):
    """Función PUT para actualizar una empresa específica en la base de datos"""
    empresa = request.json
    try:
        empresa = request.json
        cursor.execute(f'SELECT nombre, calle, numeroExterior, colonia, ciudad, estado, telefono, '
                        f'correo, contrasenia, nombreEncargado, apellidoPaternoE, apellidoMaternoE, '
                        f'esEntrega, pesoEstablecido FROM empresa WHERE idEmpresa = %s', (id_empresa,))
        if cursor.fetchone() is not None:
            cursor.execute('UPDATE empresa SET nombre = %s, calle = %s, numeroExterior = %s, colonia = %s, ciudad = %s, estado = %s, telefono = %s, correo = %s, nombreEncargado = %s, apellidoPaternoE = %s, apellidoMaternoE = %s, esEntrega = %s, pesoEstablecido = %s WHERE idEmpresa = %s', (
                empresa['nombre'].upper(), empresa['calle'].upper(), empresa['numeroExterior'], empresa['colonia'].upper(), empresa['ciudad'].upper(), empresa['estado'].upper(), empresa['telefono'], empresa['correo'].upper(), empresa['nombreEncargado'].upper(), empresa['apellidoPaternoE'].upper(), empresa['apellidoMaternoE'].upper(), empresa['esEntrega'], empresa['pesoEstablecido'], id_empresa,))
            conexion.connection.commit()
            return jsonify({'success': True, 'status': 202, 'message': 'Actualización exitosa', 'data': empresa})
        else:
            # Se retorna un objeto JSON con un error 404
            return jsonify({'error': {'code': 404, 'type': 'Error del cliente', 'message': 'Empresa no encontrada', 'details': f'No se encontró la empresa {id_empresa} en la base de datos'}})
    except IntegrityError as e:
        # Se retorna un objeto JSON con un error 400
        return jsonify({'error': {'code': 400, 'type': 'Error del cliente', 'message': 'Error de integridad MySQL', 'details': str(e)}})

# * DELETE


def eliminar_empresa(id_empresa, cursor, conexion):
    """Función DELETE para eliminar una empresa específica o todas las empresas de la base de datos"""
    try:
        # Se ejecuta una consulta SQL
        cursor.execute(
            'DELETE FROM empresa WHERE idEmpresa = %s', (id_empresa,))
        conexion.connection.commit()
        return jsonify({'success': True, 'status': 200, 'message': 'Empresa eliminada'})
    except OperationalError as e:
        # Se retorna un objeto JSON con un error 500
        return jsonify({'error': {'code': 500, 'type': 'Error del servidor', 'message': 'Error en la base de datos', 'details': str(e)}})

# * PATCH


def cambiar_contrasenia_empresa(id_empresa, cursor, conexion):
    """Función PATCH para cambiar la contraseña de una empresa específica en la base de datos"""
    try:
        body = request.json['contrasenia']
        cursor.execute(
            f'SELECT idEmpresa FROM empresa WHERE idEmpresa = {id_empresa}')
        if cursor.fetchone() is not None:
            if 'contrasenia' in body:
                contrasenia_encriptada = generate_password_hash(body['contrasenia'], method='pbkdf2:sha256')
                cursor.execute('UPDATE empresa SET contrasenia = %s WHERE idEmpresa = %s', (contrasenia_encriptada, id_empresa,))
                conexion.connection.commit()
                return jsonify({'success': True, 'status': 200, 'message': 'Contraseña actualizada'})
            # Se retorna un objeto JSON con un error 400
            return jsonify({'error': {'code': 400, 'type': 'Error del cliente', 'message': 'Petición incorrecta', 'details': 'Falta la clave contrasenia en el body de la petición'}})
        # Se retorna un objeto JSON con un error 404
        return jsonify({'error': {'code': 404, 'type': 'Error del cliente', 'message': 'Empresa no encontrada', 'details': f'No se encontró la empresa {id_empresa} en la base de datos'}})
    except KeyError as e:
        # Se retorna un objeto JSON con un error 400
        return jsonify({'error': {'code': 400, 'type': 'Error del cliente', 'message': 'Petición inválida', 'details': f'Falta la clave {str(e)} en el body de la petición'}})
    except IntegrityError as e:
        # Se retorna un objeto JSON con un error 400
        return jsonify({'error': {'code': 400, 'type': 'Error del cliente', 'message': 'Error de integridad MySQL', 'details': str(e)}})
    except OperationalError as e:
        # Se retorna un objeto JSON con un error 500
        return jsonify({'error': {'code': 500, 'type': 'Error del servidor', 'message': 'Error en la base de datos', 'details': str(e)}})
