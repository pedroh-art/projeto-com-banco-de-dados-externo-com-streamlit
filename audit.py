import datetime

def registrar_log(conn, usuario, acao, detalhes=None):
    """
    Registra uma ação sensível no sistema para auditoria.
    """
    try:
        conn.table("audit_logs").insert({
            "usuario": usuario,
            "acao": acao,
            "detalhes": detalhes,
            "timestamp": datetime.datetime.now().isoformat()
        }).execute()
        return True
    except Exception as e:
        print(f"Falha ao registrar log de auditoria: {e}")
        return False

def listar_logs(conn, limite=50):
    try:
        return conn.table("audit_logs").select("*").order("timestamp", desc=True).limit(limite).execute().data
    except:
        return []

def limpar_logs(conn):
    """Remove todos os logs de auditoria."""
    try:
        conn.table("audit_logs").delete().neq("id", -1).execute()
        return True
    except Exception as e:
        print(f"Erro ao limpar logs: {e}")
        return False