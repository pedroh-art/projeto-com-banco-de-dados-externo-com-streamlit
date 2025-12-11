# auth.py
import streamlit as st
import sqlite3
import bcrypt

def login_usuario(conn, usuario, senha):
    """
    Autentica um usuário no banco de dados.
    Retorna (usuario, tipo) ou None se inválido.
    """
    try:
        c = conn.cursor()
        c.execute("SELECT usuario, tipo, senha FROM usuarios WHERE usuario = ?", (usuario,))
        resultado = c.fetchone()
        if resultado:
            usuario_db, tipo, senha_hash = resultado
            if bcrypt.checkpw(senha.encode('utf-8'), senha_hash):
                return (usuario_db, tipo)
        return None
    except Exception as e:
        st.error(f"Erro ao fazer login: {e}")
        return None

def initialize_session_state():
    """Inicializa as variáveis de sessão do Streamlit."""
    if "usuario_logado" not in st.session_state:
        st.session_state.usuario_logado = None
        st.session_state.tipo_usuario = None

def is_admin():
    """Verifica se o usuário logado é administrador."""
    return st.session_state.tipo_usuario == "administrador"