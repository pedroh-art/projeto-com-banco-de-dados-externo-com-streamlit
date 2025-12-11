# models/compromisso.py
import sqlite3

# Horários padrão (08:00 a 19:00)
HORARIOS_PADRAO = [f"{h:02d}:00" for h in range(8, 20)]

def criar_compromisso(conn, titulo, descricao, data, inicio, fim):
    try:
        c = conn.cursor()
        c.execute("""
            INSERT INTO compromissos (titulo, descricao, data, horario_inicio, horario_fim)
            VALUES (?, ?, ?, ?, ?)
        """, (titulo.strip(), descricao.strip(), data, inicio, fim))
        conn.commit()
        return True
    except Exception as e:
        raise e

def listar_compromissos(conn):
    try:
        c = conn.cursor()
        c.execute("""
            SELECT id, titulo, descricao, data, horario_inicio, horario_fim
            FROM compromissos
            ORDER BY data, horario_inicio
        """)
        return c.fetchall()
    except Exception as e:
        raise e

def atualizar_compromisso(conn, comp_id, titulo, descricao, data, inicio, fim):
    try:
        c = conn.cursor()
        c.execute("""
            UPDATE compromissos
            SET titulo = ?, descricao = ?, data = ?, horario_inicio = ?, horario_fim = ?
            WHERE id = ?
        """, (titulo.strip(), descricao.strip(), data, inicio, fim, comp_id))
        conn.commit()
        return True
    except Exception as e:
        raise e

def excluir_compromisso(conn, comp_id):
    try:
        c = conn.cursor()
        c.execute("DELETE FROM compromissos WHERE id = ?", (comp_id,))
        conn.commit()
        return True
    except Exception as e:
        raise e