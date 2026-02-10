# db.py
import sqlite3

DB_NAME = "documents.db"

def get_connection():
    return sqlite3.connect(DB_NAME)


def update_description(doc_id, new_desc):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE documents SET description=? WHERE id=?",
        (new_desc, doc_id)
    )
    conn.commit()
    conn.close()


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT NOT NULL,
            file_path TEXT UNIQUE NOT NULL,
            file_type TEXT NOT NULL,
            description TEXT,
            tags TEXT,
            added_on DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def update_doc_details(doc_id, description, tags):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE documents SET description=?, tags=? WHERE id=?",
        (description, tags, doc_id)
    )
    conn.commit()
    conn.close()


def insert_document(name, path, ftype, desc):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO documents (file_name, file_path, file_type, description)
        VALUES (?, ?, ?, ?)
    """, (name, path, ftype, desc))
    conn.commit()
    conn.close()

def delete_document(doc_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM documents WHERE id=?", (doc_id,))
    conn.commit()
    conn.close()

def fetch_documents(search="", ftype="ALL", tag=""):
    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT
            id,
            file_name,
            file_type,
            description,
            tags,
            file_path
        FROM documents
        WHERE (
            file_name LIKE ?
            OR description LIKE ?
            OR tags LIKE ?
        )
    """

    params = [
        f"%{search}%",
        f"%{search}%",
        f"%{tag}%"
    ]

    if ftype != "ALL":
        query += " AND file_type = ?"
        params.append(ftype)

    query += " ORDER BY added_on DESC"

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows


