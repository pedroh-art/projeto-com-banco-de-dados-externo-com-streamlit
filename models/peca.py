# models/peca.py

def registrar_peca(conn, nome, quantidade):
    """Registra uma nova peça no inventário."""
    try:
        conn.table("pecas").insert({
            "nome": nome.strip(),
            "quantidade": quantidade
        }).execute()
        return True
    except Exception as e:
        print(f"Erro ao registrar peça: {e}")
        return False

def listar_pecas(conn):
    """Lista todas as peças do inventário, ordenadas por nome."""
    try:
        res = conn.table("pecas").select("*").order("nome").execute()
        return res.data if res.data else []
    except Exception as e:
        print(f"Erro ao listar peças: {e}")
        return []

def atualizar_quantidade_peca(conn, peca_id, nova_quantidade):
    """Atualiza a quantidade de uma peça existente."""
    try:
        conn.table("pecas").update({"quantidade": nova_quantidade}).eq("id", peca_id).execute()
        return True
    except Exception as e:
        print(f"Erro ao atualizar quantidade da peça: {e}")
        return False

def excluir_peca(conn, peca_id):
    """Exclui uma peça do inventário."""
    try:
        conn.table("pecas").delete().eq("id", peca_id).execute()
        return True
    except Exception as e:
        print(f"Erro ao excluir peça: {e}")
        return False