import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# Carregar variáveis de ambiente
load_dotenv()

# Configurações do banco de dados
DATABASE_URL = os.getenv('DATABASE_URL', '')

if not DATABASE_URL:
    raise Exception("DATABASE_URL não configurada! Configure no Railway ou no arquivo .env")

print("✅ Conectando ao PostgreSQL...")

def get_connection():
    """Retorna uma conexão com o banco de dados PostgreSQL"""
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        print(f"❌ Erro ao conectar PostgreSQL: {e}")
        raise

def return_connection(conn):
    """Fecha a conexão com o banco de dados"""
    if conn:
        conn.close()

def init_database():
    """Inicializa o banco de dados com todas as tabelas necessárias"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # ============================================
    # TABELA DE EMAILS AUTORIZADOS
    # ============================================
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

    # ============================================
    # TABELA DE CASOS DE USO
    # ============================================
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

    # ============================================
    # TABELA DE BOAS PRÁTICAS
    # ============================================
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

    # ============================================
    # TABELA DE FERRAMENTAS
    # ============================================
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

    # ============================================
    # TABELA DE VÍDEOS/PÍLULAS
    # ============================================
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

    # ============================================
    # TABELA DE SNIPPETS
    # ============================================
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

    # ============================================
    # TABELA DE MATERIAIS DE REFERÊNCIA
    # ============================================
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

    # ============================================
    # TABELA DE HISTÓRICO DO AE DO MÊS
    # ============================================
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

    # ============================================
    # TABELAS DO ROADMAP
    # ============================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS roadmap_progresso (
            id SERIAL PRIMARY KEY,
            pilar TEXT NOT NULL,
            progresso INTEGER NOT NULL,
            meta TEXT,
            atualizado_por TEXT,
            data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS roadmap_entregas (
            id SERIAL PRIMARY KEY,
            titulo TEXT NOT NULL,
            responsavel TEXT NOT NULL,
            prazo TEXT NOT NULL,
            prioridade TEXT NOT NULL,
            status TEXT DEFAULT 'pendente',
            criado_por TEXT,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS roadmap_fases (
            id SERIAL PRIMARY KEY,
            fase TEXT NOT NULL,
            status TEXT NOT NULL,
            data_prevista TEXT NOT NULL,
            entregas TEXT,
            data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # ============================================
    # TABELAS PARA ONBOARDING E FEEDBACK
    # ============================================
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trilhas_aprendizado (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            nivel TEXT NOT NULL,
            descricao TEXT,
            tempo_estimado TEXT,
            requisitos TEXT,
            criado_por TEXT,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trilhas_etapas (
            id SERIAL PRIMARY KEY,
            trilha_id INTEGER NOT NULL,
            ordem INTEGER NOT NULL,
            titulo TEXT NOT NULL,
            descricao TEXT,
            tipo TEXT NOT NULL,
            conteudo_id INTEGER,
            url_externa TEXT,
            prazo_dias INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS progresso_usuario (
            id SERIAL PRIMARY KEY,
            usuario_email TEXT NOT NULL,
            trilha_id INTEGER NOT NULL,
            etapa_id INTEGER NOT NULL,
            status TEXT DEFAULT 'pendente',
            data_inicio TIMESTAMP,
            data_conclusao TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback_casos (
            id SERIAL PRIMARY KEY,
            caso_id INTEGER NOT NULL,
            usuario_email TEXT NOT NULL,
            avaliacao INTEGER CHECK (avaliacao >= 1 AND avaliacao <= 5),
            comentario TEXT,
            utilidade TEXT,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS casos_destaque (
            id SERIAL PRIMARY KEY,
            caso_id INTEGER NOT NULL,
            motivo TEXT,
            destacado_por TEXT,
            data_destaque TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # ============================================
    # DADOS INICIAIS
    # ============================================
    
    # Inserir admin padrão
    cursor.execute("SELECT * FROM allowed_emails WHERE email = 'admin@aehub.com'")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO allowed_emails (email, role, nome, added_by)
            VALUES (%s, %s, %s, %s)
        """, ('admin@aehub.com', 'admin', 'Administrador', 'system'))

    # Inserir dados iniciais do roadmap
    cursor.execute("SELECT COUNT(*) FROM roadmap_progresso")
    if cursor.fetchone()[0] == 0:
        progressos_iniciais = [
            ("Pilar A: Casos de Uso", 75, "50 casos até Jun/26", "system"),
            ("Pilar B: Boas Práticas", 60, "8 checklists completos", "system"),
            ("Pilar C: Stack de Ferramentas", 85, "50+ ferramentas catalogadas", "system"),
            ("Pilar D: Biblioteca", 40, "200+ materiais catalogados", "system"),
            ("Pilar E: Treinamento", 35, "20 pílulas + playlist", "system"),
            ("Pilar F: Gamificação", 70, "Sistema de pontos e badges", "system")
        ]
        for pilar, prog, meta, autor in progressos_iniciais:
            cursor.execute("""
                INSERT INTO roadmap_progresso (pilar, progresso, meta, atualizado_por)
                VALUES (%s, %s, %s, %s)
            """, (pilar, prog, meta, autor))
    
    cursor.execute("SELECT COUNT(*) FROM roadmap_fases")
    if cursor.fetchone()[0] == 0:
        fases_iniciais = [
            ("Fase 1: Crowdsourcing", "✅ Concluído", "26/03/2026", "18 cases coletados"),
            ("Fase 2: Curadoria", "🔄 Em andamento", "Abril 2026", "Categorização com IA, agrupamento por temas"),
            ("Fase 3: Documentação", "📝 Planejada", "Maio 2026", "Consolidação do Guia de Estilo, templates"),
            ("Fase 4: Biblioteca", "🚀 Iniciada", "Junho 2026", "Importação de 100+ materiais, busca integrada"),
            ("Fase 5: Gamificação", "📅 Agendada", "Julho 2026", "Sistema de pontos, badges, ranking")
        ]
        for fase, status, data, entregas in fases_iniciais:
            cursor.execute("""
                INSERT INTO roadmap_fases (fase, status, data_prevista, entregas)
                VALUES (%s, %s, %s, %s)
            """, (fase, status, data, entregas))

    # Inserir dados iniciais das trilhas
    cursor.execute("SELECT COUNT(*) FROM trilhas_aprendizado")
    if cursor.fetchone()[0] == 0:
        # Trilha Iniciante
        cursor.execute("""
            INSERT INTO trilhas_aprendizado (nome, nivel, descricao, tempo_estimado, requisitos, criado_por)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, ('Fundamentos de Analytics Engineering', 'iniciante', 
              'Trilha essencial para novos AEs: conceitos de modelagem, DAX básico e Power Query',
              '2 semanas', 'Conhecimento básico de SQL', 'system'))
        
        cursor.execute("SELECT lastval()")
        trilha_id = cursor.fetchone()[0]
        
        etapas_iniciante = [
            (1, "Introdução ao Star Schema", "Entenda os conceitos de modelagem dimensional", "material", None, None, 2),
            (2, "DAX Básico: Medidas e Contexto", "Aprenda a criar medidas simples e entender contexto", "video", None, "https://youtu.be/example", 3),
            (3, "Power Query para Iniciantes", "Transformação e limpeza de dados", "material", None, None, 2),
            (4, "Case: Otimização de Modelo", "Estude um caso real de otimização", "caso", 1, None, 3),
            (5, "Checklist de Boas Práticas", "Valide seus conhecimentos com nosso checklist", "desafio", None, None, 2)
        ]
        
        for ordem, titulo, desc, tipo, conteudo_id, url, prazo in etapas_iniciante:
            cursor.execute("""
                INSERT INTO trilhas_etapas (trilha_id, ordem, titulo, descricao, tipo, conteudo_id, url_externa, prazo_dias)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (trilha_id, ordem, titulo, desc, tipo, conteudo_id, url, prazo))
        
        # Trilha Intermediário
        cursor.execute("""
            INSERT INTO trilhas_aprendizado (nome, nivel, descricao, tempo_estimado, requisitos, criado_por)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, ('Otimização e Performance', 'intermediario', 
              'Aprofunde seus conhecimentos em performance DAX, otimização de modelos e boas práticas avançadas',
              '3 semanas', 'Conhecimento básico de DAX e modelagem', 'system'))
        
        # Trilha Avançado
        cursor.execute("""
            INSERT INTO trilhas_aprendizado (nome, nivel, descricao, tempo_estimado, requisitos, criado_por)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, ('Arquitetura e Integrações', 'avancado', 
              'Domine integrações com Databricks, APIs e arquiteturas de dados escaláveis',
              '4 semanas', 'Experiência com DAX e Power Query', 'system'))

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Banco de dados PostgreSQL inicializado com sucesso!")

# ============================================
# FUNÇÕES PARA GERENCIAR USUÁRIOS
# ============================================

def adicionar_usuario_com_avatar(email, role='viewer', nome=None, avatar_file=None, added_by=None):
    """Adiciona um usuário com avatar personalizado"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if not nome:
            nome = email.split('@')[0].replace('.', ' ').title()
        
        cursor.execute("""
            INSERT INTO allowed_emails (email, role, nome, avatar_file, added_by)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT(email) DO UPDATE SET 
                role = EXCLUDED.role,
                nome = EXCLUDED.nome,
                avatar_file = EXCLUDED.avatar_file
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
    cursor.execute("SELECT avatar_file FROM allowed_emails WHERE email = %s", (email,))
    result = cursor.fetchone()
    cursor.close()
    return_connection(conn)
    return result[0] if result else None

def get_nome_usuario(email):
    """Retorna o nome do usuário"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM allowed_emails WHERE email = %s", (email,))
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
    cursor.execute("UPDATE allowed_emails SET avatar_file = %s WHERE email = %s", (avatar_file, email))
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
            'added_at': str(row[5])[:10] if row[5] else 'N/A'
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
                
                cursor.execute("SELECT id FROM materiais WHERE titulo = %s", (titulo,))
                existe = cursor.fetchone()
                
                if not existe:
                    cursor.execute("""
                        INSERT INTO materiais (titulo, tipo, topicos, descricao, url, autor, autor_email)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
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
    
    cursor.execute("""
        INSERT INTO ae_mes_historico (email, nome, mes, ano, pontuacao, contribuicoes, definido_por)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
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
print("✅ Banco PostgreSQL pronto para uso!")