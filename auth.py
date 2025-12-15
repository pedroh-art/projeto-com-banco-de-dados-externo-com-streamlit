# auth.py
import streamlit as st
import bcrypt
from database import supabase

def login_usuario(usuario, senha):
    try:
        res = supabase.table("usuarios").select("*").eq("usuario", usuario).execute()
        if not res.data:
            return None
        
        user = res.data[0]

        # Garante que 'user' é um dicionário e tem a chave 'senha' antes de usar.
        if isinstance(user, dict) and "senha" in user:
            stored_hash = user["senha"].encode('latin1')
            if bcrypt.checkpw(senha.encode('utf-8'), stored_hash):
                return (user.get("usuario"), user.get("tipo"))
        
        return None # Retorna None se o usuário não for encontrado ou a senha estiver incorreta.
    except Exception as e:
        st.error(f"Erro no login: {e}")
        return None

def initialize_session_state():
    if "usuario_logado" not in st.session_state:
        st.session_state.usuario_logado = None
        st.session_state.tipo_usuario = None

def is_admin():
    return st.session_state.tipo_usuario == "administrador"