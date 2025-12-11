# database.py
import os
import bcrypt

# Verifica se estamos no Render (PostgreSQL) ou local (SQLite)
DATABASE_URL = os.getenv("DATABASE_URL")

# Define o caminho do banco: usa /tmp na nuvem, raiz localmente
DB_PATH = "/tmp/equipe.db" if os.path.exists("/tmp") else "equipe.db"

def init_db():
<<<<<<< HEAD
    if DATABASE_URL:
        return _init_postgres()
    else:
        return _init_sqlite()
=======
    """
    Inicializa a conexão com o banco de dados e cria todas as tabelas necessárias.
    Retorna o objeto de conexão.
    """
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.execute("PRAGMA foreign_keys = ON")
        _create_tables(conn)
        return conn
    except Exception as e:
        raise RuntimeError(f"Erro ao inicializar o banco de dados: {e}")
>>>>>>> ad4c32dfb06ad3e62a2ef341a7d556687f868e28

def _init_sqlite():
    import sqlite3
    DB_PATH = "equipe.db"
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    _create_tables(conn, "sqlite")
    return conn

def _init_postgres():
    import psycopg2
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    _create_tables(conn, "postgres")
    return conn

def _create_tables(conn, db_type):
    c = conn.cursor()

    # Tabela: integrantes
    if db_type == "sqlite":
        c.execute("""
            CREATE TABLE IF NOT EXISTS integrantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL
            )
        """)
    else:
        c.execute("""
            CREATE TABLE IF NOT EXISTS integrantes (
                id SERIAL PRIMARY KEY,
                nome TEXT UNIQUE NOT NULL
            )
        """)

    # Tabela: atribuicoes
    if db_type == "sqlite":
        c.execute("""
            CREATE TABLE IF NOT EXISTS atribuicoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                integrante_id INTEGER,
                setor TEXT NOT NULL,
                funcao TEXT NOT NULL,
                UNIQUE(integrante_id, setor, funcao),
                FOREIGN KEY(integrante_id) REFERENCES integrantes(id) ON DELETE CASCADE
            )
        """)
    else:
        c.execute("""
            CREATE TABLE IF NOT EXISTS atribuicoes (
                id SERIAL PRIMARY KEY,
                integrante_id INTEGER,
                setor TEXT NOT NULL,
                funcao TEXT NOT NULL,
                UNIQUE(integrante_id, setor, funcao),
                FOREIGN KEY(integrante_id) REFERENCES integrantes(id) ON DELETE CASCADE
            )
        """)

    # Tabela: usuarios
    if db_type == "sqlite":
        c.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                senha BLOB NOT NULL,
                tipo TEXT NOT NULL CHECK(tipo IN ('administrador', 'membro'))
            )
        """)
    else:
        c.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                usuario TEXT UNIQUE NOT NULL,
                senha BYTEA NOT NULL,
                tipo TEXT NOT NULL CHECK(tipo IN ('administrador', 'membro'))
            )
        """)

    # Tabela: tarefas
    if db_type == "sqlite":
        c.execute("""
            CREATE TABLE IF NOT EXISTS tarefas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descricao TEXT,
                status TEXT NOT NULL CHECK(status IN ('to_do', 'doing', 'done')),
                integrante_id INTEGER,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(integrante_id) REFERENCES integrantes(id) ON DELETE SET NULL
            )
        """)
    else:
        c.execute("""
            CREATE TABLE IF NOT EXISTS tarefas (
                id SERIAL PRIMARY KEY,
                titulo TEXT NOT NULL,
                descricao TEXT,
                status TEXT NOT NULL CHECK(status IN ('to_do', 'doing', 'done')),
                integrante_id INTEGER,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(integrante_id) REFERENCES integrantes(id) ON DELETE SET NULL
            )
        """)

    # Tabela: compromissos
    if db_type == "sqlite":
        c.execute("""
            CREATE TABLE IF NOT EXISTS compromissos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descricao TEXT,
                data DATE NOT NULL,
                horario_inicio TEXT NOT NULL,
                horario_fim TEXT NOT NULL,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    else:
        c.execute("""
            CREATE TABLE IF NOT EXISTS compromissos (
                id SERIAL PRIMARY KEY,
                titulo TEXT NOT NULL,
                descricao TEXT,
                data DATE NOT NULL,
                horario_inicio TEXT NOT NULL,
                horario_fim TEXT NOT NULL,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

    # Garantir usuário admin
    c.execute("SELECT 1 FROM usuarios WHERE usuario = 'pedro'")
    if not c.fetchone():
        senha_admin = os.getenv("ADMIN_PASSWORD")
        if not senha_admin:
            raise RuntimeError("ADMIN_PASSWORD não definida!")
        senha_hash = bcrypt.hashpw(senha_admin.encode('utf-8'), bcrypt.gensalt())
        if db_type == "sqlite":
            c.execute("INSERT INTO usuarios (usuario, senha, tipo) VALUES (?, ?, ?)",
                      ("pedro", senha_hash, "administrador"))
        else:
            c.execute("INSERT INTO usuarios (usuario, senha, tipo) VALUES (%s, %s, %s)",
                      ("pedro", senha_hash, "administrador"))

    conn.commit()
