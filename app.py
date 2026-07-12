# Mi Inventario en Internet — Python + Streamlit + Neon
# ============================================================================
# APLICACIÓN WEB PARA GESTIÓN DE INVENTARIO
# ============================================================================
# Esta aplicación permite administrar un inventario de productos usando:
# - Streamlit: Framework para crear interfaces web interactivas con Python
# - SQLAlchemy: Biblioteca para interactuar con bases de datos
# - Neon: Base de datos PostgreSQL en la nube (almacena los datos)
# ============================================================================

import streamlit as st  # Importa Streamlit para crear la interfaz web
from sqlalchemy import text  # Importa text de SQLAlchemy para ejecutar consultas SQL

# Fondo azul suave personalizado
st.markdown("""
<style>
    /* Fondo azul suave para toda la aplicación */
    .stApp {
        background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 50%, #e0f2fe 100%);
    }
    
    /* Contenedor principal con fondo blanco semitransparente */
    .block-container {
        background-color: rgba(255, 255, 255, 0.85);
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Estilo para las pestañas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: bold;
    }
    
    /* Estilo para los selectbox */
    .stSelectbox label {
        font-weight: bold;
        color: #1e40af;
    }
    
    /* Estilo para los botones */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 24px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    }
    
    /* Estilo para los metric */
    [data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #3b82f6;
    }
    
    /* Estilo para el título */
    h1 {
        color: #1e40af !important;
    }
</style>
""", unsafe_allow_html=True)

# Configura el título de la aplicación (se muestra en la parte superior)
st.title("📦 Mi Inventario")

# Crea la conexión a la base de datos Neon usando la configuración en secrets.toml
# El parámetro "neon" debe coincidir con el nombre en [connections.neon]
# El parámetro type="sql" indica que es una conexión SQL
conexion = st.connection("neon", type="sql")


def ejecutar(sql, datos=None):
    """
    Función para ejecutar consultas SQL en la base de datos.
    
    Parámetros:
    - sql: Consulta SQL con marcadores de posición (:n, :p, :c, etc.)
    - datos: Diccionario con los valores para los marcadores de posición (opcional)
    
    Esta función:
    1. Abre una sesión con la base de datos
    2. Ejecuta la consulta SQL con los datos proporcionados
    3. Confirma los cambios (commit)
    4. La sesión se cierra automáticamente al salir del bloque 'with'
    """
    with conexion.session as s:  # Abre una sesión de base de datos
        s.execute(text(sql), datos)  # Ejecuta la consulta con los datos
        s.commit()  # Guarda los cambios en la base de datos


# Crea 4 pestañas en la interfaz para diferentes operaciones
# Cada pestaña contiene un conjunto diferente de controles y funcionalidades
pestana1, pestana2, pestana3, pestana4 = st.tabs(["👁️ Ver", "➕ Agregar", "✏️ Editar", "🗑️ Eliminar"])

# --- PESTAÑA 1: VER PRODUCTOS ---
# Esta pestaña muestra todos los productos almacenados en la base de datos
with pestana1:
    # Consulta todos los productos ordenados por ID (de menor a mayor)
    # El parámetro ttl=0 significa que no se cachea la consulta (siempre obtiene datos frescos)
    productos = conexion.query("SELECT * FROM productos ORDER BY id;", ttl=0)
    
    # Muestra los productos en una tabla interactiva
    # hide_index=True oculta la columna de índice numérico
    st.dataframe(productos, hide_index=True)
    
    # Muestra una métrica con el total de productos
    st.metric("📦 Total de productos", len(productos))

# --- PESTAÑA 2: AGREGAR PRODUCTO ---
# Esta pestaña permite agregar un nuevo producto al inventario
with pestana2:
    nombre = st.text_input("🏷️ Nombre del producto")
    precio = st.number_input("💲 Precio", min_value=0.0)
    stock = st.number_input("📊 Cantidad", min_value=0, step=1)
    
    if st.button("💾 Guardar"):
        ejecutar(
            "INSERT INTO productos (nombre, precio, stock) VALUES (:n, :p, :c);",
            {"n": nombre, "p": precio, "c": stock},
        )
        st.success("¡Producto guardado!")
        st.rerun()

# --- PESTAÑA 3: EDITAR PRODUCTO ---
# Esta pestaña permite modificar el precio y stock de un producto existente
with pestana3:
    productos = conexion.query("SELECT * FROM productos ORDER BY id;", ttl=0)
    lista = [f"🏷️ {fila.id} - {fila.nombre}" for fila in productos.itertuples()]
    
    if lista:
        elegido = st.selectbox("¿Cuál producto quieres cambiar?", lista)
        numero = int(elegido.split(" - ")[0])
        
        nuevo_precio = st.number_input("💲 Nuevo precio", min_value=0.0, key="np")
        nuevo_stock = st.number_input("📊 Nueva cantidad", min_value=0, step=1, key="nc")
        
        if st.button("🔄 Actualizar"):
            ejecutar(
                "UPDATE productos SET precio = :p, stock = :c WHERE id = :id;",
                {"p": nuevo_precio, "c": nuevo_stock, "id": numero},
            )
            st.success("¡Producto actualizado!")
            st.rerun()

# --- PESTAÑA 4: ELIMINAR PRODUCTO ---
# Esta pestaña permite eliminar un producto del inventario
with pestana4:
    productos = conexion.query("SELECT * FROM productos ORDER BY id;", ttl=0)
    lista = [f"🏷️ {fila.id} - {fila.nombre}" for fila in productos.itertuples()]
    
    if lista:
        elegido = st.selectbox("¿Cuál producto quieres borrar?", lista, key="borrar")
        numero = int(elegido.split(" - ")[0])
        
        if st.button("❌ Eliminar"):
            ejecutar("DELETE FROM productos WHERE id = :id;", {"id": numero})
            st.success("Producto eliminado.")
            st.rerun()
