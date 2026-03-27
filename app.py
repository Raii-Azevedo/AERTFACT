import streamlit as st
from datetime import datetime
import sys
import os
import pandas as pd
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.menu import render_sidebar
from allowed_emails import can_edit, is_admin
from database import get_connection, return_connection, DB_TYPE

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
user_role = st.session_state.get("user_role", "")
is_admin_user = is_admin(user_email)
can_edit_content = can_edit(user_email)  # user e admin podem editar

st.title("🚀 Roadmap de Implementação")
st.markdown("""
*Estratégia e cronograma para transformar o conhecimento tácito em ativos digitais estruturados*
""")

# Mostrar badge de permissão
if is_admin_user:
    st.info("🔐 **Modo Admin:** Você pode editar todo o conteúdo do roadmap.")
elif can_edit_content:
    st.info("✏️ **Modo Editor:** Você pode atualizar progressos e adicionar entregas.")
else:
    st.info("👁️ **Modo Visualização:** Apenas visualização. Para editar, solicite acesso de administrador.")

st.divider()

def get_placeholder():
    return '%s' if DB_TYPE == 'postgresql' else '?'

# ============================================
# FUNÇÕES PARA GERENCIAR DADOS DO ROADMAP
# ============================================

def criar_tabelas_roadmap():
    """Cria as tabelas necessárias para o roadmap"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
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
        
        # Inserir dados iniciais se não existirem
        cursor.execute("SELECT COUNT(*) FROM roadmap_progresso")
        if cursor.fetchone()[0] == 0:
            progressos_iniciais = [
                ("Pilar A: Casos de Uso", 75, "50 casos até Jun/25", "system"),
                ("Pilar B: Boas Práticas", 60, "8 checklists completos", "system"),
                ("Pilar C: Stack de Ferramentas", 85, "50+ ferramentas catalogadas", "system"),
                ("Pilar D: Biblioteca", 40, "200+ materiais catalogados", "system"),
                ("Pilar E: Treinamento", 35, "20 pílulas + playlist", "system"),
                ("Pilar F: Gamificação", 70, "Sistema de pontos e badges", "system")
            ]
            for pilar, prog, meta, autor in progressos_iniciais:
                if DB_TYPE == 'postgresql':
                    cursor.execute("""
                        INSERT INTO roadmap_progresso (pilar, progresso, meta, atualizado_por)
                        VALUES (%s, %s, %s, %s)
                    """, (pilar, prog, meta, autor))
                else:
                    cursor.execute("""
                        INSERT INTO roadmap_progresso (pilar, progresso, meta, atualizado_por)
                        VALUES (?, ?, ?, ?)
                    """, (pilar, prog, meta, autor))
        
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
        return True
    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")
        return False

def get_progresso_pilares():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT pilar, progresso, meta FROM roadmap_progresso ORDER BY id")
    resultados = cursor.fetchall()
    cursor.close()
    return_connection(conn)
    return resultados

def atualizar_progresso(pilar, novo_progresso, user_email):
    if not can_edit_content:
        return False
    conn = get_connection()
    cursor = conn.cursor()
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
    return True

def get_entregas():
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
    if not can_edit_content:
        return False
    conn = get_connection()
    cursor = conn.cursor()
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
    return True

def remover_entrega(entrega_id):
    if not can_edit_content:
        return False
    conn = get_connection()
    cursor = conn.cursor()
    if DB_TYPE == 'postgresql':
        cursor.execute("DELETE FROM roadmap_entregas WHERE id = %s", (entrega_id,))
    else:
        cursor.execute("DELETE FROM roadmap_entregas WHERE id = ?", (entrega_id,))
    conn.commit()
    cursor.close()
    return_connection(conn)
    return True

def atualizar_status_entrega(entrega_id, novo_status):
    if not can_edit_content:
        return False
    conn = get_connection()
    cursor = conn.cursor()
    if DB_TYPE == 'postgresql':
        cursor.execute("UPDATE roadmap_entregas SET status = %s WHERE id = %s", (novo_status, entrega_id))
    else:
        cursor.execute("UPDATE roadmap_entregas SET status = ? WHERE id = ?", (novo_status, entrega_id))
    conn.commit()
    cursor.close()
    return_connection(conn)
    return True

def get_fases():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT fase, status, data_prevista, entregas FROM roadmap_fases ORDER BY id")
    resultados = cursor.fetchall()
    cursor.close()
    return_connection(conn)
    return resultados

def atualizar_fase(fase, novo_status, user_email):
    if not can_edit_content:
        return False
    conn = get_connection()
    cursor = conn.cursor()
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
    return True

# Inicializar tabelas
criar_tabelas_roadmap()

# ============================================
# SEÇÃO 2: PILARES E PROGRESSO
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
            
            # Apenas admin pode editar progresso
            if is_admin_user:
                novo_prog = st.slider("Ajustar", 0, 100, progresso, key=f"prog_{pilar}", label_visibility="collapsed")
                if novo_prog != progresso:
                    if st.button("💾 Salvar", key=f"save_{pilar}"):
                        atualizar_progresso(pilar, novo_prog, user_email)
                        st.rerun()

st.divider()

# ============================================
# SEÇÃO 3: CRONOGRAMA DE EXECUÇÃO
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
            # Apenas admin pode editar status das fases
            if is_admin_user:
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
# SEÇÃO 6: PRÓXIMAS ENTREGAS
# ============================================
st.subheader("📋 Próximas Entregas")

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
                # Apenas admin pode editar status e remover entregas
                if is_admin_user:
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
                    status_emoji = {"pendente": "⏳", "em andamento": "🔄", "concluído": "✅"}.get(status, "📌")
                    st.markdown(f"{status_emoji} {status}")
else:
    st.info("Nenhuma entrega cadastrada ainda.")

# ============================================
# SEÇÃO ADMIN (APENAS PARA ADMIN)
# ============================================
if is_admin_user:
    st.divider()
    with st.expander("🔧 **Administração do Roadmap** (Apenas Administradores)", expanded=False):
        st.warning("⚠️ Área restrita para administradores")
        
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