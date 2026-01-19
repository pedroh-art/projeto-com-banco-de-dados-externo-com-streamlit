import datetime

def registrar_round(conn, pontuacao_total, video_url, notas, missoes_status, versao_robo="v1.0"):
    """
    Registra um round de treino completo.
    missoes_status: dict { 'nome_missao': 'sucesso' | 'falha' | 'parcial' }
    """
    try:
        # 1. Salva o Round Geral
        data_round = {
            "data_hora": datetime.datetime.now().isoformat(),
            "pontuacao_total": pontuacao_total,
            "video_url": video_url,
            "notas": notas,
            "versao_robo": versao_robo
        }
        res = conn.table("robo_rounds").insert(data_round).execute()
        round_id = res.data[0]['id']

        # 2. Salva o status de cada missão nesse round
        detalhes = []
        for missao, status in missoes_status.items():
            detalhes.append({
                "round_id": round_id,
                "missao_nome": missao,
                "status": status
            })
        
        if detalhes:
            conn.table("robo_round_missoes").insert(detalhes).execute()
            
        return True
    except Exception as e:
        print(f"Erro ao registrar round: {e}")
        return False

def obter_dados_rounds(conn):
    """Retorna histórico de rounds."""
    try:
        return conn.table("robo_rounds").select("*").order("data_hora", desc=True).execute().data
    except:
        return []

def obter_estatisticas_missoes(conn):
    """Retorna dados para cálculo de taxa de sucesso."""
    try:
        # Retorna todas as execuções de missões para processamento no Pandas
        return conn.table("robo_round_missoes").select("*").execute().data
    except:
        return []