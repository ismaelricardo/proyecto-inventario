# Mi Inventario

Aplicación web para gestión de inventario de productos, desarrollada con Python y Streamlit, conectada a una base de datos PostgreSQL en Neon.

## Tecnologías

- **Python** — Lenguaje de programación
- **Streamlit** — Framework para crear interfaces web interactivas
- **SQLAlchemy** — Biblioteca para interactuar con bases de datos
- **Neon** — Base de datos PostgreSQL en la nube
- **psycopg2** — Adaptador PostgreSQL para Python

## Requisitos

- Python 3.9 o superior
- Cuenta en [Neon](https://neon.tech) con una base de datos creada

## Instalación

1. Clonar o descargar el proyecto:

```bash
git clone <url-del-repositorio>
cd proyecto-inventario
```

2. Instalar las dependencias:

```bash
pip install -r requirements.txt
```

3. Configurar la conexión a la base de datos en `.streamlit/secrets.toml` con tus credenciales de Neon:

```toml
[connections.neon]
url = "postgresql+psycopg2://USUARIO:CONTRASENA@TU-HOST/neondb?sslmode=require"
```

## Ejecutar la aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá en el navegador en `http://localhost:8501`.

## Estructura del proyecto

```
proyecto-inventario/
├── app.py                  # Código principal de la aplicación
├── requirements.txt        # Dependencias del proyecto
├── .gitignore              # Archivos ignorados por Git
├── README.md               # Este archivo
└── .streamlit/
    └── secrets.toml        # Configuración de conexión a la base de datos
```

## Base de datos

La tabla `productos` debe tener la siguiente estructura:

```sql
CREATE TABLE productos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    precio DECIMAL(10, 2) NOT NULL,
    stock INTEGER NOT NULL
);
```

## Funcionalidades

- **Ver productos** — Lista todos los productos con su precio y stock
- **Agregar producto** — Crea un nuevo producto en el inventario
- **Editar producto** — Modifica el precio y stock de un producto existente
- **Eliminar producto** — Borra un producto del inventario
