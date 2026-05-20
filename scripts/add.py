import os
import sys
import csv
import mariadb

def detect_delimiter(file_path):
    """Detects if the file is tab, semicolon, or comma separated."""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        first_line = f.readline()
        if '\t' in first_line:
            return '\t'
        elif ';' in first_line:
            return ';'
        else:
            return ','

def parse_and_upload(csv_path):
    if not os.path.exists(csv_path):
        print(f"❌ Error: El archivo CSV en '{csv_path}' no existe.")
        return

    # Detect delimiter
    delimiter = detect_delimiter(csv_path)
    print(f"🔍 Delimitador detectado: '{repr(delimiter)}'")

    # Read CSV
    with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f, delimiter=delimiter)
        try:
            headers = next(reader)
        except StopIteration:
            print("❌ Error: El archivo CSV está vacío.")
            return

        # Lowercase and strip headers for clean matching
        headers_clean = [h.strip().lower() for h in headers]
        print(f"📋 Cabeceras encontradas ({len(headers_clean)}): {headers}")

        # Dynamic Column Mapping
        col_catalog = -1
        col_piece = -1
        col_material = -1
        col_author = -1
        col_date = -1
        col_enlace = -1

        # Match columns by keywords (flexible matching for custom spreadsheets)
        for idx, h in enumerate(headers_clean):
            if "planos" in h or "catalog" in h:
                col_catalog = idx
            elif "weight" in h or "piece" in h or "part" in h:
                col_piece = idx
            elif "coating" in h:
                col_material = idx
            elif "dwg. date" in h:
                col_author = idx
            elif h == "appr.":
                col_date = idx
            elif "comment" in h or "enlace" in h or "link" in h:
                col_enlace = idx

        # Fallbacks if keywords not found
        if col_catalog == -1: col_catalog = 1
        if col_piece == -1: col_piece = 2
        if col_material == -1: col_material = 8
        if col_author == -1: col_author = 11
        if col_date == -1: col_date = 12
        if col_enlace == -1: col_enlace = 18

        print(f"⚙️ Mapeo de columnas dinámico:")
        print(f"   - Código Catálogo: Columna {col_catalog} ('{headers[col_catalog]}')")
        print(f"   - Nombre Pieza: Columna {col_piece} ('{headers[col_piece]}')")
        print(f"   - Material (Coating): Columna {col_material} ('{headers[col_material]}')")
        print(f"   - Autor (Dwg Date): Columna {col_author} ('{headers[col_author]}')")
        print(f"   - Fecha (Appr): Columna {col_date} ('{headers[col_date]}')")
        print(f"   - Enlace: Columna {col_enlace} ('{headers[col_enlace]}')")

        # Database Connection details (matching docker-compose)
        db_user = os.environ.get("DB_USER", "db_user_drawings")
        db_password = os.environ.get("DB_PASSWORD", "db_password_drawings_987")
        db_host = os.environ.get("DB_HOST", "localhost")
        db_port = int(os.environ.get("DB_PORT", 3306))
        db_name = os.environ.get("DB_NAME", "planos_telescopio")

        print(f"🔌 Conectando a MariaDB en {db_host}:{db_port}...")
        try:
            conn = mariadb.connect(
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port,
                database=db_name
            )
            cursor = conn.cursor()
            print("✅ Conexión establecida con éxito.")

            # dynamic schema migration: check if enlace column exists, create it if missing
            cursor.execute("SHOW COLUMNS FROM drawings LIKE 'enlace'")
            col_exists = cursor.fetchone()
            if not col_exists:
                print("🔧 Columna 'enlace' no detectada en la tabla. Migrando esquema de base de datos...")
                cursor.execute("ALTER TABLE drawings ADD COLUMN enlace VARCHAR(500) NULL")
                print("✅ Columna 'enlace' añadida con éxito.")

            # Truncate old table entries to avoid duplicate bloat
            cursor.execute("TRUNCATE TABLE drawings")
            print("🧹 Tabla 'drawings' vaciada con éxito para evitar duplicados.")

            # Insert rows
            inserted_count = 0
            for row_idx, row in enumerate(reader, start=2):
                if not row or len(row) < 2:
                    continue
                
                # Extract values with safe bounds
                catalog_code = row[col_catalog].strip() if col_catalog < len(row) else ""
                piece_name = row[col_piece].strip() if col_piece < len(row) else ""
                material = row[col_material].strip() if col_material < len(row) else ""
                author_initials = row[col_author].strip() if col_author < len(row) else ""
                author_date = row[col_date].strip() if col_date < len(row) else ""
                enlace = row[col_enlace].strip() if col_enlace < len(row) else ""

                # Skip header repetitions or empty rows
                if not catalog_code or catalog_code.lower() == "planos (hipervinculo)" or catalog_code.lower() == "code":
                    continue

                # Insert into DB
                cursor.execute(
                    """
                    INSERT INTO drawings (catalog_code, piece_name, material, author_initials, author_date, enlace)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (catalog_code, piece_name, material, author_initials, author_date, enlace if enlace else None)
                )
                inserted_count += 1

            conn.commit()
            cursor.close()
            conn.close()
            print(f"🎉 ¡Éxito! Se han importado {inserted_count} planos correctamente a la base de datos.")

        except mariadb.Error as e:
            print(f"❌ Error de MariaDB: {e}")

if __name__ == "__main__":
    csv_file = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "data", "drive.csv")
    print(f"📂 Iniciando importación desde: {csv_file}")
    parse_and_upload(csv_file)
