# models/conhecimento.py
# Gerencia Wiki, Riscos e Treinamentos

# --- WIKI ---
def salvar_artigo_wiki(conn, titulo, conteudo, categoria, autor):
    try:
        conn.table("wiki_artigos").insert({
            "titulo": titulo, "conteudo": conteudo, 
            "categoria": categoria, "autor": autor
        }).execute()
        return True
    except Exception as e:
        print(e)
        return False

def listar_wiki(conn):
    try:
        return conn.table("wiki_artigos").select("*").order("created_at", desc=True).execute().data
    except:
        return []

def excluir_artigo_wiki(conn, artigo_id):
    try:
        conn.table("wiki_artigos").delete().eq("id", artigo_id).execute()
        return True
    except:
        return False

def salvar_decisao_estrategica(conn, decisao, alternativas, justificativa, autor):
    """Salva uma decisão estruturada na Wiki."""
    titulo = f"Decisão: {decisao}"
    conteudo = f"### 🎯 Decisão Tomada\n{decisao}\n\n### ❌ Alternativas Descartadas\n{alternativas}\n\n### ⚖️ Justificativa\n{justificativa}"
    return salvar_artigo_wiki(conn, titulo, conteudo, "Decisões Estratégicas", autor)

# --- RISCOS ---
def salvar_risco(conn, descricao, probabilidade, impacto, plano_mitigacao):
    try:
        conn.table("riscos").insert({
            "descricao": descricao,
            "probabilidade": probabilidade, # Alta, Média, Baixa
            "impacto": impacto,             # Alto, Médio, Baixo
            "plano_mitigacao": plano_mitigacao
        }).execute()
        return True
    except:
        return False

def listar_riscos(conn):
    try:
        return conn.table("riscos").select("*").execute().data
    except:
        return []

def excluir_risco(conn, id_risco):
    try:
        conn.table("riscos").delete().eq("id", id_risco).execute()
        return True
    except:
        return False

# --- TREINAMENTO ---
def salvar_topico_treino(conn, titulo, nivel, link_material):
    try:
        conn.table("treinamentos").insert({
            "titulo": titulo, "nivel": nivel, "link_material": link_material
        }).execute()
        return True
    except:
        return False

def listar_treinamentos(conn):
    try:
        return conn.table("treinamentos").select("*").order("nivel").execute().data
    except:
        return []

def salvar_progresso_treino(conn, treino_id, integrante_id, validado=False):
    """Registra ou valida o progresso de um treino."""
    try:
        conn.table("treino_progresso").upsert({
            "treino_id": treino_id, 
            "integrante_id": integrante_id, 
            "validado": validado
        }).execute()
        return True
    except:
        return False

def listar_progresso_treino(conn):
    try:
        return conn.table("treino_progresso").select("*").execute().data
    except:
        return []