import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações do banco de dados
DB_TYPE = os.getenv('DB_TYPE', 'sqlite')
DATABASE_URL = os.getenv('DATABASE_URL', '')

# Se tiver DATABASE_URL, usa PostgreSQL (Railway, Heroku, etc.)
if DATABASE_URL:
    DB_TYPE = 'postgresql'
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        print("✅ PostgreSQL disponível")
    except ImportError:
        print("⚠️ psycopg2 não instalado, usando SQLite")
        DB_TYPE = 'sqlite'
        DATABASE_URL = ''

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'ae_knowledge')
DB_USER = os.getenv('DB_USER', '')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_PATH = os.getenv('DB_PATH', 'ae_knowledge.db')

def get_connection():
    """Retorna uma conexão com o banco de dados"""
    if DB_TYPE.lower() == 'postgresql' and DATABASE_URL:
        try:
            return psycopg2.connect(DATABASE_URL)
        except Exception as e:
            print(f"❌ Erro ao conectar PostgreSQL: {e}")
            print("⚠️ Usando SQLite como fallback")
            import sqlite3
            if not os.path.exists(DB_PATH):
                init_database()
            return sqlite3.connect(DB_PATH)
    else:
        import sqlite3
        if not os.path.exists(DB_PATH):
            init_database()
        return sqlite3.connect(DB_PATH)

def return_connection(conn):
    """Fecha a conexão com o banco de dados"""
    if conn:
        conn.close()

def init_database():
    """Inicializa o banco de dados com todas as tabelas necessárias"""
    if DB_TYPE.lower() == 'postgresql' and DATABASE_URL:
        _init_postgresql()
    else:
        _init_sqlite()

def _init_sqlite():
    """Inicializa banco SQLite"""
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Tabela de emails autorizados
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS allowed_emails (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        role TEXT NOT NULL DEFAULT 'viewer',
        nome TEXT,
        avatar_url TEXT,
        avatar_file TEXT,
        added_by TEXT,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Tabela de casos de uso
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS casos_uso (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            contexto TEXT NOT NULL,
            tecnologia TEXT NOT NULL,
            descricao TEXT NOT NULL,
            resultado TEXT,
            tags TEXT,
            autor TEXT NOT NULL,
            autor_email TEXT NOT NULL,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabela de boas práticas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS boas_praticas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            categoria TEXT NOT NULL,
            conteudo TEXT NOT NULL,
            autor TEXT NOT NULL,
            autor_email TEXT NOT NULL,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabela de ferramentas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ferramentas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL,
            versao TEXT,
            descricao TEXT,
            nivel TEXT,
            documentacao_link TEXT,
            autor TEXT NOT NULL,
            autor_email TEXT NOT NULL,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabela de vídeos/pílulas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descricao TEXT,
            tema TEXT NOT NULL,
            nivel TEXT NOT NULL,
            duracao TEXT,
            youtube_id TEXT,
            thumbnail_url TEXT,
            autor TEXT NOT NULL,
            autor_email TEXT NOT NULL,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabela de snippets
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS snippets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            linguagem TEXT NOT NULL,
            codigo TEXT NOT NULL,
            descricao TEXT,
            tags TEXT,
            autor TEXT NOT NULL,
            autor_email TEXT NOT NULL,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabela de materiais de referência
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
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabela de histórico do AE do Mês
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ae_mes_historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            nome TEXT NOT NULL,
            mes INTEGER NOT NULL,
            ano INTEGER NOT NULL,
            pontuacao INTEGER NOT NULL,
            contribuicoes TEXT,
            definido_por TEXT,
            data_definicao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Inserir admin padrão se não existir
    cursor.execute("SELECT * FROM allowed_emails WHERE email = 'admin@aehub.com'")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO allowed_emails (email, role, nome, added_by)
            VALUES ('admin@aehub.com', 'admin', 'Administrador', 'system')
        """)

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Banco de dados SQLite inicializado com sucesso!")

def _init_postgresql():
    """Inicializa banco PostgreSQL"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
    except Exception as e:
        print(f"❌ Erro ao conectar PostgreSQL: {e}")
        print("⚠️ Usando SQLite como fallback")
        global DB_TYPE
        DB_TYPE = 'sqlite'
        return _init_sqlite()
    
    cursor = conn.cursor()

    # Tabela de emails autorizados
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS allowed_emails (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        role VARCHAR(50) NOT NULL DEFAULT 'viewer',
        nome VARCHAR(255),
        avatar_url TEXT,
        avatar_file TEXT,
        added_by VARCHAR(255),
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Tabela de casos de uso
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS casos_uso (
            id SERIAL PRIMARY KEY,
            titulo VARCHAR(500) NOT NULL,
            contexto TEXT NOT NULL,
            tecnologia VARCHAR(100) NOT NULL,
            descricao TEXT NOT NULL,
            resultado TEXT,
            tags TEXT,
            autor VARCHAR(255) NOT NULL,
            autor_email VARCHAR(255) NOT NULL,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabela de boas práticas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS boas_praticas (
            id SERIAL PRIMARY KEY,
            titulo VARCHAR(500) NOT NULL,
            categoria VARCHAR(100) NOT NULL,
            conteudo TEXT NOT NULL,
            autor VARCHAR(255) NOT NULL,
            autor_email VARCHAR(255) NOT NULL,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabela de ferramentas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ferramentas (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            categoria VARCHAR(100) NOT NULL,
            versao VARCHAR(50),
            descricao TEXT,
            nivel VARCHAR(50),
            documentacao_link TEXT,
            autor VARCHAR(255) NOT NULL,
            autor_email VARCHAR(255) NOT NULL,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabela de vídeos/pílulas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id SERIAL PRIMARY KEY,
            titulo VARCHAR(500) NOT NULL,
            descricao TEXT,
            tema VARCHAR(100) NOT NULL,
            nivel VARCHAR(50) NOT NULL,
            duracao VARCHAR(20),
            youtube_id VARCHAR(20),
            thumbnail_url TEXT,
            autor VARCHAR(255) NOT NULL,
            autor_email VARCHAR(255) NOT NULL,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabela de snippets
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS snippets (
            id SERIAL PRIMARY KEY,
            titulo VARCHAR(500) NOT NULL,
            linguagem VARCHAR(50) NOT NULL,
            codigo TEXT NOT NULL,
            descricao TEXT,
            tags TEXT,
            autor VARCHAR(255) NOT NULL,
            autor_email VARCHAR(255) NOT NULL,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabela de materiais de referência
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS materiais (
            id SERIAL PRIMARY KEY,
            titulo VARCHAR(500) NOT NULL,
            tipo VARCHAR(50) NOT NULL,
            topicos TEXT,
            descricao TEXT,
            url TEXT,
            autor VARCHAR(255) NOT NULL,
            autor_email VARCHAR(255) NOT NULL,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabela de histórico do AE do Mês
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ae_mes_historico (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) NOT NULL,
            nome VARCHAR(255) NOT NULL,
            mes INTEGER NOT NULL,
            ano INTEGER NOT NULL,
            pontuacao INTEGER NOT NULL,
            contribuicoes TEXT,
            definido_por VARCHAR(255),
            data_definicao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Inserir admin padrão se não existir
    cursor.execute("SELECT * FROM allowed_emails WHERE email = 'admin@aehub.com'")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO allowed_emails (email, role, nome, added_by)
            VALUES (%s, %s, %s, %s)
        """, ('admin@aehub.com', 'admin', 'Administrador', 'system'))

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Banco de dados PostgreSQL inicializado com sucesso!")

# ============================================
# FUNÇÕES PARA GERENCIAR USUÁRIOS COM AVATAR
# ============================================

def adicionar_usuario_com_avatar(email, role='viewer', nome=None, avatar_file=None, added_by=None):
    """Adiciona um usuário com avatar personalizado"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if not nome:
            nome = email.split('@')[0].replace('.', ' ').title()
        
        if DB_TYPE == 'postgresql':
            cursor.execute("""
                INSERT INTO allowed_emails (email, role, nome, avatar_file, added_by)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT(email) DO UPDATE SET 
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
        print(f"Erro ao adicionar usuário: {e}")
        return False

def get_avatar_url(email):
    """Retorna o caminho do arquivo de avatar do usuário"""
    conn = get_connection()
    cursor = conn.cursor()
    if DB_TYPE == 'postgresql':
        cursor.execute("SELECT avatar_file FROM allowed_emails WHERE email = %s", (email,))
    else:
        cursor.execute("SELECT avatar_file FROM allowed_emails WHERE email = ?", (email,))
    result = cursor.fetchone()
    cursor.close()
    return_connection(conn)
    return result[0] if result else None

def get_nome_usuario(email):
    """Retorna o nome do usuário"""
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

def atualizar_avatar_usuario(email, avatar_file):
    """Atualiza o avatar de um usuário"""
    conn = get_connection()
    cursor = conn.cursor()
    if DB_TYPE == 'postgresql':
        cursor.execute("UPDATE allowed_emails SET avatar_file = %s WHERE email = %s", (avatar_file, email))
    else:
        cursor.execute("UPDATE allowed_emails SET avatar_file = ? WHERE email = ?", (avatar_file, email))
    conn.commit()
    cursor.close()
    return_connection(conn)
    return True

def get_todos_usuarios_detalhes():
    """Retorna todos os usuários com detalhes completos"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT email, role, nome, avatar_file, added_by, added_at 
        FROM allowed_emails 
        ORDER BY added_at DESC
    """)
    results = cursor.fetchall()
    cursor.close()
    return_connection(conn)
    
    usuarios = []
    for row in results:
        usuarios.append({
            'email': row[0],
            'role': row[1],
            'nome': row[2] if row[2] else row[0].split('@')[0].replace('.', ' ').title(),
            'avatar_file': row[3],
            'added_by': row[4] if row[4] else 'Sistema',
            'added_at': row[5][:10] if row[5] else 'N/A'
        })
    return usuarios

# ============================================
# FUNÇÕES PARA MATERIAIS
# ============================================

def importar_materiais_do_excel(excel_path=None):
    """Importa os materiais do arquivo Excel para o banco de dados"""
    try:
        import pandas as pd
        
        if excel_path is None:
            possiveis_caminhos = [
                "assets/2. Analytics Engineering - List of Reference Materials.xlsx",
                "2. Analytics Engineering - List of Reference Materials.xlsx",
                "../assets/2. Analytics Engineering - List of Reference Materials.xlsx"
            ]
            
            excel_path = None
            for caminho in possiveis_caminhos:
                if os.path.exists(caminho):
                    excel_path = caminho
                    break
            
            if excel_path is None:
                print("❌ Arquivo Excel não encontrado")
                return False
        
        print(f"📖 Lendo arquivo: {excel_path}")
        df = pd.read_excel(excel_path, sheet_name="Content Library")
        
        conn = get_connection()
        cursor = conn.cursor()
        
        contador = 0
        for _, row in df.iterrows():
            if pd.notna(row['Item']):
                titulo = str(row['Item'])[:200]
                tipo = str(row['Type']) if pd.notna(row['Type']) else "Other"
                topicos = str(row['Topic(s)']) if pd.notna(row['Topic(s)']) else ""
                descricao = str(row['Description']) if pd.notna(row['Description']) else ""
                url = titulo if "http" in titulo else ""
                autor = str(row['Created by']) if pd.notna(row['Created by']) else "Sistema"
                
                if DB_TYPE == 'postgresql':
                    cursor.execute("SELECT id FROM materiais WHERE titulo = %s", (titulo,))
                else:
                    cursor.execute("SELECT id FROM materiais WHERE titulo = ?", (titulo,))
                existe = cursor.fetchone()
                
                if not existe:
                    if DB_TYPE == 'postgresql':
                        cursor.execute("""
                            INSERT INTO materiais (titulo, tipo, topicos, descricao, url, autor, autor_email)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (titulo, tipo, topicos, descricao, url, autor, "system@aehub.com"))
                    else:
                        cursor.execute("""
                            INSERT INTO materiais (titulo, tipo, topicos, descricao, url, autor, autor_email)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (titulo, tipo, topicos, descricao, url, autor, "system@aehub.com"))
                    contador += 1
        
        conn.commit()
        cursor.close()
        return_connection(conn)
        print(f"✅ Importados {contador} novos materiais")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao importar materiais: {e}")
        return False

# ============================================
# FUNÇÕES PARA AE DO MÊS
# ============================================

def salvar_ae_mes_historico(email, nome, pontuacao, contribuicoes, definido_por):
    """Salva o AE do Mês no histórico"""
    conn = get_connection()
    cursor = conn.cursor()
    
    mes = datetime.now().month
    ano = datetime.now().year
    
    if DB_TYPE == 'postgresql':
        cursor.execute("""
            INSERT INTO ae_mes_historico (email, nome, mes, ano, pontuacao, contribuicoes, definido_por)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (email, nome, mes, ano, pontuacao, contribuicoes, definido_por))
    else:
        cursor.execute("""
            INSERT INTO ae_mes_historico (email, nome, mes, ano, pontuacao, contribuicoes, definido_por)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (email, nome, mes, ano, pontuacao, contribuicoes, definido_por))
    
    conn.commit()
    cursor.close()
    return_connection(conn)
    print(f"✅ AE do Mês salvo no histórico: {nome}")

def get_historico_ae_mes():
    """Retorna o histórico do AE do Mês"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT nome, mes, ano, pontuacao, contribuicoes, data_definicao 
        FROM ae_mes_historico 
        ORDER BY ano DESC, mes DESC
        LIMIT 12
    """)
    
    resultados = cursor.fetchall()
    cursor.close()
    return_connection(conn)
    return resultados

# ============================================
# INICIALIZAR BANCO
# ============================================
init_database()
print(f"✅ Banco inicializado - Modo: {DB_TYPE.upper()}")