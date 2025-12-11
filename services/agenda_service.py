# services/agenda_service.py
import datetime
from collections import defaultdict
from models.compromisso import listar_compromissos

def obter_compromissos_agrupados(conn):
    """
    Retorna compromissos agrupados por data, em ordem cronológica.
    Formato: { "2025-07-25": [ (titulo, descricao, inicio, fim), ... ] }
    """
    compromissos = listar_compromissos(conn)
    agrupado = defaultdict(list)
    
    for _, titulo, descricao, data, inicio, fim in compromissos:
        agrupado[data].append((titulo, descricao, inicio, fim))
    
    # Ordenar por data
    return dict(sorted(agrupado.items()))