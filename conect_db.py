import mysql.connector
import datetime
from win10toast import ToastNotifier
import csv
import os

def crear_tabla(conexion):
    try:
        # Obtener la lista de bases de datos
        cursor = conexion.cursor()
        cursor.execute("SHOW DATABASES;")
        bases_de_datos = cursor.fetchall()
        cursor.close()

        # Mostrar las bases de datos disponibles
        print("Bases de datos disponibles:")
        for base in bases_de_datos:
            print(base[0])

        # Seleccionar una base de datos
        nombre_base = input("Ingrese el nombre de la base de datos: ")

        # Verificar si la base de datos existe antes de proceder
        if (nombre_base,) not in bases_de_datos:
            notificacion("Error", f"La base de datos {nombre_base} no existe.")
            return

        cursor = conexion.cursor()
        cursor.execute(f"USE {nombre_base};")

        # Solicitar el nombre de la nueva tabla
        nombre_tabla = input("Ingrese el nombre de la nueva tabla: ")

        # Verificar si la tabla ya existe
        cursor.execute(f"SHOW TABLES LIKE '{nombre_tabla}';")
        if cursor.fetchone():
            notificacion("Error", f"La tabla {nombre_tabla} ya existe en la base de datos {nombre_base}.")
            return

        # Solicitar las columnas de la nueva tabla
        columnas = []
        while True:
            nombre_columna = input("Ingrese el nombre de la columna (o 'fin' para terminar): ")
            if nombre_columna.lower() == 'fin':
                break

            tipo_dato = input(f"Ingrese el tipo de dato para la columna {nombre_columna} (e.g., VARCHAR(255)): ")
            if 'VARCHAR' in tipo_dato:
                longitud = input("Ingrese la longitud para VARCHAR (e.g., 255): ")
                tipo_dato = f"VARCHAR({longitud})"

            columnas.append(f"{nombre_columna} {tipo_dato}")

        # Verificar si se han ingresado al menos dos columnas
        if len(columnas) < 2:
            notificacion("Error", "Se necesitan al menos dos columnas para crear una tabla.")
            return

        # Solicitar la clave primaria
        primary_key = input("Ingrese el nombre de la clave primaria: ")

        # Construir la consulta de creación de tabla
        consulta = f"CREATE TABLE {nombre_tabla} ({', '.join(columnas)}, PRIMARY KEY ({primary_key}));"

        # Mostrar la consulta en consola
        mostrar_consulta(consulta)

        # Ejecutar la consulta de creación de tabla
        cursor.execute(consulta)
        conexion.commit()
        cursor.close()

        notificacion("Tabla Creada", f"La tabla {nombre_tabla} ha sido creada en la base de datos {nombre_base}", [consulta])

    except mysql.connector.Error as err:
        notificacion("Error", f"No se pudo crear la tabla: {err}")


def realizar_respaldo(conexion):
    try:
        # Obtener la lista de bases de datos
        cursor = conexion.cursor()
        cursor.execute("SHOW DATABASES;")
        bases_de_datos = cursor.fetchall()
        cursor.close()

        # Mostrar las bases de datos disponibles
        print("Bases de datos disponibles:")
        for base in bases_de_datos:
            print(base[0])

        # Seleccionar una base de datos para respaldo
        nombre_base_resp = input("Ingrese el nombre de la base de datos para realizar el respaldo: ")

        # Verificar si la base de datos existe antes de proceder
        if (nombre_base_resp,) not in bases_de_datos:
            notificacion("Error", f"La base de datos {nombre_base_resp} no existe.")
            return

        # Obtener la fecha actual para incluir en el nombre del archivo de respaldo
        fecha_actual = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Crear un archivo SQL para el respaldo
        nombre_archivo_respaldo = f"respaldo_{nombre_base_resp}_{fecha_actual}.sql"
        ruta_archivo_respaldo = os.path.join(os.getcwd(), nombre_archivo_respaldo)

        with open(ruta_archivo_respaldo, mode='w', encoding='utf-8') as archivo_sql:
            # Obtener la estructura de las tablas
            cursor = conexion.cursor()
            cursor.execute(f"SHOW TABLES FROM {nombre_base_resp};")
            tablas_resp = cursor.fetchall()

            # Recorrer las tablas y obtener la estructura y datos
            for tabla_resp in tablas_resp:
                tabla_resp = tabla_resp[0]
                cursor.execute(f"SHOW CREATE TABLE {nombre_base_resp}.{tabla_resp};")
                create_table_statement = cursor.fetchone()[1]

                # Escribir la estructura de la tabla al archivo SQL
                archivo_sql.write(f"\n\n{create_table_statement};\n\n")

                # Obtener y escribir los datos de la tabla al archivo SQL
                cursor.execute(f"SELECT * FROM {nombre_base_resp}.{tabla_resp};")
                datos_resp = cursor.fetchall()

                for fila_resp in datos_resp:
                    valores = ", ".join([f"'{str(valor)}'" if valor is not None else "NULL" for valor in fila_resp])
                    archivo_sql.write(f"INSERT INTO {nombre_base_resp}.{tabla_resp} VALUES ({valores});\n")

        notificacion("Respaldo Exitoso", f"El respaldo de la base de datos {nombre_base_resp} se ha realizado correctamente. Archivo: {nombre_archivo_respaldo}")

    except mysql.connector.Error as err:
        notificacion("Error", f"No se pudo realizar el respaldo: {err}")

def actualizar_datos(conexion):
    try:
        # Obtener la lista de bases de datos
        cursor = conexion.cursor()
        cursor.execute("SHOW DATABASES;")
        bases_de_datos = cursor.fetchall()
        cursor.close()

        # Mostrar las bases de datos disponibles
        print("Bases de datos disponibles:")
        for base in bases_de_datos:
            print(base[0])

        # Seleccionar una base de datos
        nombre_base = input("Ingrese el nombre de la base de datos: ")

        # Verificar si la base de datos existe antes de proceder
        if (nombre_base,) not in bases_de_datos:
            notificacion("Error", f"La base de datos {nombre_base} no existe.")
            return

        cursor = conexion.cursor()
        cursor.execute(f"USE {nombre_base};")
        cursor.execute("SHOW TABLES;")
        tablas = cursor.fetchall()
        cursor.close()

        # Mostrar las tablas disponibles en la base de datos seleccionada
        print("Tablas disponibles:")
        for tabla in tablas:
            print(tabla[0])

        # Seleccionar una tabla
        tabla_seleccionada = input("Ingrese el nombre de la tabla: ")

        cursor = conexion.cursor()
        cursor.execute(f"DESCRIBE {tabla_seleccionada};")
        columnas_info = cursor.fetchall()
        cursor.close()

        # Construir un diccionario de tipo de datos para cada columna
        tipos_de_datos = {columna[0]: columna[1] for columna in columnas_info}

        # Mostrar las columnas en consola
        print(f"Columnas de la tabla {tabla_seleccionada}:")
        for columna in columnas_info:
            print(columna[0])

        # Obtener la clave primaria de la tabla
        cursor = conexion.cursor()
        cursor.execute(f"SHOW KEYS FROM {tabla_seleccionada} WHERE Key_name = 'PRIMARY';")
        primary_key_info = cursor.fetchone()
        cursor.close()

        if not primary_key_info:
            notificacion("Error", "La tabla seleccionada no tiene una clave primaria definida.")
            return

        primary_key_name = primary_key_info[4]

        # Pedir al usuario el valor de la clave primaria para la actualización
        primary_key_value = input(f"Ingrese el valor de la clave primaria ({primary_key_name}): ")

        # Construir la consulta de actualización
        set_clauses = []
        for columna in columnas_info:
            nombre_columna = columna[0]
            nuevo_valor = input(f"Ingrese el nuevo valor para la columna {nombre_columna}: ")

            # Convertir a cadena si la columna es de tipo VARCHAR
            if tipos_de_datos[nombre_columna].startswith("varchar"):
                nuevo_valor = f"'{nuevo_valor}'"

            set_clauses.append(f"{nombre_columna} = {nuevo_valor}")

        consulta = f"UPDATE {tabla_seleccionada} SET {', '.join(set_clauses)} WHERE {primary_key_name} = '{primary_key_value}';"

        # Mostrar la consulta en consola
        mostrar_consulta(consulta)

        # Ejecutar la consulta de actualización
        cursor = conexion.cursor()
        cursor.execute(consulta)
        conexion.commit()
        cursor.close()

        notificacion("Actualización", f"Datos actualizados en {tabla_seleccionada} con clave primaria {primary_key_name}={primary_key_value}", [consulta])

    except mysql.connector.Error as err:
        notificacion("Error", f"No se pudieron actualizar los datos: {err}")


def descargar_registros(conexion):
    try:
        # Obtener la lista de bases de datos
        cursor = conexion.cursor()
        cursor.execute("SHOW DATABASES;")
        bases_de_datos = cursor.fetchall()
        cursor.close()

        # Mostrar las bases de datos disponibles
        print("Bases de datos disponibles:")
        for base in bases_de_datos:
            print(base[0])

        # Seleccionar una base de datos
        nombre_base = input("Ingrese el nombre de la base de datos: ")

        # Verificar si la base de datos existe antes de proceder
        if (nombre_base,) not in bases_de_datos:
            notificacion("Error", f"La base de datos {nombre_base} no existe.")
            return

        cursor = conexion.cursor()
        cursor.execute(f"USE {nombre_base};")
        cursor.execute("SHOW TABLES;")
        tablas = cursor.fetchall()
        cursor.close()

        # Mostrar las tablas disponibles en la base de datos seleccionada
        print("Tablas disponibles:")
        for tabla in tablas:
            print(tabla[0])

        # Seleccionar una tabla
        tabla_seleccionada = input("Ingrese el nombre de la tabla: ")

        cursor = conexion.cursor()
        cursor.execute(f"SELECT * FROM {tabla_seleccionada};")
        datos = cursor.fetchall()

        # Verificar si hay datos en la tabla
        if not datos:
            notificacion("Advertencia", f"No hay datos en la tabla {tabla_seleccionada}.")
            return

        # Obtener los nombres de las columnas
        cursor.execute(f"DESCRIBE {tabla_seleccionada};")
        columnas_info = [columna[0] for columna in cursor.fetchall()]

        # Pedir al usuario el nombre del archivo CSV
        nombre_archivo = input("Ingrese el nombre del archivo CSV (sin extensión): ")

        # Construir el nombre completo del archivo CSV
        nombre_completo_archivo = f"{nombre_archivo}.csv"

        # Escribir los datos en el archivo CSV
        with open(nombre_completo_archivo, mode='w', newline='', encoding='utf-8') as archivo_csv:
            escritor_csv = csv.writer(archivo_csv)
            
            # Escribir encabezados
            escritor_csv.writerow(columnas_info)

            # Escribir datos
            escritor_csv.writerows(datos)

        notificacion("Descarga Exitosa", f"Los datos de la tabla {tabla_seleccionada} han sido descargados en {nombre_completo_archivo}")

    except mysql.connector.Error as err:
        notificacion("Error", f"No se pudieron descargar los datos: {err}")

def notificacion(titulo, cuerpo, datos=None):
    toaster = ToastNotifier()
    mensaje = f"{cuerpo}\n\nDatos:\n{datos}" if datos else cuerpo
    toaster.show_toast(titulo, mensaje, duration=10)

def mostrar_consulta(consulta):
    print("Consulta ejecutada:")
    print(consulta)

def crear_base_de_datos(conexion):
    nombre_base = input("Ingrese el nombre de la base de datos a crear: ")
    try:
        cursor = conexion.cursor()
        cursor.execute(f"CREATE DATABASE {nombre_base};")
        conexion.commit()
        cursor.close()
        notificacion("BASE DE DATOS", f"La base de datos {nombre_base} ha sido creada")
    except mysql.connector.Error as err:
        notificacion("Error", f"No se pudo crear la base de datos: {err}")

def mostrar_bases_de_datos(conexion):
    try:
        cursor = conexion.cursor()
        cursor.execute("SHOW DATABASES;")
        bases_de_datos = cursor.fetchall()
        cursor.close()
        for base in bases_de_datos:
            print(base[0])
        notificacion("Bases de Datos", "Todas las bases de datos han sido mostradas")
    except mysql.connector.Error as err:
        notificacion("Error", f"No se pudieron mostrar las bases de datos: {err}")

def mostrar_tablas(conexion, nombre_base):
    try:
        cursor = conexion.cursor()
        cursor.execute(f"USE {nombre_base};")
        cursor.execute("SHOW TABLES;")
        tablas = cursor.fetchall()
        cursor.close()
        for tabla in tablas:
            print(tabla[0])

        tabla_seleccionada = input("Seleccione una tabla para ver sus datos: ")
        consulta = f"SELECT * FROM {tabla_seleccionada};"

        cursor = conexion.cursor()
        cursor.execute(consulta)
        datos = cursor.fetchall()

        # Crear una lista de cadenas formateadas para cada fila de datos
        datos_formateados = [', '.join(map(str, fila)) for fila in datos]

        mostrar_consulta(consulta)
        notificacion("Datos", f"Datos de {tabla_seleccionada} han sido mostrados", datos_formateados)

    except mysql.connector.Error as err:
        notificacion("Error", f"No se pudieron mostrar las tablas: {err}")

def insertar_datos(conexion):
    try:
        # Obtener la lista de bases de datos
        cursor = conexion.cursor()
        cursor.execute("SHOW DATABASES;")
        bases_de_datos = cursor.fetchall()
        cursor.close()

        # Mostrar las bases de datos disponibles
        print("Bases de datos disponibles:")
        for base in bases_de_datos:
            print(base[0])

        # Seleccionar una base de datos
        nombre_base = input("Ingrese el nombre de la base de datos: ")

        # Verificar si la base de datos existe antes de proceder
        if (nombre_base,) not in bases_de_datos:
            notificacion("Error", f"La base de datos {nombre_base} no existe.")
            return

        cursor = conexion.cursor()
        cursor.execute(f"USE {nombre_base};")
        cursor.execute("SHOW TABLES;")
        tablas = cursor.fetchall()
        cursor.close()

        # Mostrar las tablas disponibles en la base de datos seleccionada
        print("Tablas disponibles:")
        for tabla in tablas:
            print(tabla[0])

        # Seleccionar una tabla
        tabla_seleccionada = input("Ingrese el nombre de la tabla: ")

        cursor = conexion.cursor()
        cursor.execute(f"DESCRIBE {tabla_seleccionada};")
        columnas_info = cursor.fetchall()
        cursor.close()

        # Construir un diccionario de tipo de datos para cada columna
        tipos_de_datos = {columna[0]: columna[1] for columna in columnas_info}

        # Mostrar las columnas en consola
        print(f"Columnas de la tabla {tabla_seleccionada}:")
        for columna in columnas_info:
            print(columna[0])

        # Construir la consulta de inserción
        columnas = [columna[0] for columna in columnas_info]
        valores = []
        for columna in columnas_info:
            nombre_columna = columna[0]
            valor = input(f"Ingrese el valor para la columna {nombre_columna}: ")

            # Convertir a cadena si la columna es de tipo VARCHAR
            if tipos_de_datos[nombre_columna].startswith("varchar"):
                valor = f"'{valor}'"

            valores.append(valor)

        consulta = f"INSERT INTO {tabla_seleccionada} ({', '.join(columnas)}) VALUES ({', '.join(valores)});"

        # Mostrar la consulta en consola
        mostrar_consulta(consulta)

        cursor = conexion.cursor()
        cursor.execute(consulta)
        conexion.commit()
        cursor.close()

        notificacion("Inserción", f"Datos insertados en {tabla_seleccionada}", [consulta])

    except mysql.connector.Error as err:
        notificacion("Error", f"No se pudieron insertar los datos: {err}")

def eliminar_datos(conexion):
    try:
        # Obtener la lista de bases de datos
        cursor = conexion.cursor()
        cursor.execute("SHOW DATABASES;")
        bases_de_datos = cursor.fetchall()
        cursor.close()

        # Mostrar las bases de datos disponibles
        print("Bases de datos disponibles:")
        for base in bases_de_datos:
            print(base[0])

        # Seleccionar una base de datos
        nombre_base = input("Ingrese el nombre de la base de datos: ")

        # Verificar si la base de datos existe antes de proceder
        if (nombre_base,) not in bases_de_datos:
            notificacion("Error", f"La base de datos {nombre_base} no existe.")
            return

        cursor = conexion.cursor()
        cursor.execute(f"USE {nombre_base};")
        cursor.execute("SHOW TABLES;")
        tablas = cursor.fetchall()
        cursor.close()

        # Mostrar las tablas disponibles en la base de datos seleccionada
        print("Tablas disponibles:")
        for tabla in tablas:
            print(tabla[0])

        # Seleccionar una tabla
        tabla_seleccionada = input("Ingrese el nombre de la tabla: ")

        # Verificar si la tabla existe antes de proceder
        if (tabla_seleccionada,) not in tablas:
            notificacion("Error", f"La tabla {tabla_seleccionada} no existe en la base de datos {nombre_base}.")
            return

        # Obtener la clave primaria de la tabla
        cursor = conexion.cursor()
        cursor.execute(f"SHOW KEYS FROM {tabla_seleccionada} WHERE Key_name = 'PRIMARY';")
        primary_key_info = cursor.fetchone()
        cursor.close()

        if not primary_key_info:
            notificacion("Error", "La tabla seleccionada no tiene una clave primaria definida.")
            return

        primary_key_name = primary_key_info[4]

        # Pedir al usuario el valor de la clave primaria para la eliminación
        primary_key_value = input(f"Ingrese el valor de la clave primaria ({primary_key_name}): ")

        # Construir la consulta de eliminación
        consulta = f"DELETE FROM {tabla_seleccionada} WHERE {primary_key_name} = '{primary_key_value}';"

        # Mostrar la consulta en consola
        mostrar_consulta(consulta)

        # Ejecutar la consulta de eliminación
        cursor = conexion.cursor()
        cursor.execute(consulta)
        conexion.commit()
        cursor.close()

        notificacion("Eliminación", f"Datos eliminados en {tabla_seleccionada} con clave primaria {primary_key_name}={primary_key_value}", [consulta])

    except mysql.connector.Error as err:
        notificacion("Error", f"No se pudieron eliminar los datos: {err}")

# Solicitar datos de conexión al usuario
host = input("Ingrese el host de la base de datos: ")
usuario = input("Ingrese el nombre de usuario de la base de datos: ")
contrasena = input("Ingrese la contraseña de la base de datos: ")

try:
    # Intentar establecer la conexión
    conexion = mysql.connector.connect(
        host=host,
        user=usuario,
        password=contrasena,
        database=""
    )

    # Mostrar notificación de conexión exitosa
    notificacion("Conexión", "Conexión exitosa")

    while True:
        # Mostrar menú
        print("Menú:")
        print("1- Crear base de datos")
        print("2- Crear Tablas")
        print("3- Ver bases de datos")
        print("4- Consultas")
        print("5- Insertar datos")
        print("6- Eliminar datos")
        print("7- Actualizar un registro")
        print("8- Descargar registros")
        print("9- Hacer Resplado")
        print("10- salir")
        

        opcion = input("Seleccione una opción (1-10): ")

        if opcion == "1":
            crear_base_de_datos(conexion)
        elif opcion == "2":
            crear_tabla(conexion)
        elif opcion == "3":
            mostrar_bases_de_datos(conexion)
        elif opcion == "4":
            nombre_base = input("Ingrese el nombre de la base de datos: ")
            mostrar_tablas(conexion, nombre_base)
        elif opcion == "5":
            insertar_datos(conexion)
        elif opcion == "6":
            eliminar_datos(conexion)
        elif opcion == "7":
            descargar_registros(conexion)
        elif opcion == "8":
           actualizar_datos(conexion)
        elif opcion == "9":
            realizar_respaldo(conexion)
        elif opcion == "10":
            break
        
        
except mysql.connector.Error as err:
    # Mostrar notificación de error en la conexión
    notificacion("Error de Conexión", f"No se puede conectar: {err}")
