# database.py
from supabase import create_client
import streamlit as st

try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
except KeyError:
    st.error("Erro: As chaves SUPABASE_URL e SUPABASE_KEY não foram configuradas no secrets.toml.")
    st.stop()

supabase = create_client(url, key)