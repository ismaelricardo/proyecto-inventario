import streamlit as st
from sqlalchemy import text
import hashlib
import os

# ============================================================================
# CONFIGURACIÓN INICIAL
# ============================================================================
st.set_page_config(page_title="Mi Inventario", page_icon="📦", layout="wide")

# Fondo azul suave personalizado
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 50%, #e0f2fe 100%);
    }
    .block-container {
        background-color: rgba(255, 255, 255, 0.85);
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stSelectbox label {
        font-weight: bold;
        color: #1e40af;
    }
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
    [data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #3b82f6;
    }
    h1 {
        color: #1e40af !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CONEXIÓN A LA BASE DE DATOS
# ============================================================================
conexion = st.connection("neon", type="sql")


def ejecutar(sql, datos=None):
    with conexion.session as s:
        s.execute(text(sql), datos)
        s.commit()


# ============================================================================
# FUNCIONES DE AUTENTICACIÓN
# ============================================================================
def hashear_password(password):
    salt = "inventario_salt_2024"
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()


def crear_tabla_usuarios():
    ejecutar("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            nombre_completo VARCHAR(100) NOT NULL,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)


def registrar_usuario(username, password, nombre_completo):
    try:
        password_hash = hashear_password(password)
        ejecutar(
            "INSERT INTO usuarios (username, password, nombre_completo) VALUES (:u, :p, :n);",
            {"u": username, "p": password_hash, "n": nombre_completo},
        )
        return True
    except Exception:
        return False


def verificar_usuario(username, password):
    password_hash = hashear_password(password)
    resultado = conexion.query(
        "SELECT * FROM usuarios WHERE username = :u AND password = :p;",
        params={"u": username, "p": password_hash},
        ttl=0,
    )
    return len(resultado) > 0


def obtener_usuario(username):
    resultado = conexion.query(
        "SELECT * FROM usuarios WHERE username = :u;",
        params={"u": username},
        ttl=0,
    )
    if len(resultado) > 0:
        return resultado.iloc[0]
    return None


# ============================================================================
# INICIALIZAR SESIÓN Y TABLA
# ============================================================================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario = None

# Crear tabla de usuarios al iniciar
crear_tabla_usuarios()


# ============================================================================
# INTERFAZ DE LOGIN / REGISTRO
# ============================================================================
def mostrar_login():
    st.title("🔐 Inicio de Sesión")

    pestana_login, pestana_registro = st.tabs(["🔑 Iniciar Sesión", "📝 Registrarse"])

    with pestana_login:
        st.subheader("Ingresa tus credenciales")
        username = st.text_input("👤 Usuario", key="login_user")
        password = st.text_input("🔒 Contraseña", type="password", key="login_pass")

        if st.button("Entrar", key="btn_login"):
            if not username or not password:
                st.error("Por favor completa todos los campos.")
            elif verificar_usuario(username, password):
                st.session_state.autenticado = True
                st.session_state.usuario = username
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")

    with pestana_registro:
        st.subheader("Crea una cuenta nueva")
        nombre = st.text_input("📝 Nombre completo", key="reg_name")
        username_reg = st.text_input("👤 Usuario", key="reg_user")
        password_reg = st.text_input("🔒 Contraseña", type="password", key="reg_pass")
        password_confirm = st.text_input("🔒 Confirmar contraseña", type="password", key="reg_confirm")

        if st.button("Registrarse", key="btn_register"):
            if not nombre or not username_reg or not password_reg or not password_confirm:
                st.error("Por favor completa todos los campos.")
            elif password_reg != password_confirm:
                st.error("Las contraseñas no coinciden.")
            elif len(password_reg) < 4:
                st.error("La contraseña debe tener al menos 4 caracteres.")
            elif registrar_usuario(username_reg, password_reg, nombre):
                st.success("¡Cuenta creada! Ahora puedes iniciar sesión.")
            else:
                st.error("El usuario ya existe. Prueba con otro.")


def mostrar_inventario():
    usuario = obtener_usuario(st.session_state.usuario)

    col_titulo, col_usuario = st.columns([3, 1])
    with col_titulo:
        st.title("📦 Mi Inventario")
    with col_usuario:
        st.markdown(f"**👤 {usuario['nombre_completo']}**")
        if st.button("🚪 Cerrar Sesión"):
            st.session_state.autenticado = False
            st.session_state.usuario = None
            st.rerun()

    pestana1, pestana2, pestana3, pestana4 = st.tabs(["👁️ Ver", "➕ Agregar", "✏️ Editar", "🗑️ Eliminar"])

    with pestana1:
        productos = conexion.query("SELECT * FROM productos ORDER BY id;", ttl=0)
        st.dataframe(productos, hide_index=True)
        st.metric("📦 Total de productos", len(productos))

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

    with pestana3:
        productos = conexion.query("SELECT * FROM productos ORDER BY id;", ttl=0)
        lista = [f"🏷️ {fila.id} - {fila.nombre}" for fila in productos.itertuples()]

        if lista:
            elegido = st.selectbox("¿Cuál producto quieres cambiar?", lista)
            numero = int(elegido.split(" - ")[0].strip().split()[-1])

            nuevo_precio = st.number_input("💲 Nuevo precio", min_value=0.0, key="np")
            nuevo_stock = st.number_input("📊 Nueva cantidad", min_value=0, step=1, key="nc")

            if st.button("🔄 Actualizar"):
                ejecutar(
                    "UPDATE productos SET precio = :p, stock = :c WHERE id = :id;",
                    {"p": nuevo_precio, "c": nuevo_stock, "id": numero},
                )
                st.success("¡Producto actualizado!")
                st.rerun()

    with pestana4:
        productos = conexion.query("SELECT * FROM productos ORDER BY id;", ttl=0)
        lista = [f"🏷️ {fila.id} - {fila.nombre}" for fila in productos.itertuples()]

        if lista:
            elegido = st.selectbox("¿Cuál producto quieres borrar?", lista, key="borrar")
            numero = int(elegido.split(" - ")[0].strip().split()[-1])

            if st.button("❌ Eliminar"):
                ejecutar("DELETE FROM productos WHERE id = :id;", {"id": numero})
                st.success("Producto eliminado.")
                st.rerun()


# ============================================================================
# FLUJO PRINCIPAL
# ============================================================================
if st.session_state.autenticado:
    mostrar_inventario()
else:
    mostrar_login()
