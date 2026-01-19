def adicionar_item(conn, nome, preco):
    try:
        conn.table("itens").insert({
            "nome": nome.strip(),
            "preco": preco
        }).execute()
        return True
    except Exception as e:
        raise e
def excluir_item(conn, item_id):
    try:
        conn.table("itens").delete().eq("id", item_id).execute()
        return True
    except Exception as e:
        raise e
def listar_itens(conn):
    try:
        res = conn.table("itens").select("*").execute()
        return res.data
    except Exception as e:
        raise e
def total_preco(conn):
    try:
        res = conn.table("itens").select("preco").execute()
        total = sum(item["preco"] for item in res.data)
        return total
    except Exception as e:
        raise e
def totalizar_dinheiro_atual(conn):
    try:
        res = conn.table("dinheiro").select("dinheiro_atual").execute()
        if res.data:
            return res.data[0]["dinheiro_atual"]
        return 0.0
    except Exception as e:
        raise e    
def atualizar_dinheiro_atual(conn, novo_valor):
    try:
        res = conn.table("dinheiro").select("*").execute()
        if res.data:
            conn.table("dinheiro").update({
                "dinheiro_atual": novo_valor
            }).eq("id", res.data[0]["id"]).execute()
        else:
            conn.table("dinheiro").insert({
                "dinheiro_atual": novo_valor
            }).execute()
        return True
    except Exception as e:
        raise e
def registrar_transacao(conn, tipo, valor, descricao, data_transacao, item_id=None):
    try:
        # item_id é ignorado no insert pois a coluna não existe no banco
        payload = {
            "tipo": tipo,
            "valor": valor,
            "descricao": descricao,
            "data_criacao": data_transacao
        }
        conn.table("transacoes").insert(payload).execute()
        return True
    except Exception as e:
        raise e
def listar_transacoes(conn):
    try:
        res = conn.table("transacoes").select("*").order("id", desc=True).execute()
        return res.data
    except Exception as e:
        raise e       
def excluir_transacao(conn, transacao_id):
    try:
        conn.table("transacoes").delete().eq("id", transacao_id).execute()
        return True
    except Exception as e:
        raise e