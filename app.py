# app.py
import streamlit as st
from auth import initialize_session_state, login_usuario, is_admin
from database import supabase as conn
from services.regras_service import carregar_regras
from views import render_membro_view, render_admin_view
from views.shared_components import LOGO_DINO_TECH
initialize_session_state()

try:
    regras = carregar_regras(conn)
except Exception as e:
    st.error(str(e))
    st.stop()

if st.session_state.usuario_logado is None:
    st.set_page_config(page_title="Login - Dino-Tech", page_icon="🦖", layout="centered")
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        body {
            background-color: #0E1117;
            font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
        }
        .stApp {
            background-image: radial-gradient(at 50% 50%, rgba(125, 42, 232, 0.1) 0%, transparent 80%);
        }
        .main .block-container {
            max-width: 450px;
            padding: 3rem 2rem;
            background: #1E1E1E; /* Card de login escuro */
            border-radius: 24px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.08);
        }
        .login-title {
            font-size: 2rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 0.5rem;
            background: linear-gradient(135deg, #00C4CC 0%, #7D2AE8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .login-subtitle {
            text-align: center;
            color: #A0A0A0;
            margin-bottom: 2rem;
            font-size: 0.95rem;
        }
        /* Garante que os labels e inputs do login sejam visíveis */
        .stTextInput label, .stTextInput input {
            color: #E0E0E0 !important;
        }
        .stTextInput > div > div > input {
            border: 1px solid #4A4A4A;
            background-color: #262730;
            color: white;
            padding: 10px 15px;
        }
        .stButton > button {
            width: 100%;
            border-radius: 12px;
            background: linear-gradient(135deg, #00C4CC 0%, #7D2AE8 100%);
            color: white;
            font-weight: 600;
            padding: 0.7rem;
            border: none;
            box-shadow: 0 4px 12px rgba(125, 42, 232, 0.2);
        }
        .stButton > button:hover {
            box-shadow: 0 6px 16px rgba(125, 42, 232, 0.3);
            transform: translateY(-1px);
        }
        </style>
        
        """,
        unsafe_allow_html=True
    )
    st.markdown(f"""<div style="text-align: center; margin-bottom: 1rem;">
            <img src="{LOGO_DINO_TECH}" alt="Dino-Tech Logo" width="200" style="filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));">
        </div>
        <div class="login-title">Bem-vindo de volta</div>
        <div class="login-subtitle">Acesse o Banco de Dados da Dino-Tech</div>""", unsafe_allow_html=True)
    with st.form("login_form"):
        usuario = st.text_input("Usuário", key="login_usuario")
        senha = st.text_input("Senha", type="password", key="login_senha")
        submit = st.form_submit_button("Entrar")
    if submit:
        resultado = login_usuario(usuario, senha)
        if resultado:
            st.session_state.usuario_logado, st.session_state.tipo_usuario = resultado
            st.rerun()
        else:
            st.error("❌ Usuário ou senha inválidos.")
    st.stop()

if not is_admin():
    render_membro_view(conn, regras, st.session_state.usuario_logado)
else:
    render_admin_view(conn, regras)