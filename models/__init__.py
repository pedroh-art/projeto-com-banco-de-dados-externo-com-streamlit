# models/__init__.py
# Pacote de modelos do sistema Dino-Tech

# Facilita imports diretos como:
# from models import integrante, tarefa, compromisso

from .integrante import (
    cadastrar_integrante,
    listar_integrantes,
    cadastrar_login_membro,
    atribuir_setor_funcao,
    listar_atribuicoes,
    remover_atribuicao,
    remover_integrante_completo,
    contar_atribuidos_por_funcao,
    contar_total_integrantes,
    contar_setores_unicos_por_integrante,
    contar_total_funcoes_por_integrante
)

from .tarefa import (
    criar_tarefa,
    atualizar_status_tarefa,
    excluir_tarefa,
    listar_tarefas_por_status,
    obter_quadro_kanban
)

from .compromisso import (
    criar_compromisso,
    listar_compromissos,
    atualizar_compromisso,
    excluir_compromisso
)
from .reclamacao import (
    criar_reclamacao,
    listar_reclamacoes,
    marcar_reclamacao_como_lida,
    excluir_reclamacao
)
from .momento import (
    upload_momento,
    listar_momentos,
    excluir_momento
)


__all__ = [
    # Integrante
    'cadastrar_integrante', 'listar_integrantes', 'cadastrar_login_membro',
    'atribuir_setor_funcao', 'listar_atribuicoes', 'remover_atribuicao',
    'remover_integrante_completo', 'contar_atribuidos_por_funcao',
    'contar_total_integrantes', 'contar_setores_unicos_por_integrante',
    'contar_total_funcoes_por_integrante',
    
    # Tarefa
    'criar_tarefa', 'atualizar_status_tarefa', 'excluir_tarefa',
    'listar_tarefas_por_status', 'obter_quadro_kanban',
    
    # Compromisso
    'criar_compromisso', 'listar_compromissos', 'atualizar_compromisso', 'excluir_compromisso',

    # Reclamação
    'criar_reclamacao', 'listar_reclamacoes', 'marcar_reclamacao_como_lida', 'excluir_reclamacao'
,
    # Momentos
    'upload_momento', 'listar_momentos', 'excluir_momento'
]