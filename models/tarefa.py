# models/tarefa.py
import sqlite3

def criar_tarefa(conn, titulo, descricao, integrante_id, status="to_do"):
    try:
        c = conn.cursor()
        c.execute("""
            INSERT INTO tarefas (titulo, descricao, status, integrante_id)
            VALUES (?, ?, ?, ?)
        """, (titulo.strip(), descricao.strip(), status, integrante_id))
        conn.commit()
        return True
    except Exception as e:
        raise e

def atualizar_status_tarefa(conn, tarefa_id, novo_status):
    try:
        c = conn.cursor()
        c.execute("UPDATE tarefas SET status = ? WHERE id = ?", (novo_status, tarefa_id))
        conn.commit()
        return True
    except Exception as e:
        raise e

def excluir_tarefa(conn, tarefa_id):
    try:
        c = conn.cursor()
        c.execute("DELETE FROM tarefas WHERE id = ?", (tarefa_id,))
        conn.commit()
        return True
    except Exception as e:
        raise e

def listar_tarefas_por_status(conn, status):
    try:
        c = conn.cursor()
        return c.execute("""
            SELECT t.id, t.titulo, t.descricao, t.integrante_id, i.nome
            FROM tarefas t
            LEFT JOIN integrantes i ON i.id = t.integrante_id
            WHERE t.status = ?
            ORDER BY t.data_criacao
        """, (status,)).fetchall()
    except Exception as e:
        raise e

def obter_quadro_kanban(conn):
    try:
        c = conn.cursor()
        c.execute("""
            SELECT t.status, t.titulo, t.descricao, i.nome
            FROM tarefas t
            LEFT JOIN integrantes i ON i.id = t.integrante_id
            ORDER BY t.status, t.data_criacao
        """)
        return c.fetchall()
    except Exception as e:
        raise e