# utils/pushbullet_util.py
try:
    from pushbullet import Pushbullet
except ImportError:
    raise ImportError("Instale o Pushbullet: pip install pushbullet.py")

def enviar_kanban_pushbullet(tarefas, token):
    """
    Envia o quadro Kanban atual via Pushbullet.
    Retorna (sucesso: bool, mensagem: str)
    """
    if not token or not token.strip():
        return False, "Token do Pushbullet não fornecido."

    try:
        pb = Pushbullet(token.strip())
        
        kanban = {"to_do": [], "doing": [], "done": []}
        for status, titulo, desc, nome in tarefas:
            kanban[status].append({
                "titulo": titulo,
                "descricao": desc or "",
                "responsavel": nome or "Não atribuído"
            })

        msg = "📋Quadro Kanban-Dino-Tech\n\n"
        nomes_colunas = {
            "to_do": "📝 A Fazer",
            "doing": "🔄 Fazendo",
            "done": "✅ Feito"
        }
        for status_key, nome_col in nomes_colunas.items():
            msg += f"\n{nome_col}\n"
            if not kanban[status_key]:
                msg += "- Nenhuma tarefa\n"
            else:
                for t in kanban[status_key]:
                    msg += f"- {t['titulo']} (Responsável ou Responsáveis:({t['responsavel']})\n)"
                    if t['descricao']:
                        msg += f"  > {t['descricao']}\n"

        pb.push_note("Kanban Atualizado", msg)
        return True, "Quadro enviado com sucesso via Pushbullet!"
    
    except Exception as e:
        return False, f"Erro ao enviar Pushbullet: {e}"