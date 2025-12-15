# models/integrante.py
import bcrypt
import secrets
import string

def cadastrar_integrante(conn, nome):
    try:
        nome = nome.strip()
        if not nome:
            raise ValueError("O nome não pode estar vazio.")
        conn.table("integrantes").insert({"nome": nome}).execute()
        return True
    except Exception as e:
        raise e

def listar_integrantes(conn):
    try:
        res = conn.table("integrantes").select("id, nome").order("nome").execute()
        return [(item['id'], item['nome']) for item in res.data]
    except Exception as e:
        raise e

def gerar_senha_forte(tamanho=12):
    """Gera uma senha aleatória segura com letras, números e símbolos."""
    if tamanho < 8:
        tamanho = 8
    caracteres = string.ascii_letters + string.digits + "!@#$%&*"
    senha = ''.join(secrets.choice(caracteres) for _ in range(tamanho))
    return senha

def cadastrar_login_membro(conn, nome):
    """
    Cria login (baseado no nome) e senha forte aleatória para um novo membro.
    """
    if not nome or not nome.strip():
        raise ValueError("Nome inválido para criação de login.")
    
    usuario = nome.strip().replace(" ", "_").lower()
    senha = gerar_senha_forte(tamanho=12)  # ✅ Senha forte!
    senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
    
    try:
        # Verifica se o usuário já existe
        res = conn.table("usuarios").select("id", count='exact').eq("usuario", usuario).execute()
        if res.count > 0:
            print(f"⚠️ Usuário '{usuario}' já existe. Login NÃO criado.")
            return None, None
        
        # Insere o novo usuário
        conn.table("usuarios").insert({"usuario": usuario, "senha": senha_hash.decode('latin1'), "tipo": "membro"}).execute()
        print(f"✅ Login criado: {usuario} | Senha: {senha}")
        return usuario, senha  # retorna a senha forte gerada
        
    except Exception as e:
        print(f"❌ Erro inesperado ao criar login '{usuario}': {e}")
        raise
def atribuir_setor_funcao(conn, integrante_id, setor, funcao):
    try:
        conn.table("atribuicoes").insert({
            "integrante_id": integrante_id, "setor": setor, "funcao": funcao
        }).execute()
        return True
    except Exception as e:
        raise e

def listar_atribuicoes(conn, integrante_id):
    try:
        res = conn.table("atribuicoes").select("setor, funcao").eq("integrante_id", integrante_id).execute()
        return [(item['setor'], item['funcao']) for item in res.data]
    except Exception as e:
        raise e

def remover_atribuicao(conn, integrante_id, setor, funcao):
    try:
        conn.table("atribuicoes").delete().match(
            {"integrante_id": integrante_id, "setor": setor, "funcao": funcao}
        ).execute()
        return True
    except Exception as e:
        raise e

def remover_integrante_completo(conn, integrante_id):
    """Remove o integrante e seu login associado (tabela 'usuarios')."""
    try:
        # Primeiro, obtém o nome do integrante para encontrar o usuário
        res = conn.table("integrantes").select("nome").eq("id", integrante_id).maybe_single().execute()
        if not res.data:
            return False
        nome = res.data["nome"]
        usuario = nome.strip().replace(" ", "_").lower()

        # Remove da tabela 'atribuicoes' (opcional, mas recomendado)
        conn.table("atribuicoes").delete().eq("integrante_id", integrante_id).execute()
        
        # Remove da tabela 'integrantes'
        conn.table("integrantes").delete().eq("id", integrante_id).execute()
        
        # 🔥 Remove da tabela 'usuarios'
        conn.table("usuarios").delete().eq("usuario", usuario).execute()
        return True
    except Exception as e:
        raise e

def contar_atribuidos_por_funcao(conn, setor, funcao):
    try:
        res = conn.table("atribuicoes").select("id", count='exact').eq("setor", setor).eq("funcao", funcao).execute()
        return res.count
    except Exception as e:
        raise e

def contar_total_integrantes(conn):
    try:
        res = conn.table("integrantes").select("id", count='exact').execute()
        return res.count
    except Exception as e:
        raise e

def contar_setores_unicos_por_integrante(conn, integrante_id):
    try:
        res = conn.table("atribuicoes").select("setor").eq("integrante_id", integrante_id).execute()
        if res.data:
            # Conta os setores únicos no lado do cliente (Python)
            return len({item['setor'] for item in res.data})
        return 0
    except Exception as e:
        raise e

def contar_total_funcoes_por_integrante(conn, integrante_id):
    try:
        res = conn.table("atribuicoes").select("id", count='exact').eq("integrante_id", integrante_id).execute()
        return res.count
    except Exception as e:
        raise e