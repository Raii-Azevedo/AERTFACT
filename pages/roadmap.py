import streamlit as st
from datetime import datetime
import sys
import os
import pandas as pd
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.menu import render_sidebar
from allowed_emails import can_edit, is_admin
from database import get_connection, return_connection

# Verificar autenticação
if not st.session_state.get("authenticated", False):
    st.switch_page("app.py")

st.set_page_config(
    page_title="Roadmap - AE Knowledge Hub",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Renderizar menu lateral
render_sidebar()

# Obter permissões
user_email = st.session_state.get("user_email", "")
can_edit_content = can_edit(user_email)
is_admin_user = is_admin(user_email)

st.title("🚀 Roadmap de Implementação")
st.markdown("""
*Estratégia e cronograma para transformar o conhecimento tácito em ativos digitais estruturados*
""")

# ============================================
# FUNÇÕES PARA GERENCIAR DADOS DO ROADMAP
# ============================================

def get_db_placeholder():
    """Retorna o placeholder correto para cada banco"""
    from database import DB_TYPE
    return '%s' if DB_TYPE == 'postgresql' else '?'

def init_roadmap_tables():
    """Cria as tabelas necessárias para o roadmap"""
    conn = get_connection()
    cursor = conn.cursor()
    from database import DB_TYPE
    
    # Tabela de progresso dos pilares
    if DB_TYPE == 'postgresql':
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
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS roadmap_progresso (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pilar TEXT NOT NULL,
                progresso INTEGER NOT NULL,
                meta TEXT,
                atualizado_por TEXT,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    # Tabela de entregas
    if DB_TYPE == 'postgresql':
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
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS roadmap_entregas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                responsavel TEXT NOT NULL,
                prazo TEXT NOT NULL,
                prioridade TEXT NOT NULL,
                status TEXT DEFAULT 'pendente',
                criado_por TEXT,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    # Tabela de fases do cronograma
    if DB_TYPE == 'postgresql':
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
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS roadmap_fases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fase TEXT NOT NULL,
                status TEXT NOT NULL,
                data_prevista TEXT NOT NULL,
                entregas TEXT,
                data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    # Inserir dados iniciais se estiver vazio
    cursor.execute("SELECT COUNT(*) FROM roadmap_progresso")
    if cursor.fetchone()[0] == 0:
        progressos_iniciais = [
            ("Pilar A: Casos de Uso", 75, "50 casos até Jun/25"),
            ("Pilar B: Boas Práticas", 60, "8 checklists completos"),
            ("Pilar C: Stack de Ferramentas", 85, "50+ ferramentas catalogadas"),
            ("Pilar D: Biblioteca", 40, "200+ materiais catalogados"),
            ("Pilar E: Treinamento", 35, "20 pílulas + playlist"),
            ("Pilar F: Gamificação", 70, "Sistema de pontos e badges")
        ]
        placeholder = get_db_placeholder()
        for pilar, prog, meta in progressos_iniciais:
            if DB_TYPE == 'postgresql':
                cursor.execute("""
                    INSERT INTO roadmap_progresso (pilar, progresso, meta, atualizado_por)
                    VALUES (%s, %s, %s, %s)
                """, (pilar, prog, meta, "system"))
            else:
                cursor.execute("""
                    INSERT INTO roadmap_progresso (pilar, progresso, meta, atualizado_por)
                    VALUES (?, ?, ?, ?)
                """, (pilar, prog, meta, "system"))
    
    cursor.execute("SELECT COUNT(*) FROM roadmap_fases")
    if cursor.fetchone()[0] == 0:
        fases_iniciais = [
            ("Fase 1: Crowdsourcing", "✅ Concluído", "26/03/2025", "18 cases coletados"),
            ("Fase 2: Curadoria", "🔄 Em andamento", "Abril 2025", "Categorização com IA, agrupamento por temas"),
            ("Fase 3: Documentação", "📝 Planejada", "Maio 2025", "Consolidação do Guia de Estilo, templates"),
            ("Fase 4: Biblioteca", "🚀 Iniciada", "Junho 2025", "Importação de 100+ materiais, busca integrada"),
            ("Fase 5: Gamificação", "📅 Agendada", "Julho 2025", "Sistema de pontos, badges, ranking")
        ]
        for fase, status, data, entregas in fases_iniciais:
            if DB_TYPE == 'postgresql':
                cursor.execute("""
                    INSERT INTO roadmap_fases (fase, status, data_prevista, entregas)
                    VALUES (%s, %s, %s, %s)
                """, (fase, status, data, entregas))
            else:
                cursor.execute("""
                    INSERT INTO roadmap_fases (fase, status, data_prevista, entregas)
                    VALUES (?, ?, ?, ?)
                """, (fase, status, data, entregas))
    
    conn.commit()
    cursor.close()
    return_connection(conn)

def get_progresso_pilares():
    """Busca o progresso dos pilares do banco"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT pilar, progresso, meta FROM roadmap_progresso ORDER BY id")
    resultados = cursor.fetchall()
    cursor.close()
    return_connection(conn)
    return resultados

def atualizar_progresso(pilar, novo_progresso, user_email):
    """Atualiza o progresso de um pilar"""
    conn = get_connection()
    cursor = conn.cursor()
    from database import DB_TYPE
    
    if DB_TYPE == 'postgresql':
        cursor.execute("""
            UPDATE roadmap_progresso 
            SET progresso = %s, atualizado_por = %s, data_atualizacao = CURRENT_TIMESTAMP
            WHERE pilar = %s
        """, (novo_progresso, user_email, pilar))
    else:
        cursor.execute("""
            UPDATE roadmap_progresso 
            SET progresso = ?, atualizado_por = ?, data_atualizacao = CURRENT_TIMESTAMP
            WHERE pilar = ?
        """, (novo_progresso, user_email, pilar))
    conn.commit()
    cursor.close()
    return_connection(conn)

def get_entregas():
    """Busca as entregas do banco"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, titulo, responsavel, prazo, prioridade, status 
        FROM roadmap_entregas 
        ORDER BY 
            CASE prioridade WHEN 'Alta' THEN 1 WHEN 'Média' THEN 2 ELSE 3 END,
            data_criacao DESC
    """)
    resultados = cursor.fetchall()
    cursor.close()
    return_connection(conn)
    return resultados

def adicionar_entrega(titulo, responsavel, prazo, prioridade, user_email):
    """Adiciona uma nova entrega"""
    conn = get_connection()
    cursor = conn.cursor()
    from database import DB_TYPE
    
    if DB_TYPE == 'postgresql':
        cursor.execute("""
            INSERT INTO roadmap_entregas (titulo, responsavel, prazo, prioridade, criado_por)
            VALUES (%s, %s, %s, %s, %s)
        """, (titulo, responsavel, prazo, prioridade, user_email))
    else:
        cursor.execute("""
            INSERT INTO roadmap_entregas (titulo, responsavel, prazo, prioridade, criado_por)
            VALUES (?, ?, ?, ?, ?)
        """, (titulo, responsavel, prazo, prioridade, user_email))
    conn.commit()
    cursor.close()
    return_connection(conn)

def remover_entrega(entrega_id):
    """Remove uma entrega"""
    conn = get_connection()
    cursor = conn.cursor()
    from database import DB_TYPE
    
    if DB_TYPE == 'postgresql':
        cursor.execute("DELETE FROM roadmap_entregas WHERE id = %s", (entrega_id,))
    else:
        cursor.execute("DELETE FROM roadmap_entregas WHERE id = ?", (entrega_id,))
    conn.commit()
    cursor.close()
    return_connection(conn)

def atualizar_status_entrega(entrega_id, novo_status):
    """Atualiza o status de uma entrega"""
    conn = get_connection()
    cursor = conn.cursor()
    from database import DB_TYPE
    
    if DB_TYPE == 'postgresql':
        cursor.execute("UPDATE roadmap_entregas SET status = %s WHERE id = %s", (novo_status, entrega_id))
    else:
        cursor.execute("UPDATE roadmap_entregas SET status = ? WHERE id = ?", (novo_status, entrega_id))
    conn.commit()
    cursor.close()
    return_connection(conn)

def get_fases():
    """Busca as fases do cronograma"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT fase, status, data_prevista, entregas FROM roadmap_fases ORDER BY id")
    resultados = cursor.fetchall()
    cursor.close()
    return_connection(conn)
    return resultados

def atualizar_fase(fase, novo_status, user_email):
    """Atualiza o status de uma fase"""
    conn = get_connection()
    cursor = conn.cursor()
    from database import DB_TYPE
    
    if DB_TYPE == 'postgresql':
        cursor.execute("""
            UPDATE roadmap_fases 
            SET status = %s, data_atualizacao = CURRENT_TIMESTAMP
            WHERE fase = %s
        """, (novo_status, fase))
    else:
        cursor.execute("""
            UPDATE roadmap_fases 
            SET status = ?, data_atualizacao = CURRENT_TIMESTAMP
            WHERE fase = ?
        """, (novo_status, fase))
    conn.commit()
    cursor.close()
    return_connection(conn)

# ============================================
# SEÇÃO 1: VISÃO GERAL E OBJETIVOS
# ============================================
with st.expander("🎯 **Visão Geral e Objetivos Estratégicos**", expanded=True):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📌 Missão
        Transformar o conhecimento tácito do time em um **ativo digital estruturado**, 
        facilitando o onboarding de novos membros e elevando o nível técnico dos projetos.
        """)
        
        st.markdown("""
        ### 🎯 Objetivos
        - **Centralizar conhecimento** em um hub único e acessível
        - **Padronizar práticas** e reduzir retrabalho
        - **Acelerar onboarding** de novos AEs
        - **Gamificar contribuições** para engajar o time
        """)
    
    with col2:
        # Buscar contagens reais do banco
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM casos_uso")
        total_casos = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM videos")
        total_videos = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM materiais")
        total_materiais = cursor.fetchone()[0]
        cursor.close()
        return_connection(conn)
        
        st.markdown(f"""
        ### 📊 KPIs de Sucesso
        | Métrica | Meta | Atual |
        |---------|------|-------|
        | Casos documentados | 50 | {total_casos} |
        | Pílulas de conhecimento | 20 | {total_videos} |
        | Materiais catalogados | 200 | {total_materiais} |
        """)

st.divider()

# ============================================
# SEÇÃO 2: PILARES E PROGRESSO (DINÂMICO)
# ============================================
st.subheader("📂 Pilares do Conhecimento - Progresso")

progressos = get_progresso_pilares()
col1, col2, col3 = st.columns(3)

for idx, (pilar, progresso, meta) in enumerate(progressos):
    with [col1, col2, col3][idx % 3]:
        with st.container(border=True):
            st.markdown(f"### {pilar.split(':')[0]}")
            st.markdown(f"*{pilar.split(':')[1] if ':' in pilar else ''}*")
            st.progress(progresso / 100, text=f"{progresso}% documentado")
            st.caption(f"🎯 **Meta:** {meta}")
            
            if can_edit_content:
                novo_prog = st.slider("Ajustar", 0, 100, progresso, key=f"prog_{pilar}", label_visibility="collapsed")
                if novo_prog != progresso:
                    if st.button("💾 Salvar", key=f"save_{pilar}"):
                        atualizar_progresso(pilar, novo_prog, user_email)
                        st.rerun()

st.divider()

# ============================================
# SEÇÃO 3: CRONOGRAMA DE EXECUÇÃO (DINÂMICO)
# ============================================
st.subheader("📅 Cronograma de Execução")

fases = get_fases()
for fase in fases:
    nome_fase = fase[0]
    status = fase[1]
    data = fase[2]
    entregas = fase[3]
    
    with st.container(border=True):
        col1, col2, col3, col4 = st.columns([2, 1, 2, 3])
        with col1:
            st.markdown(f"### {nome_fase}")
        with col2:
            if can_edit_content:
                novo_status = st.selectbox(
                    "Status",
                    ["✅ Concluído", "🔄 Em andamento", "📝 Planejada", "🚀 Iniciada", "📅 Agendada"],
                    index=["✅ Concluído", "🔄 Em andamento", "📝 Planejada", "🚀 Iniciada", "📅 Agendada"].index(status) if status in ["✅ Concluído", "🔄 Em andamento", "📝 Planejada", "🚀 Iniciada", "📅 Agendada"] else 0,
                    key=f"status_{nome_fase}",
                    label_visibility="collapsed"
                )
                if novo_status != status:
                    atualizar_fase(nome_fase, novo_status, user_email)
                    st.rerun()
            else:
                st.markdown(f"**{status}**")
        with col3:
            st.markdown(f"📅 **{data}**")
        with col4:
            st.markdown(f"📦 {entregas}")

st.divider()

# ============================================
# SEÇÃO 4: PRÓXIMOS PASSOS
# ============================================
st.subheader("🚀 Próximos Passos e Evolução")

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown("#### 🎥 Pílulas de Conhecimento")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM videos")
        total_videos = cursor.fetchone()[0]
        cursor.close()
        return_connection(conn)
        st.progress(min(total_videos / 20, 1.0), text=f"{total_videos}/20 vídeos")
        st.markdown("""
        - [x] Estrutura da playlist definida
        - [x] Template de gravação criado
        - [ ] Playlist oficial no YouTube
        """)
        
        st.markdown("#### 🛠️ Biblioteca de Snippets")
        st.progress(0.30, text="30%")
        st.markdown("""
        - [x] Estrutura de categorias definida
        - [ ] Em desenvolvimento
        """)

with col2:
    with st.container(border=True):
        st.markdown("#### 🔄 Ciclo de Atualização Mensal")
        st.progress(0.50, text="50%")
        st.markdown("""
        - [x] Calendário definido (última sexta do mês)
        - [x] Template de atualização criado
        - [ ] Processo automatizado
        """)
        
        st.markdown("#### 🏆 Gamificação")
        st.progress(0.70, text="70%")
        st.markdown("""
        - [x] Sistema de pontos definido
        - [x] AE do Mês implementado
        - [ ] Badges por nível
        """)

st.divider()

# ============================================
# SEÇÃO 5: MÉTRICAS E MONITORAMENTO
# ============================================
st.subheader("📊 Métricas e Monitoramento")

# Dados reais do banco
conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM casos_uso")
total_casos = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM materiais")
total_materiais = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM videos")
total_videos = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM ferramentas")
total_ferramentas = cursor.fetchone()[0]
cursor.close()
return_connection(conn)

dados_evolucao = pd.DataFrame({
    'Mês': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
    'Casos': [8, 12, total_casos, total_casos + 8, total_casos + 15, total_casos + 22],
    'Materiais': [20, 35, total_materiais, total_materiais + 30, total_materiais + 60, total_materiais + 100],
    'Vídeos': [2, 5, total_videos, total_videos + 3, total_videos + 6, total_videos + 10]
})

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Evolução do Repositório")
    st.line_chart(dados_evolucao.set_index('Mês'))

with col2:
    st.markdown("#### Engajamento do Time")
    st.markdown(f"""
    | Métrica | Valor | Meta |
    |---------|-------|------|
    | Casos documentados | {total_casos} | 50 |
    | Materiais catalogados | {total_materiais} | 200 |
    | Pílulas produzidas | {total_videos} | 20 |
    | Ferramentas homologadas | {total_ferramentas} | 50 |
    """)

st.divider()

# ============================================
# SEÇÃO 6: PRÓXIMAS ENTREGAS (DINÂMICO)
# ============================================
st.subheader("📋 Próximas Entregas")

# Buscar entregas do banco
entregas = get_entregas()

if entregas:
    for entrega in entregas:
        entrega_id = entrega[0]
        titulo = entrega[1]
        responsavel = entrega[2]
        prazo = entrega[3]
        prioridade = entrega[4]
        status = entrega[5]
        
        with st.container(border=True):
            col1, col2, col3, col4, col5 = st.columns([3, 2, 1, 1, 1])
            with col1:
                st.markdown(f"**{titulo}**")
            with col2:
                st.markdown(f"👤 {responsavel}")
            with col3:
                st.markdown(f"📅 {prazo}")
            with col4:
                if prioridade == "Alta":
                    st.error("🔴 Alta")
                elif prioridade == "Média":
                    st.warning("🟡 Média")
                else:
                    st.info("🔵 Baixa")
            with col5:
                if can_edit_content:
                    novo_status = st.selectbox(
                        "Status",
                        ["pendente", "em andamento", "concluído"],
                        index=["pendente", "em andamento", "concluído"].index(status) if status in ["pendente", "em andamento", "concluído"] else 0,
                        key=f"status_entrega_{entrega_id}",
                        label_visibility="collapsed"
                    )
                    if novo_status != status:
                        atualizar_status_entrega(entrega_id, novo_status)
                        st.rerun()
                    
                    if st.button("🗑️", key=f"del_{entrega_id}"):
                        remover_entrega(entrega_id)
                        st.rerun()
                else:
                    st.markdown(f"📌 {status}")
else:
    st.info("Nenhuma entrega cadastrada ainda. Use a área de administração para adicionar.")

# ============================================
# SEÇÃO 7: ADMIN - GESTÃO DO ROADMAP
# ============================================
if can_edit_content or is_admin_user:
    st.divider()
    with st.expander("🔧 **Administração do Roadmap** (Apenas Editores)", expanded=False):
        st.warning("⚠️ Área restrita para atualização do roadmap")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("➕ Adicionar Nova Entrega")
            nova_entrega = st.text_input("Descrição da entrega")
            responsavel = st.text_input("Responsável")
            prazo = st.date_input("Prazo")
            prioridade = st.selectbox("Prioridade", ["Alta", "Média", "Baixa"])
            
            if st.button("💾 Adicionar ao Roadmap", type="primary"):
                if nova_entrega and responsavel:
                    adicionar_entrega(nova_entrega, responsavel, str(prazo), prioridade, user_email)
                    st.success(f"✅ Entrega '{nova_entrega}' adicionada com sucesso!")
                    st.rerun()
                else:
                    st.warning("Preencha descrição e responsável")
        
        with col2:
            st.subheader("📈 Atualizar Progresso dos Pilares")
            progressos_atual = get_progresso_pilares()
            
            for pilar, prog, meta in progressos_atual:
                st.markdown(f"**{pilar}**")
                novo_prog = st.slider("", 0, 100, prog, key=f"admin_{pilar}", label_visibility="collapsed")
                if novo_prog != prog:
                    atualizar_progresso(pilar, novo_prog, user_email)
                    st.success(f"Progresso de {pilar} atualizado!")
                    st.rerun()

st.divider()
st.caption("💡 **Roadmap Vivo:** Este documento é atualizado em tempo real com base nas contribuições do time.")
st.caption("📅 **Próxima revisão:** Última sexta-feira do mês | 👥 **Participantes:** Todo o time de AE")