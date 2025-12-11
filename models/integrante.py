# models/integrante.py
import sqlite3
import bcrypt
import secrets
import string
def cadastrar_integrante(conn, nome):
    try:
        nome = nome.strip()
        if not nome:
            raise ValueError("O nome não pode estar vazio.")
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO integrantes (nome) VALUES (?)", (nome,))
        conn.commit()
        return True
    except Exception as e:
        raise e

def listar_integrantes(conn):
    try:
        c = conn.cursor()
        return c.execute("SELECT id, nome FROM integrantes ORDER BY nome").fetchall()
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
        c = conn.cursor()
        # Verifica se o usuário já existe
        c.execute("SELECT 1 FROM usuarios WHERE usuario = ?", (usuario,))
        if c.fetchone():
            print(f"⚠️ Usuário '{usuario}' já existe. Login NÃO criado.")
            return None, None
        
        # Insere o novo usuário
        c.execute(
            "INSERT INTO usuarios (usuario, senha, tipo) VALUES (?, ?, ?)",
            (usuario, senha_hash, "membro")
        )
        conn.commit()
        print(f"✅ Login criado: {usuario} | Senha: {senha}")
        return usuario, senha  # retorna a senha forte gerada
        
    except sqlite3.IntegrityError as e:
        print(f"❌ Erro de integridade ao criar login '{usuario}': {e}")
        return None, None
    except Exception as e:
        print(f"❌ Erro inesperado ao criar login '{usuario}': {e}")
        raise
def atribuir_setor_funcao(conn, integrante_id, setor, funcao):
    try:
        c = conn.cursor()
        c.execute("INSERT INTO atribuicoes (integrante_id, setor, funcao) VALUES (?, ?, ?)",
                  (integrante_id, setor, funcao))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return True
    except Exception as e:
        raise e

def listar_atribuicoes(conn, integrante_id):
    try:
        c = conn.cursor()
        return c.execute("SELECT setor, funcao FROM atribuicoes WHERE integrante_id=?", (integrante_id,)).fetchall()
    except Exception as e:
        raise e

def remover_atribuicao(conn, integrante_id, setor, funcao):
    try:
        c = conn.cursor()
        c.execute("DELETE FROM atribuicoes WHERE integrante_id=? AND setor=? AND funcao=?",
                  (integrante_id, setor, funcao))
        conn.commit()
        return True
    except Exception as e:
        raise e

def remover_integrante_completo(conn, integrante_id):
    """
    Remove o integrante e seu login associado (tabela 'usuarios').
    """
    try:
        c = conn.cursor()
        
        # Primeiro, obtém o nome do integrante para encontrar o usuário
        c.execute("SELECT nome FROM integrantes WHERE id = ?", (integrante_id,))
        resultado = c.fetchone()
        if not resultado:
            return False
        nome = resultado[0]
        usuario = nome.strip().replace(" ", "_").lower()

        # Remove da tabela 'atribuicoes' (opcional, mas recomendado)
        c.execute("DELETE FROM atribuicoes WHERE integrante_id = ?", (integrante_id,))
        
        # Remove da tabela 'integrantes'
        c.execute("DELETE FROM integrantes WHERE id = ?", (integrante_id,))
        
        # 🔥 Remove da tabela 'usuarios'
        c.execute("DELETE FROM usuarios WHERE usuario = ?", (usuario,))
        
        conn.commit()
        return True
    except Exception as e:
        raise e

def contar_atribuidos_por_funcao(conn, setor, funcao):
    try:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM atribuicoes WHERE setor = ? AND funcao = ?", (setor, funcao))
        return c.fetchone()[0]
    except Exception as e:
        raise e

def contar_total_integrantes(conn):
    try:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM integrantes")
        return c.fetchone()[0]
    except Exception as e:
        raise e

def contar_setores_unicos_por_integrante(conn, integrante_id):
    try:
        c = conn.cursor()
        c.execute("SELECT COUNT(DISTINCT setor) FROM atribuicoes WHERE integrante_id = ?", (integrante_id,))
        return c.fetchone()[0]
    except Exception as e:
        raise e

def contar_total_funcoes_por_integrante(conn, integrante_id):
    try:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM atribuicoes WHERE integrante_id = ?", (integrante_id,))
        return c.fetchone()[0]
    except Exception as e:
        raise e