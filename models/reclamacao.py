# models/reclamacao.py
import datetime

def criar_reclamacao(conn, texto, integrante_id):
    """
    Cria uma nova reclamação no banco de dados, associada a um integrante.
    """
    try:
        conn.table("reclamacoes").insert({
            "texto": texto.strip(),
            "status": "nova",
            "data_criacao": datetime.datetime.now().isoformat(),
            "integrante_id": integrante_id
        }).execute()
        return True
    except Exception as e:
        print(f"Erro ao criar reclamação: {e}")
        return False

def listar_reclamacoes(conn):
    """
    Lista todas as reclamações, incluindo o nome do autor, ordenando pela data de criação.
    """
    try:
        # O join é feito automaticamente pelo Supabase se a chave estrangeira estiver configurada
        res = conn.table("reclamacoes").select("*, integrantes(nome)").order("data_criacao", desc=True).execute()
        
        reclamacoes_com_autor = []
        for rec in res.data:
            # Garante que o nome do autor seja tratado corretamente
            if rec.get("integrante_id") is None:
                rec["autor"] = "Anônimo"
            elif rec.get("integrantes") and rec["integrantes"].get("nome"):
                rec["autor"] = rec["integrantes"]["nome"]
            else:
                rec["autor"] = "Autor desconhecido (usuário removido)"
            reclamacoes_com_autor.append(rec)
            
        return reclamacoes_com_autor
    except Exception as e:
        print(f"Erro ao listar reclamações: {e}")
        return []

def marcar_reclamacao_como_lida(conn, reclamacao_id):
    """
    Atualiza o status de uma reclamação para 'lida'.
    """
    try:
        conn.table("reclamacoes").update({"status": "lida"}).eq("id", reclamacao_id).execute()
        return True
    except Exception as e:
        print(f"Erro ao marcar reclamação como lida: {e}")
        return False

def excluir_reclamacao(conn, reclamacao_id):
    """
    Remove uma reclamação do banco de dados.
    """
    try:
        conn.table("reclamacoes").delete().eq("id", reclamacao_id).execute()
        return True
    except Exception as e:
        print(f"Erro ao excluir reclamação: {e}")
        return False