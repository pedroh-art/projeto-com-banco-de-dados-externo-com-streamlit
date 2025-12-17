# models/missao.py

def criar_missao(conn, nome, pontuacao, descricao):
    """Cria uma nova missão do tapete."""
    try:
        conn.table("missoes_tapete").insert({
            "nome": nome.strip(),
            "pontuacao": pontuacao,
            "descricao": descricao.strip()
        }).execute()
        return True
    except Exception as e:
        print(f"Erro ao criar missão: {e}")
        return False

def listar_missoes(conn):
    """Lista todas as missões, ordenadas por pontuação decrescente."""
    try:
        res = conn.table("missoes_tapete").select("*").order("pontuacao", desc=True).execute()
        return res.data if res.data else []
    except Exception as e:
        print(f"Erro ao listar missões: {e}")
        return []

def atualizar_missao(conn, missao_id, nome, pontuacao, descricao):
    """Atualiza os dados de uma missão."""
    try:
        conn.table("missoes_tapete").update({
            "nome": nome.strip(),
            "pontuacao": pontuacao,
            "descricao": descricao.strip()
        }).eq("id", missao_id).execute()
        return True
    except Exception as e:
        print(f"Erro ao atualizar missão: {e}")
        return False

def atualizar_status_missao(conn, missao_id, novo_status):
    """Atualiza o status de uma missão."""
    try:
        conn.table("missoes_tapete").update({"status": novo_status}).eq("id", missao_id).execute()
        return True
    except Exception as e:
        print(f"Erro ao atualizar status da missão: {e}")
        return False

def excluir_missao(conn, missao_id):
    """Exclui uma missão do inventário."""
    try:
        conn.table("missoes_tapete").delete().eq("id", missao_id).execute()
        return True
    except Exception as e:
        print(f"Erro ao excluir missão: {e}")
        return False