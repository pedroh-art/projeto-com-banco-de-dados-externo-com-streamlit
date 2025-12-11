# app.py
import streamlit as st
from database import init_db
from auth import initialize_session_state, login_usuario, is_admin
from services.regras_service import carregar_regras
from views import render_membro_view, render_admin_view

# Inicialização
initialize_session_state()
try:
    regras = carregar_regras()
except Exception as e:
    st.error(str(e))
    st.stop()

conn = init_db()

# ==============================================================================
# 🔐 TELA DE LOGIN
# ==============================================================================
if st.session_state.usuario_logado is None:
    st.set_page_config(page_title="Login - Dino-Tech", layout="centered")
    st.markdown("<h1 style='text-align:center; color:#FFD700;'>🔐 Login - Dino-Tech</h1>", unsafe_allow_html=True)
    with st.form("login_form"):
        usuario = st.text_input("Usuário", key="login_usuario")
        senha = st.text_input("Senha", type="password", key="login_senha")
        submit = st.form_submit_button("Entrar")
    
    if submit:
        resultado = login_usuario(conn, usuario, senha)
        if resultado:
            st.session_state.usuario_logado, st.session_state.tipo_usuario = resultado
            st.rerun()
        else:
            st.error("❌ Usuário ou senha inválidos.")
    
    
    st.stop()

# ==============================================================================
# 👥 VISÃO DO MEMBRO
# ==============================================================================
if not is_admin():
    render_membro_view(conn, regras, st.session_state.usuario_logado)
    st.stop()

# ==============================================================================
# 👑 VISÃO DO ADMINISTRADOR
# ==============================================================================
render_admin_view(conn, regras)