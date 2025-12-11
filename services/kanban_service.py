# services/kanban_service.py
from collections import defaultdict
from models.tarefa import listar_tarefas_por_status

def obter_kanban_agrupado(conn):
    """
    Retorna o quadro Kanban agrupado por status.
    Formato: {
        "to_do": [ (id, titulo, descricao, integrante_id, nome_resp), ... ],
        "doing": [ ... ],
        "done": [ ... ]
    }
    """
    kanban = {
        "to_do": listar_tarefas_por_status(conn, "to_do"),
        "doing": listar_tarefas_por_status(conn, "doing"),
        "done": listar_tarefas_por_status(conn, "done")
    }
    return kanban