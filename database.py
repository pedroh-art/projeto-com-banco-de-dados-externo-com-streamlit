# database.py
import streamlit as st
from supabase import create_client, Client

def init_connection() -> Client:
    """
    Inicializa e retorna o cliente Supabase usando as credenciais
    armazenadas nos segredos do Streamlit.
    """
    try:
        url = st.secrets["supabase"]["url"]
        # SEGURANÇA: Use a chave 'service_role' no secrets.toml para que o app tenha permissão de admin.
        # Em seguida, bloqueie a escrita para a chave 'anon' nas políticas RLS do Supabase.
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except FileNotFoundError:
        st.error("❌ Arquivo de segredos não encontrado. Crie o arquivo `.streamlit/secrets.toml` com as credenciais do Supabase.")
        st.stop()
    except KeyError:
        st.error("❌ Credenciais do Supabase incompletas no `secrets.toml`.")
        st.stop()

# Cria a instância do cliente que será importada por outros módulos
supabase = init_connection()