# models/core_values.py
import datetime

def registrar_avaliacao_cv(conn, dados, autor_id):
    """Salva a autoavaliação dos Core Values."""
    try:
        dados['autor_id'] = autor_id
        dados['data_registro'] = datetime.datetime.now().isoformat()
        conn.table("core_values_avaliacao").insert(dados).execute()
        return True
    except Exception as e:
        print(f"Erro ao salvar avaliação CV: {e}")
        return False

def listar_avaliacoes_cv(conn):
    """Lista todas as avaliações para relatórios."""
    try:
        res = conn.table("core_values_avaliacao").select("*").order("data_registro", desc=True).execute()
        return res.data
    except Exception as e:
        return []

def registrar_atividade_cv(conn, atividade, data, participantes, aprendizado, autor_id):
    """Registra uma atividade no Diário de Bordo."""
    try:
        payload = {
            "atividade": atividade,
            "data_atividade": str(data),
            "participantes": participantes, # Supabase guarda array ou string dependendo da config
            "aprendizado": aprendizado,
            "autor_id": autor_id
        }
        conn.table("core_values_log").insert(payload).execute()
        return True
    except Exception as e:
        print(f"Erro ao registrar atividade CV: {e}")
        return False

def listar_atividades_cv(conn):
    try:
        res = conn.table("core_values_log").select("*").order("data_atividade", desc=True).execute()
        return res.data
    except Exception as e:
        return []

def atualizar_atividade_cv(conn, id_atividade, atividade, data, participantes, aprendizado):
    """Atualiza uma atividade de Core Values existente."""
    try:
        conn.table("core_values_log").update({
            "atividade": atividade,
            "data_atividade": str(data),
            "participantes": participantes,
            "aprendizado": aprendizado
        }).eq("id", id_atividade).execute()
        return True
    except Exception as e:
        print(f"Erro ao atualizar atividade CV: {e}")
        return False

def excluir_atividade_cv(conn, atividade_id):
    """Exclui uma atividade de Core Values."""
    try:
        conn.table("core_values_log").delete().eq("id", atividade_id).execute()
        return True
    except Exception as e:
        print(f"Erro ao excluir atividade CV: {e}")
        return False

def excluir_avaliacao_cv(conn, avaliacao_id):
    """Exclui uma avaliação de Core Values."""
    try:
        conn.table("core_values_avaliacao").delete().eq("id", avaliacao_id).execute()
        return True
    except Exception as e:
        print(f"Erro ao excluir avaliação CV: {e}")
        return False

def registrar_conflito_cv(conn, resumo, solucao, autor_id):
    """Registra uma resolução de conflito."""
    try:
        payload = {
            "resumo": resumo,
            "solucao": solucao,
            "autor_id": autor_id,
            "data_registro": datetime.datetime.now().isoformat()
        }
        conn.table("core_values_conflitos").insert(payload).execute()
        return True
    except Exception as e:
        print(f"Erro ao registrar conflito: {e}")
        return False

def listar_conflitos_cv(conn):
    try:
        res = conn.table("core_values_conflitos").select("*, integrantes(nome)").order("data_registro", desc=True).execute()
        return res.data
    except Exception as e:
        return []

def excluir_conflito_cv(conn, conflito_id):
    """Exclui um registro de conflito."""
    try:
        conn.table("core_values_conflitos").delete().eq("id", conflito_id).execute()
        return True
    except Exception as e:
        print(f"Erro ao excluir conflito: {e}")
        return False