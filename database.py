# database.py
import streamlit as st
from supabase import create_client, Client

def init_connection() -> Client:
    """
    Inicializa e retorna o cliente Supabase usando as credenciais
    armazenadas nos segredos do Streamlit.
    """
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

# Cria a instância do cliente que será importada por outros módulos
supabase = init_connection()