# 🔭 Base de Datos de Planos - Nordic Optical Telescope (NOT)

Este repositorio contiene el entorno de desarrollo local dockerizado para la **Base de Datos de Planos** de la Asociación Científica del Telescopio Óptico Nórdico. El entorno cuenta con un servidor web basado en **Flask** y una base de datos **MariaDB** que se configuran e inicializan de forma completamente automática.

---

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado y activo en tu máquina:
1. **Docker Desktop** (Asegúrate de iniciar la aplicación y que el motor/daemon de Docker esté corriendo en verde).
2. **Git** (Para clonar y subir cambios).

---

## 🚀 1. Cómo Montar el Entorno Local

Para compilar las imágenes e inicializar el servidor local y la base de datos MariaDB juntos, sigue estos pasos:

1. Abre tu terminal (PowerShell, Command Prompt o Git Bash) en la carpeta raíz del proyecto (`c:\Coding\repository-drawings-database`).
2. Ejecuta el siguiente comando para construir y arrancar los contenedores en segundo plano:
   ```bash
   docker compose up --build -d
   ```
3. Docker descargará MariaDB, compilará el servidor de Python Flask, configurará los volúmenes de red y base de datos, y los levantará.
4. **Verificación de acceso web**:
   - 🇪🇸 **Versión en Español**: [http://localhost:5000/index-es.html](http://localhost:5000/index-es.html)
   - 🇬🇧 **Versión en Inglés**: [http://localhost:5000/index-en.html](http://localhost:5000/index-en.html)

> [!TIP]
> **Desarrollo en Tiempo Real (Hot-Reloading)**: Hemos configurado el volumen del servidor web apuntando a tu directorio local. Cualquier cambio que guardes en tus archivos locales de Python, HTML o CSS se actualizará automáticamente dentro de Docker sin necesidad de reiniciar nada.

---

## ⚙️ 2. ¿Dónde y Qué cambiar en las Configuraciones?

Si deseas cambiar las contraseñas, los puertos, el nombre de la base de datos o ajustar el comportamiento de los contenedores, esto es lo que debes modificar:

### A. Cambiar puertos, credenciales o volúmenes del sistema
Todo esto se edita en el archivo central **`docker-compose.yml`**:
*   **Puertos de Base de Datos**: Por defecto está en `- "3306:3306"`. Si tienes otra base de datos en tu ordenador local que ya use el puerto 3306, cámbialo a `- "3307:3306"` (el puerto de tu PC será el 3307).
*   **Credenciales de MariaDB**: Modifica las variables bajo `environment:` en la sección `db`:
    - `MARIADB_ROOT_PASSWORD` (Contraseña de superusuario root).
    - `MARIADB_DATABASE` (Nombre de la base de datos creada por defecto).
    - `MARIADB_USER` (Usuario estándar).
    - `MARIADB_PASSWORD` (Contraseña del usuario estándar).
*   *Nota*: Si cambias las credenciales del usuario o base de datos en el `db`, asegúrate de actualizar exactamente los mismos valores en la sección `environment:` de `web` para que el backend de Flask se pueda conectar correctamente.

### B. Ajustar el Servidor Web o Librerías
*   **Añadir paquetes de Python**: Si en el futuro necesitas usar una nueva librería de Python, añádela al archivo **`requirements.txt`** en la raíz y recompile con `docker compose up --build -d`.
*   **Dependencias de Compilación**: El archivo **`Dockerfile`** usa `python:3.11-slim` e instala paquetes del sistema como `gcc` y `libmariadb-dev`. No necesitas tocar este archivo a menos que quieras cambiar la versión base de Python o añadir software a nivel de sistema operativo en el servidor.

---

## 🔌 3. Cómo conectarte desde Clientes de Base de Datos (dbconnect / DBeaver)

Si utilizas un cliente de bases de datos gráfico externo en tu ordenador local (como la extensión **Database Client (dbconnect)** en VS Code, **DBeaver**, **HeidiSQL** o **MySQL Workbench**), puedes conectarte a la base de datos activa usando los siguientes parámetros:

| Parámetro | Valor a introducir | Observaciones |
| :--- | :--- | :--- |
| **Tipo de Conexión (Dialect)** | `MariaDB` o `MySQL` | Ambos funcionan de forma idéntica. |
| **Server/Host (IP)** | `localhost` o `127.0.0.1` | Apunta a tu máquina local. |
| **Port (Puerto)** | `3306` | El puerto que expusimos en `docker-compose.yml`. |
| **Database (Esquema)** | `planos_telescopio` | Nombre de la base de datos creada. |

### 🔐 Opciones de Credenciales de Acceso:

*   **Opción 1: Usuario Estándar (Recomendado)**
    - **User**: `db_user_drawings`
    - **Password**: `db_password_drawings_987`
*   **Opción 2: Administrador Root (Acceso Total)**
    - **User**: `root`
    - **Password**: `root_super_secret_pwd_991`

---

## 📥 4. Cómo Subir todos tus Datos (CSV) a la Base de Datos Local

Hemos creado un importador avanzado e inteligente en **`scripts/add.py`** que procesa cualquier archivo CSV o Excel exportado, limpia la base de datos local e inserta los datos. 

Como el script necesita compilar librerías específicas de bases de datos (que en Windows pueden requerir herramientas pesadas de desarrollo), **el script está optimizado para correr directamente dentro de tu contenedor web de Docker**.

### Paso 1: Colocar tu archivo CSV
Coloca tu archivo CSV en la carpeta `data` de tu proyecto y asegúrate de renombrarlo a `drive.csv`:
*   Ruta local en tu ordenador: `c:\Coding\repository-drawings-database\data\drive.csv`

### Paso 2: Ejecutar la importación
Abre tu terminal en la raíz del proyecto y ejecuta el siguiente comando:
```bash
docker compose exec web python scripts/add.py
```

---

### 🧠 ¿Cómo funciona la magia de importación de `add.py`?

El script fue diseñado con ingeniería de resiliencia avanzada:
1.  **Auto-Detección de Delimitador**: Lee el archivo y detecta de forma automática si los datos están separados por comas `,`, puntos y comas `;` o tabulaciones `\t` (común al copiar y pegar desde Excel).
2.  **Mapeo Inteligente de Columnas**: Analiza la fila de cabeceras y busca términos clave. Si las columnas de tu hoja de Excel se desordenan o añaden campos extra en el futuro, el script las mapea perfectamente de forma dinámica:
    -   *Código de Catálogo* ➜ Busca columnas con `planos` o `catalog`.
    -   *Nombre de Pieza* ➜ Busca columnas con `weight`, `piece` o `part`.
    -   *Material* ➜ Asocia automáticamente la columna `coating` o `material`.
    -   *Autor* ➜ Busca `dwg. date` o `author`.
    -   *Fecha* ➜ Mapea la columna de aprobación `appr.`.
    -   *Hipervínculo* ➜ Busca `comments`, `enlace` o `link`.
3.  **Migración de Esquema Dinámica**: Si ejecutas el script y tu tabla en MariaDB no cuenta todavía con la columna de hipervínculos `enlace`, el script realiza una alteración de tabla en caliente (`ALTER TABLE`) en segundos de forma transparente y continúa su trabajo sin colgarse.
4.  **Enlaces Interactivos en la Web**: Una vez importado, la web mostrará todos tus planos locales, y si algún plano incluye una URL en sus comentarios/comentarios de enlace, la columna de acción mostrará un botón de **"Ver Plano" / "View Drawing"** funcional que abrirá el hipervínculo en una pestaña nueva.

---

## 🛑 5. Comandos Útiles de Mantenimiento

*   **Ver logs de los contenedores en tiempo real**:
    ```bash
    docker compose logs -f
    ```
*   **Apagar el entorno local sin borrar datos**:
    ```bash
    docker compose stop
    ```
*   **Volver a encender tras haberlo apagado**:
    ```bash
    docker compose start
    ```
*   **Destruir el entorno por completo (útil si deseas reiniciar la base de datos desde cero)**:
    ```bash
    docker compose down -v
    ```
