# services/regras_service.py
import json

# ID único para nosso conjunto de regras no banco de dados.
# Como teremos apenas um "documento" de regras, podemos usar um ID fixo.
REGRAS_ID = 1

def carregar_regras(conn):
    """
    Carrega as regras do banco de dados Supabase.
    Se não houver regras, retorna um dicionário vazio.
    """
    try:
        # Busca a linha na tabela 'regras' onde o id é REGRAS_ID
        res = conn.table("regras").select("conteudo").eq("id", REGRAS_ID).single().execute()
        if res.data and "conteudo" in res.data:
            return res.data["conteudo"]
        return {}
    except Exception as e:
        # Se der erro (ex: tabela vazia), retorna um dict vazio para não quebrar a app
        print(f"Aviso: Não foi possível carregar as regras do Supabase. {e}")
        return {}

def salvar_regras(conn, regras: dict):
    """
    Salva ou atualiza o dicionário `regras` no banco de dados Supabase.
    """
    try:
        # O método 'upsert' é perfeito aqui: ele insere se não existir, ou atualiza se já existir.
        conn.table("regras").upsert({
            "id": REGRAS_ID,
            "conteudo": regras
        }).execute()
        return True
    except Exception as e:
        print(f"Erro ao salvar regras no Supabase: {e}")
        return False