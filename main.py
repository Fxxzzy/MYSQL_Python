import sqlite3

def autenticar_usuario(usuario, contraseña):
    try:
        # Conectar a la base de datos SQLite (o crearla si no existe)
        conexion = sqlite3.connect("base_de_datos.db")

        # Crear un cursor para ejecutar consultas
        cursor = conexion.cursor()

        # Consulta para verificar el usuario y la contraseña
        consulta = "SELECT * FROM usuarios WHERE nombre_usuario = ? AND contraseña = ?"
        parametros = (usuario, contraseña)
        cursor.execute(consulta, parametros)

        # Obtener el resultado de la consulta
        resultado = cursor.fetchone()

        # Cerrar el cursor y la conexión
        cursor.close()
        conexion.close()

        return resultado is not None

    except sqlite3.Error as error:
        print(f"Error al conectar a la base de datos: {error}")
        return False

# Crear la tabla de usuarios si no existe
try:
    conexion = sqlite3.connect("base_de_datos.db")
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_usuario TEXT,
            contraseña TEXT
        )
    """)

    conexion.commit()
    cursor.close()
    conexion.close()

except sqlite3.Error as error:
    print(f"Error al crear la tabla: {error}")

# Solicitar al usuario que ingrese el nombre de usuario y la contraseña
usuario_ingresado = input("Ingrese su nombre de usuario: ")
contraseña_ingresada = input("Ingrese su contraseña: ")

# Autenticar al usuario
if autenticar_usuario(usuario_ingresado, contraseña_ingresada):
    print("¡Inicio de sesión exitoso!")
else:
    print("Nombre de usuario o contraseña incorrectos. Intenta de nuevo.")
