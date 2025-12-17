# models/votacao.py
from collections import defaultdict

def criar_votacao(conn, titulo, opcoes, tipo_votacao='anonima'):
    """Cria uma nova votação com suas opções."""
    try:
        # Insere a votação e obtém o ID
        res_votacao = conn.table("votacoes").insert({
            "titulo": titulo,
            "tipo_votacao": tipo_votacao,
            "status": "aberta"
        }).execute()
        
        if not res_votacao.data:
            return False

        votacao_id = res_votacao.data[0]['id']
        
        # Insere as opções
        opcoes_para_inserir = [
            {"votacao_id": votacao_id, "texto_opcao": opt.strip()}
            for opt in opcoes if opt.strip()
        ]
        if not opcoes_para_inserir:
            # Se não houver opções válidas, remove a votação criada
            conn.table("votacoes").delete().eq("id", votacao_id).execute()
            return False

        conn.table("opcoes_votacao").insert(opcoes_para_inserir).execute()
        return True
    except Exception as e:
        print(f"Erro ao criar votação: {e}")
        return False

def listar_votacoes_com_status(conn):
    """Lista todas as votações com seu status e opções."""
    try:
        res = conn.table("votacoes").select("*, opcoes_votacao(*)").order("data_criacao", desc=True).execute()
        return res.data if res.data else []
    except Exception as e:
        print(f"Erro ao listar votações: {e}")
        return []

def atualizar_status_votacao(conn, votacao_id, novo_status):
    """Atualiza o status de uma votação (aberta/fechada)."""
    try:
        conn.table("votacoes").update({"status": novo_status}).eq("id", votacao_id).execute()
        return True
    except Exception as e:
        print(f"Erro ao atualizar status da votação: {e}")
        return False

def excluir_votacao(conn, votacao_id):
    """Exclui uma votação e todos os seus dados relacionados (opções, votos)."""
    try:
        conn.table("votacoes").delete().eq("id", votacao_id).execute()
        return True
    except Exception as e:
        print(f"Erro ao excluir votação: {e}")
        return False

def obter_resultados(conn, votacao_id):
    """Obtém os resultados de uma votação, contando os votos por opção."""
    try:
        # Pega todas as opções da votação
        res_opcoes = conn.table("opcoes_votacao").select("id, texto_opcao").eq("votacao_id", votacao_id).execute()
        if not res_opcoes.data:
            return {}

        # Inicializa o contador de resultados com todas as opções tendo 0 votos
        resultados = {opt['texto_opcao']: 0 for opt in res_opcoes.data}
        
        # Pega todos os votos para a votação
        res_votos = conn.table("votos").select("opcao_id").eq("votacao_id", votacao_id).execute()
        if not res_votos.data:
            return resultados

        # Mapeia opcao_id para texto_opcao
        map_id_para_texto = {opt['id']: opt['texto_opcao'] for opt in res_opcoes.data}

        # Conta os votos
        for voto in res_votos.data:
            texto_da_opcao = map_id_para_texto.get(voto['opcao_id'])
            if texto_da_opcao:
                resultados[texto_da_opcao] += 1
        
        return resultados
    except Exception as e:
        print(f"Erro ao obter resultados: {e}")
        return {}

def obter_resultados_detalhados(conn, votacao_id):
    """Obtém os resultados detalhados de uma votação não anônima, mostrando quem votou em quê."""
    try:
        # Pega todos os votos com os nomes dos integrantes e o texto das opções
        res = conn.table("votos").select("integrantes(nome), opcoes_votacao(texto_opcao)").eq("votacao_id", votacao_id).execute()
        if not res.data:
            return {}

        # Agrupa os votantes por opção
        resultados_detalhados = defaultdict(list)
        for voto in res.data:
            nome_integrante = voto.get("integrantes", {}).get("nome", "Desconhecido")
            texto_opcao = voto.get("opcoes_votacao", {}).get("texto_opcao", "Opção inválida")
            resultados_detalhados[texto_opcao].append(nome_integrante)
        
        return dict(resultados_detalhados)
    except Exception as e:
        print(f"Erro ao obter resultados detalhados: {e}")
        return {}

def verificar_voto_integrante(conn, votacao_id, integrante_id):
    """Verifica se um integrante já votou em uma votação específica."""
    try:
        res = conn.table("votos").select("id").eq("votacao_id", votacao_id).eq("integrante_id", integrante_id).execute()
        return bool(res.data)
    except Exception as e:
        print(f"Erro ao verificar voto: {e}")
        return False

def registrar_voto(conn, votacao_id, opcao_id, integrante_id):
    """Registra o voto de um integrante em uma opção."""
    try:
        # Verifica se já não votou
        if verificar_voto_integrante(conn, votacao_id, integrante_id):
            return False, "Você já votou nesta enquete."

        conn.table("votos").insert({
            "votacao_id": votacao_id,
            "opcao_id": opcao_id,
            "integrante_id": integrante_id
        }).execute()
        return True, "Voto registrado com sucesso!"
    except Exception as e:
        print(f"Erro ao registrar voto: {e}")
        return False, "Ocorreu um erro ao registrar seu voto."