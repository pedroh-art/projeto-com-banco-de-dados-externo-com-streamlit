# models/tarefa.py

def criar_tarefa(conn, titulo, descricao, integrante_id, status="to_do"):
    try:
        conn.table("tarefas").insert({
            "titulo": titulo.strip(),
            "descricao": descricao.strip(),
            "status": status,
            "integrante_id": integrante_id
        }).execute()
        return True
    except Exception as e:
        raise e

def atualizar_status_tarefa(conn, tarefa_id, novo_status):
    try:
        conn.table("tarefas").update({"status": novo_status}).eq("id", tarefa_id).execute()
        return True
    except Exception as e:
        raise e

def excluir_tarefa(conn, tarefa_id):
    try:
        conn.table("tarefas").delete().eq("id", tarefa_id).execute()
        return True
    except Exception as e:
        raise e

def listar_tarefas_por_status(conn, status):
    try:
        # Supabase faz o join automaticamente se as chaves estrangeiras estiverem configuradas
        res = conn.table("tarefas").select("id, titulo, descricao, integrante_id, integrantes(nome)").eq("status", status).order("data_criacao").execute()
        tarefas = []
        for item in res.data:
            nome_integrante = item["integrantes"]["nome"] if item["integrantes"] else "Não atribuído"
            tarefas.append((item["id"], item["titulo"], item["descricao"], item["integrante_id"], nome_integrante))
        return tarefas
    except Exception as e:
        raise e

def obter_quadro_kanban(conn):
    try:
        res = conn.table("tarefas").select("status, titulo, descricao, integrantes(nome)").order("status").order("data_criacao").execute()
        quadro = []
        for item in res.data:
            nome_integrante = item["integrantes"]["nome"] if item["integrantes"] else "Não atribuído"
            quadro.append((item["status"], item["titulo"], item["descricao"], nome_integrante))
        return quadro
    except Exception as e:
        raise e