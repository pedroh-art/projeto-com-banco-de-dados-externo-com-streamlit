# models/projeto_inovacao.py
import uuid

def obter_dados_pi(conn):
    """Obtém todos os dados do Projeto de Inovação."""
    try:
        res = conn.table("projeto_inovacao").select("*").eq("id", 1).maybe_single().execute()
        return res.data if res and hasattr(res, 'data') else None
    except Exception as e:
        print(f"Erro ao obter dados do PI: {e}")
        return None

def salvar_dados_pi(conn, dados):
    """Salva ou atualiza os dados textuais do Projeto de Inovação."""
    try:
        dados['id'] = 1 # Garante que sempre estamos atualizando a mesma linha
        conn.table("projeto_inovacao").upsert(dados).execute()
        return True
    except Exception as e:
        print(f"Erro ao salvar dados do PI: {e}")
        return False

def adicionar_arquivo_pi(conn, nome, descricao, arquivo_file):
    """Faz upload de um arquivo e o associa ao Projeto de Inovação."""
    try:
        url_arquivo = None
        if arquivo_file:
            bucket_name = "pi_bucket"
            file_path = f"{uuid.uuid4()}_{arquivo_file.name}"
            conn.storage.from_(bucket_name).upload(file=arquivo_file.getvalue(), path=file_path)
            url_arquivo = conn.storage.from_(bucket_name).get_public_url(file_path)

        conn.table("pi_arquivos").insert({
            "nome_arquivo": nome,
            "descricao": descricao,
            "url_arquivo": url_arquivo
        }).execute()
        return True
    except Exception as e:
        print(f"Erro ao adicionar arquivo ao PI: {e}")
        return False

def listar_arquivos_pi(conn):
    """Lista todos os arquivos associados ao Projeto de Inovação."""
    try:
        res = conn.table("pi_arquivos").select("*").order("data_criacao", desc=True).execute()
        return res.data if res.data else []
    except Exception as e:
        print(f"Erro ao listar arquivos do PI: {e}")
        return []

def excluir_arquivo_pi(conn, arquivo_id, url_arquivo):
    """Exclui um arquivo do Storage e do banco de dados."""
    try:
        # Exclui do Storage
        if url_arquivo:
            bucket_name = "pi_bucket"
            file_path = url_arquivo.split(f"{bucket_name}/")[-1]
            if file_path:
                conn.storage.from_(bucket_name).remove([file_path])
        
        # Exclui do banco de dados
        conn.table("pi_arquivos").delete().eq("id", arquivo_id).execute()
        return True
    except Exception as e:
        print(f"Erro ao excluir arquivo do PI: {e}")
        return False