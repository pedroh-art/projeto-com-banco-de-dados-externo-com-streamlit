# services/__init__.py
# Pacote de serviços do sistema Dino-Tech

from .regras_service import carregar_regras, salvar_regras
from .agenda_service import obter_compromissos_agrupados
from .kanban_service import obter_kanban_agrupado

__all__ = [
    'carregar_regras',
    'salvar_regras',
    'obter_compromissos_agrupados',
    'obter_kanban_agrupado'
]