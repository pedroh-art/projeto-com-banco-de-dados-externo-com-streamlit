# models/momento.py
import datetime
import uuid

def upload_momento(conn, file, descricao, integrante_id):
    """
    Faz o upload de uma imagem para o Storage e salva os dados na tabela 'momentos'.
    """
    try:
        # 1. Faz o upload do arquivo para o Supabase Storage
        bucket_name = "momentos_bucket"
        # Garante um nome de arquivo único usando um timestamp
        file_path = f"{uuid.uuid4()}.{file.name.split('.')[-1]}"
        
        # O método upload mudou para `upload` e o `file_options` não é mais necessário para upsert
        conn.storage.from_(bucket_name).upload(file=file.getvalue(), path=file_path)

        # 2. Pega a URL pública do arquivo que acabamos de subir
        res_url = conn.storage.from_(bucket_name).get_public_url(file_path)
        
        # 3. Insere os dados na tabela 'momentos'
        conn.table("momentos").insert({
            "descricao": descricao.strip(),
            "integrante_id": integrante_id,
            "url_imagem": res_url
        }).execute()
        
        return True
    except Exception as e:
        print(f"Erro ao fazer upload do momento: {e}")
        return False

def listar_momentos(conn):
    """
    Lista todos os momentos da equipe, com o nome do autor.
    """
    try:
        res = conn.table("momentos").select("*, integrantes(nome)").order("data_criacao", desc=True).execute()
        return res.data
    except Exception as e:
        print(f"Erro ao listar momentos: {e}")
        return []

def excluir_momento(conn, momento_id, url_imagem):
    """
    Exclui a imagem do Storage e o registro da tabela 'momentos'.
    """
    try:
        # 1. Extrai o nome do arquivo da URL para deletar do Storage
        bucket_name = "momentos_bucket"
        file_name = url_imagem.split(f"{bucket_name}/")[-1]
        conn.storage.from_(bucket_name).remove([file_name])
        
        # 2. Deleta o registro da tabela
        conn.table("momentos").delete().eq("id", momento_id).execute()
        return True
    except Exception as e:
        print(f"Erro ao excluir momento: {e}")
        return False