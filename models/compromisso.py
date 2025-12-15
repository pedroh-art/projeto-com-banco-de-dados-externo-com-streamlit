# models/compromisso.py

# Horários padrão (08:00 a 19:00)
HORARIOS_PADRAO = [f"{h:02d}:00" for h in range(8, 20)]

def criar_compromisso(conn, titulo, descricao, data, inicio, fim):
    try:
        conn.table("compromissos").insert({
            "titulo": titulo.strip(),
            "descricao": descricao.strip(),
            "data": str(data),
            "horario_inicio": inicio,
            "horario_fim": fim
        }).execute()
        return True
    except Exception as e:
        raise e

def listar_compromissos(conn):
    try:
        res = conn.table("compromissos").select("id, titulo, descricao, data, horario_inicio, horario_fim").order("data").order("horario_inicio").execute()
        return [tuple(item.values()) for item in res.data]
    except Exception as e:
        raise e

def atualizar_compromisso(conn, comp_id, titulo, descricao, data, inicio, fim):
    try:
        conn.table("compromissos").update({
            "titulo": titulo.strip(),
            "descricao": descricao.strip(),
            "data": str(data),
            "horario_inicio": inicio,
            "horario_fim": fim
        }).eq("id", comp_id).execute()
        return True
    except Exception as e:
        raise e

def excluir_compromisso(conn, comp_id):
    try:
        conn.table("compromissos").delete().eq("id", comp_id).execute()
        return True
    except Exception as e:
        raise e