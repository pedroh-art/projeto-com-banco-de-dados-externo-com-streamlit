# models/planejamento.py

# --- ROADMAP ---
def criar_marco(conn, titulo, data_limite, status="pendente"):
    try:
        conn.table("roadmap_marcos").insert({
            "titulo": titulo, "data_limite": str(data_limite), "status": status
        }).execute()
        return True
    except Exception:
        return False

def listar_marcos(conn):
    try:
        res = conn.table("roadmap_marcos").select("*").order("data_limite").execute()
        return res.data
    except Exception:
        return []

def atualizar_status_marco(conn, id_marco, novo_status):
    try:
        conn.table("roadmap_marcos").update({"status": novo_status}).eq("id", id_marco).execute()
        return True
    except Exception:
        return False

def excluir_marco(conn, id_marco):
    try:
        conn.table("roadmap_marcos").delete().eq("id", id_marco).execute()
        return True
    except Exception:
        return False

# --- SCRIPTS DE APRESENTAÇÃO ---
def salvar_roteiro(conn, tipo, conteudo):
    """Salva ou atualiza o roteiro (tipo: 'robo', 'pi', 'core')."""
    try:
        # Verifica se já existe
        res = conn.table("apresentacao_scripts").select("id").eq("tipo", tipo).execute()
        if res.data:
            conn.table("apresentacao_scripts").update({"conteudo": conteudo}).eq("tipo", tipo).execute()
        else:
            conn.table("apresentacao_scripts").insert({"tipo": tipo, "conteudo": conteudo}).execute()
        return True
    except Exception as e:
        print(e)
        return False

def obter_roteiro(conn, tipo):
    try:
        res = conn.table("apresentacao_scripts").select("conteudo").eq("tipo", tipo).maybe_single().execute()
        return res.data['conteudo'] if res.data else ""
    except Exception:
        return ""

def salvar_avaliacao_treino(conn, tipo_apresentacao, tempo, nota_clareza, nota_equipe, obs):
    try:
        conn.table("treinos_log").insert({
            "tipo": tipo_apresentacao, "tempo": tempo, "clareza": nota_clareza, "equipe": nota_equipe, "obs": obs
        }).execute()
        return True
    except Exception as e:
        print(f"Erro ao salvar avaliação treino: {e}")
        return False

def listar_avaliacoes_treino(conn):
    try:
        res = conn.table("treinos_log").select("*").order("created_at", desc=True).execute()
        return res.data if res.data else []
    except Exception:
        return []

def excluir_avaliacao_treino(conn, avaliacao_id):
    try:
        conn.table("treinos_log").delete().eq("id", avaliacao_id).execute()
        return True
    except Exception:
        return False