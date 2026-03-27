import os
import sys
from datetime import datetime

# ================= CONFIGURAÇÃO =================
# Tenta pegar DATABASE_URL do ambiente
DATABASE_URL = os.environ.get('DATABASE_URL', '')

# Se tiver DATABASE_URL, usa PostgreSQL
if DATABASE_URL:
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        DB_TYPE = 'postgresql'
        print("✅ Usando PostgreSQL via Railway")
    except ImportError:
        import sqlite3
        DB_TYPE = 'sqlite'
        print("⚠️ psycopg2 não instalado, usando SQLite")
else:
    import sqlite3
    DB_TYPE = 'sqlite'
    print("📁 Usando SQLite local")

DB_PATH = "ae_knowledge.db"

# ================= FUNÇÕES DE CONEXÃO =================
def get_connection():
    """Retorna uma conexão com o banco"""
    if DB_TYPE == 'postgresql' and DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)
    else:
        import sqlite3
        return sqlite3.connect(DB_PATH)

def return_connection(conn):
    """Fecha a conexão"""
    if conn:
        conn.close()

# ================= INICIALIZAÇÃO =================
def init_database():
    """Inicializa o banco de dados"""
    if DB_TYPE == 'postgresql':
        _init_postgresql()
    else:
        _init_sqlite()

def _init_sqlite():
    """Inicializa SQLite"""
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabela allowed_emails
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS allowed_emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL DEFAULT 'viewer',
            nome TEXT,
            avatar_file TEXT,
            added_by TEXT,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela materiais
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS materiais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            tipo TEXT NOT NULL,
            topicos TEXT,
            descricao TEXT,
            url TEXT,
            autor TEXT NOT NULL,
            autor_email TEXT NOT NULL,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Adicionar admin
    cursor.execute("SELECT * FROM allowed_emails WHERE email = 'admin@aehub.com'")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO allowed_emails (email, role, nome, added_by)
            VALUES ('admin@aehub.com', 'admin', 'Administrador', 'system')
        """)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ SQLite inicializado")

def _init_postgresql():
    """Inicializa PostgreSQL"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tabela allowed_emails
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS allowed_emails (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL DEFAULT 'viewer',
            nome TEXT,
            avatar_file TEXT,
            added_by TEXT,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela materiais
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS materiais (
            id SERIAL PRIMARY KEY,
            titulo TEXT NOT NULL,
            tipo TEXT NOT NULL,
            topicos TEXT,
            descricao TEXT,
            url TEXT,
            autor TEXT NOT NULL,
            autor_email TEXT NOT NULL,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Adicionar admin
    cursor.execute("SELECT * FROM allowed_emails WHERE email = 'admin@aehub.com'")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO allowed_emails (email, role, nome, added_by)
            VALUES (%s, %s, %s, %s)
        """, ('admin@aehub.com', 'admin', 'Administrador', 'system'))
    
    conn.commit()
    cursor.close()
    return_connection(conn)
    print("✅ PostgreSQL inicializado")

# Inicializar
init_database()

# ================= FUNÇÕES AUXILIARES =================
def get_nome_usuario(email):
    """Retorna nome do usuário"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if DB_TYPE == 'postgresql':
        cursor.execute("SELECT nome FROM allowed_emails WHERE email = %s", (email,))
    else:
        cursor.execute("SELECT nome FROM allowed_emails WHERE email = ?", (email,))
    
    result = cursor.fetchone()
    cursor.close()
    return_connection(conn)
    
    if result and result[0]:
        return result[0]
    return email.split('@')[0].replace('.', ' ').title()

def adicionar_usuario_com_avatar(email, role='viewer', nome=None, avatar_file=None, added_by=None):
    """Adiciona usuário com avatar"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if not nome:
            nome = email.split('@')[0].replace('.', ' ').title()
        
        if DB_TYPE == 'postgresql':
            cursor.execute("""
                INSERT INTO allowed_emails (email, role, nome, avatar_file, added_by)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (email) DO UPDATE SET 
                    role = EXCLUDED.role,
                    nome = EXCLUDED.nome,
                    avatar_file = EXCLUDED.avatar_file
            """, (email.lower().strip(), role, nome, avatar_file, added_by))
        else:
            cursor.execute("""
                INSERT INTO allowed_emails (email, role, nome, avatar_file, added_by)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(email) DO UPDATE SET 
                    role = excluded.role,
                    nome = excluded.nome,
                    avatar_file = excluded.avatar_file
            """, (email.lower().strip(), role, nome, avatar_file, added_by))
        
        conn.commit()
        cursor.close()
        return_connection(conn)
        return True
    except Exception as e:
        print(f"Erro: {e}")
        return False