# models/acompanhamento.py

# --- Funções para Checklist da Competição ---

def listar_itens_checklist(conn):
    try:
        res = conn.table("checklist_competicao").select("*, integrantes(nome)").order("id").execute()
        return res.data if res.data else []
    except Exception as e:
        print(f"Erro ao listar itens do checklist: {e}")
        return []

def adicionar_item_checklist(conn, texto, responsavel_id):
    try:
        conn.table("checklist_competicao").insert({
            "item_texto": texto,
            "responsavel_id": responsavel_id
        }).execute()
        return True
    except Exception as e:
        print(f"Erro ao adicionar item ao checklist: {e}")
        return False

def atualizar_status_checklist(conn, item_id, status):
    try:
        conn.table("checklist_competicao").update({"status": status}).eq("id", item_id).execute()
        return True
    except Exception as e:
        print(f"Erro ao atualizar status do checklist: {e}")
        return False

def excluir_item_checklist(conn, item_id):
    try:
        conn.table("checklist_competicao").delete().eq("id", item_id).execute()
        return True
    except Exception as e:
        print(f"Erro ao excluir item do checklist: {e}")
        return False

# --- Funções para Registro de Reuniões ---

def listar_reunioes(conn):
    try:
        res = conn.table("reunioes").select("*").order("data_reuniao", desc=True).execute()
        return res.data if res.data else []
    except Exception as e:
        print(f"Erro ao listar reuniões: {e}")
        return []

def registrar_reuniao(conn, data, pauta, participantes, decisoes):
    try:
        conn.table("reunioes").insert({
            "data_reuniao": str(data),
            "pauta": pauta,
            "participantes": participantes,
            "decisoes": decisoes
        }).execute()
        return True
    except Exception as e:
        print(f"Erro ao registrar reunião: {e}")
        return False

def excluir_reuniao(conn, reuniao_id):
    try:
        conn.table("reunioes").delete().eq("id", reuniao_id).execute()
        return True
    except Exception as e:
        print(f"Erro ao excluir reunião: {e}")
        return False

# --- Funções para Lista de Erros e Soluções ---

def listar_erros_solucoes(conn):
    try:
        res = conn.table("erros_solucoes").select("*, integrantes(nome)").order("data_ocorrido", desc=True).execute()
        return res.data if res.data else []
    except Exception as e:
        print(f"Erro ao listar erros e soluções: {e}")
        return []

def registrar_erro_solucao(conn, erro, solucao, responsavel_id, data):
    try:
        conn.table("erros_solucoes").insert({
            "erro_descricao": erro,
            "solucao_aplicada": solucao,
            "responsavel_id": responsavel_id,
            "data_ocorrido": str(data)
        }).execute()
        return True
    except Exception as e:
        print(f"Erro ao registrar erro/solução: {e}")
        return False

def excluir_erro_solucao(conn, erro_id):
    try:
        conn.table("erros_solucoes").delete().eq("id", erro_id).execute()
        return True
    except Exception as e:
        print(f"Erro ao excluir erro/solução: {e}")
        return False

# --- Funções para Próximos Passos ---
# (As funções para esta seção podem ser reutilizadas do módulo de tarefas ou criadas de forma similar)
# Por simplicidade, vamos omitir por enquanto e focar nas outras três.
# Se necessário, posso adicionar `listar_passos`, `adicionar_passo`, `atualizar_passo`, `excluir_passo`.