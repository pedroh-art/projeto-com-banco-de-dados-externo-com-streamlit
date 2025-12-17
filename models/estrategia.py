# models/estrategia.py
import uuid

def salvar_base_robo(conn, nome, descricao, foto_file):
    """Salva ou atualiza as informações da base do robô."""
    try:
        foto_url = None
        if foto_file:
            bucket_name = "estrategias_bucket"
            file_path = f"base_robo/{uuid.uuid4()}.{foto_file.name.split('.')[-1]}"
            conn.storage.from_(bucket_name).upload(file=foto_file.getvalue(), path=file_path)
            foto_url = conn.storage.from_(bucket_name).get_public_url(file_path)

        # Verifica se já existe uma base para fazer update, senão insert
        # Usaremos o ID=1 como um identificador fixo para a única entrada da base do robô.
        # Isso simplifica a lógica para sempre atualizar a mesma linha.
        base_id = 1
        dados = {"nome_base": nome, "descricao": descricao}
        if foto_url:
            dados["foto_url"] = foto_url

        # Adiciona o ID aos dados para o upsert funcionar corretamente
        dados["id"] = base_id

        # A função upsert irá inserir a linha com id=1 se ela não existir,
        # ou atualizar a linha existente com id=1. É mais robusta que a lógica anterior.
        conn.table("estrategia_base").upsert(dados).execute()

        return True
    except Exception as e:
        print(f"Erro ao salvar base do robô: {e}")
        return False

def obter_base_robo(conn):
    """Obtém as informações da base do robô."""
    try:
        res = conn.table("estrategia_base").select("*").maybe_single().execute()
        # Adiciona uma verificação para garantir que res e res.data existam
        if res and hasattr(res, 'data'):
            return res.data
        return None
    except Exception as e:
        print(f"Erro ao obter base do robô: {e}")
        return None

def excluir_base_robo(conn):
    """Exclui a base do robô e sua foto associada do armazenamento."""
    try:
        base_id = 1
        # Primeiro, busca a URL da foto para poder excluí-la do Storage
        res = conn.table("estrategia_base").select("foto_url").eq("id", base_id).maybe_single().execute()

        if res and res.data and res.data.get("foto_url"):
            foto_url = res.data["foto_url"]
            bucket_name = "estrategias_bucket"
            # Extrai o caminho do arquivo a partir da URL pública
            file_path = foto_url.split(f"{bucket_name}/")[-1]
            if file_path:
                conn.storage.from_(bucket_name).remove([file_path])

        # Em seguida, exclui o registro da tabela do banco de dados
        conn.table("estrategia_base").delete().eq("id", base_id).execute()
        return True
    except Exception as e:
        print(f"Erro ao excluir base do robô: {e}")
        return False

def adicionar_acessorio(conn, nome, descricao, missao_id, foto_file):
    """Adiciona um novo acessório a uma missão."""
    try:
        foto_url = None
        if foto_file:
            bucket_name = "estrategias_bucket"
            file_path = f"acessorios/{uuid.uuid4()}.{foto_file.name.split('.')[-1]}"
            conn.storage.from_(bucket_name).upload(file=foto_file.getvalue(), path=file_path)
            foto_url = conn.storage.from_(bucket_name).get_public_url(file_path)

        conn.table("acessorios").insert({
            "nome": nome,
            "descricao": descricao,
            "missao_id": missao_id,
            "foto_url": foto_url
        }).execute()
        return True
    except Exception as e:
        print(f"Erro ao adicionar acessório: {e}")
        return False

def listar_acessorios_por_missao(conn):
    """Lista todos os acessórios, agrupados por missão."""
    try:
        res = conn.table("acessorios").select("*, missoes_tapete(nome)").order("missao_id").execute()
        return res.data if res.data else []
    except Exception as e:
        print(f"Erro ao listar acessórios: {e}")
        return []

def excluir_acessorio(conn, acessorio_id):
    """Exclui um acessório."""
    try:
        conn.table("acessorios").delete().eq("id", acessorio_id).execute()
        return True
    except Exception as e:
        print(f"Erro ao excluir acessório: {e}")
        return False