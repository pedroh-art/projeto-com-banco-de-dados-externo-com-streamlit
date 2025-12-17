# models/codigo.py
import uuid

def salvar_codigo(conn, nome, descricao, codigo, missao_id, video_file, codigo_id=None):
    """Cria ou atualiza um código na biblioteca."""
    try:
        dados = {
            "nome": nome,
            "descricao": descricao,
            "codigo": codigo,
            "missao_id": missao_id
        }

        if video_file:
            bucket_name = "codigos_bucket"
            file_path = f"{uuid.uuid4()}.{video_file.name.split('.')[-1]}"
            conn.storage.from_(bucket_name).upload(file=video_file.getvalue(), path=file_path)
            dados["video_url"] = conn.storage.from_(bucket_name).get_public_url(file_path)

        if codigo_id:
            # Atualiza um código existente
            conn.table("codigos_robo").update(dados).eq("id", codigo_id).execute()
        else:
            # Cria um novo código
            conn.table("codigos_robo").insert(dados).execute()
        
        return True
    except Exception as e:
        print(f"Erro ao salvar código: {e}")
        return False

def listar_codigos_com_missao(conn):
    """Lista todos os códigos, incluindo o nome da missão associada."""
    try:
        res = conn.table("codigos_robo").select("*, missoes_tapete(nome)").order("data_atualizacao", desc=True).execute()
        return res.data if res.data else []
    except Exception as e:
        print(f"Erro ao listar códigos: {e}")
        return []

def excluir_codigo(conn, codigo_id):
    """Exclui um código e seu vídeo associado."""
    try:
        # Primeiro, busca a URL do vídeo para poder excluí-lo do Storage
        res = conn.table("codigos_robo").select("video_url").eq("id", codigo_id).maybe_single().execute()

        if res and res.data and res.data.get("video_url"):
            video_url = res.data["video_url"]
            bucket_name = "codigos_bucket"
            # Extrai o caminho do arquivo a partir da URL pública
            file_path = video_url.split(f"{bucket_name}/")[-1]
            if file_path:
                try:
                    conn.storage.from_(bucket_name).remove([file_path])
                except Exception as storage_error:
                    # Continua mesmo se o arquivo não for encontrado no storage
                    print(f"Aviso: erro ao remover vídeo do storage (pode já ter sido removido): {storage_error}")

        # Em seguida, exclui o registro da tabela do banco de dados
        conn.table("codigos_robo").delete().eq("id", codigo_id).execute()
        return True
    except Exception as e:
        print(f"Erro ao excluir código: {e}")
        return False