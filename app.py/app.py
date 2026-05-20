from flask import Flask, render_template
import mariadb
import sys
import os
import csv

app = Flask(__name__, template_folder='../webapp', static_folder='../webapp')

def get_project_structure():
    tree = {
        'T00': {'name': '2.5m Telescope', 'children': {}},
        'A00': {'name': 'Telescope Adaptor', 'children': {}},
        'X00': {'name': 'Building', 'children': {}},
        'W00': {'name': 'Weather Station', 'children': {}},
        'FM00': {'name': 'Filter Mechanism', 'children': {}},
    }
    
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'drive.csv')
    if not os.path.exists(csv_path):
        return tree
        
    with open(csv_path, encoding='utf-8') as f:
        reader = csv.reader(f)
        try:
            next(reader)
            next(reader)
        except StopIteration:
            pass
            
        for row in reader:
            if len(row) < 4:
                continue
            code = row[2].strip()
            name = row[3].strip()
            if not code:
                continue
                
            parts = code.split('.')
            
            root_key = None
            first_letter = parts[0][0].upper()
            if first_letter == 'T': root_key = 'T00'
            elif first_letter == 'A': root_key = 'A00'
            elif first_letter == 'X': root_key = 'X00'
            elif first_letter == 'W': root_key = 'W00'
            elif code.startswith('FM'): root_key = 'FM00'
            
            if not root_key:
                root_key = parts[0]
                if root_key not in tree:
                    tree[root_key] = {'name': name if len(parts)==1 else '', 'children': {}}

            current = tree[root_key]['children']
            for i, part in enumerate(parts):
                full_code = '.'.join(parts[:i+1])
                
                if full_code == root_key:
                    break
                    
                if full_code not in current:
                    current[full_code] = {'name': name if i == len(parts)-1 else full_code, 'children': {}}
                elif i == len(parts) - 1:
                    if name:
                        current[full_code]['name'] = name
                
                current = current[full_code]['children']
                
    return tree

# Función para conectar a la base de datos
def conectar_bd():
    try:
        conexion = mariadb.connect(
            user=os.environ.get("DB_USER", "tu_usuario"),      # Cambia esto por tu usuario de MariaDB
            password=os.environ.get("DB_PASSWORD", "tu_password"), # Cambia esto por tu contraseña
            host=os.environ.get("DB_HOST", "localhost"),
            port=int(os.environ.get("DB_PORT", 3306)),
            database=os.environ.get("DB_NAME", "planos_telescopio")
        )
        return conexion
    except mariadb.Error as e:
        print(f"Error conectando a MariaDB: {e}")
        return None

# Ruta principal de la web
@app.route('/')
@app.route('/index-es.html')
def inicio():
    conexion = conectar_bd()
    planos_desde_bd = []
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        consulta = """
            SELECT catalog_code, piece_name, material, author_initials, author_date, enlace 
            FROM drawings 
            LIMIT 100
        """
        try:
            cursor.execute(consulta)
            planos_desde_bd = cursor.fetchall()
        except mariadb.Error as e:
            print(f"Error en la consulta: {e}")
        finally:
            conexion.close()
    
    estructura = get_project_structure()
    return render_template('index-es.html', lista_planos=planos_desde_bd, estructura=estructura)

@app.route('/index-en.html')
def inicio_en():
    conexion = conectar_bd()
    planos_desde_bd = []
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        consulta = """
            SELECT catalog_code, piece_name, material, author_initials, author_date, enlace 
            FROM drawings 
            LIMIT 100
        """
        try:
            cursor.execute(consulta)
            planos_desde_bd = cursor.fetchall()
        except mariadb.Error as e:
            print(f"Error en la consulta: {e}")
        finally:
            conexion.close()
    
    estructura = get_project_structure()
    return render_template('index-en.html', lista_planos=planos_desde_bd, estructura=estructura)

if __name__ == '__main__':
    app.run(debug=True)