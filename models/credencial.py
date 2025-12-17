# models/credencial.py

def criar_credencial(conn, servico, usuario, senha):
    """Cria uma nova credencial no banco de dados."""
    try:
        conn.table("credenciais").insert({
            "servico": servico,
            "usuario": usuario,
            "senha": senha
        }).execute()
        return True
    except Exception as e:
        print(f"Erro ao criar credencial: {e}")
        return False

def listar_credenciais(conn):
    """Lista todas as credenciais cadastradas, ordenadas por serviço."""
    try:
        res = conn.table("credenciais").select("*").order("servico").execute()
        return res.data if res.data else []
    except Exception as e:
        print(f"Erro ao listar credenciais: {e}")
        return []

def excluir_credencial(conn, credencial_id):
    """Exclui uma credencial pelo seu ID."""
    try:
        conn.table("credenciais").delete().eq("id", credencial_id).execute()
        return True
    except Exception as e:
        print(f"Erro ao excluir credencial: {e}")
        return False