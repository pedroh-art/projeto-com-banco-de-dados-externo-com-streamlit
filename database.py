# database.py
import streamlit as st
from supabase import create_client, Client

def init_connection() -> Client:
    """
    Inicializa e retorna o cliente Supabase usando as credenciais
    armazenadas nos segredos do Streamlit.
    """
    url = st.secrets["supabase"]["url"]
    # SEGURANÇA: Use a chave 'service_role' no secrets.toml para que o app tenha permissão de admin.
    # Em seguida, bloqueie a escrita para a chave 'anon' nas políticas RLS do Supabase.
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

# Cria a instância do cliente que será importada por outros módulos
supabase = init_connection()