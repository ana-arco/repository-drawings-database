from flask import Flask, render_template
import mariadb
import sys

app = Flask(__name__)

# Función para conectar a la base de datos
def conectar_bd():
    try:
        conexion = mariadb.connect(
            user="tu_usuario",      # Cambia esto por tu usuario de MariaDB
            password="tu_password", # Cambia esto por tu contraseña
            host="localhost",
            port=3306,
            database="planos_telescopio"
        )
        return conexion
    except mariadb.Error as e:
        print(f"Error conectando a MariaDB: {e}")
        sys.exit(1)

# Ruta principal de la web
@app.route('/')
def inicio():
    conexion = conectar_bd()
    cursor = conexion.cursor(dictionary=True) # Devuelve los datos como diccionarios
    
    # Aquí hacemos la consulta real a la base de datos
    # (Suponiendo que ya tuviéramos la tabla drawings creada)
    consulta = """
        SELECT catalog_code, piece_name, material, author_initials, author_date 
        FROM drawings 
        LIMIT 10
    """
    
    try:
        cursor.execute(consulta)
        planos_desde_bd = cursor.fetchall()
    except mariadb.Error as e:
        print(f"Error en la consulta: {e}")
        planos_desde_bd = []
        
    conexion.close()
    
    # Renderizamos el HTML y le "inyectamos" la variable con los planos
    return render_template('index.html', lista_planos=planos_desde_bd)

if __name__ == '__main__':
    app.run(debug=True) # debug=True recarga el servidor si haces cambios