import streamlit as st
from datetime import datetime
import sys
import os

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.menu import render_sidebar
from allowed_emails import can_edit
from database import get_connection, return_connection

# Verificar autenticação
if not st.session_state.get("authenticated", False):
    st.switch_page("app.py")

# Configurar a página
st.set_page_config(
    page_title="Dashboard - AE Knowledge Hub",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# IMPORTANTE: Renderizar o menu estilizado PRIMEIRO
# Isso vai criar o sidebar com nosso menu estilizado
render_sidebar()

# Obter dados do usuário
user_email = st.session_state.get("user_email", "")
can_edit_content = can_edit(user_email)

# Conteúdo principal
st.title("🚀 AE Knowledge Hub")
st.caption(f"Atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# KPIs - Buscar do banco
conn = get_connection()
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM casos_uso")
total_casos = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM videos")
total_videos = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM snippets")
total_snippets = cursor.fetchone()[0]

cursor.close()
return_connection(conn)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📚 Casos Documentados", total_casos, "↑ 3")
with col2:
    st.metric("👥 Contribuidores", "12", "↑ 2")
with col3:
    st.metric("🎥 Pílulas Produzidas", total_videos, "↑ 2")
with col4:
    st.metric("🏆 AE do Mês", "Rafael M.", "Março 2025")

st.divider()

# Seções principais
st.subheader("📂 Pilares do Conhecimento")

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.markdown("### 📊 Casos de Uso")
        st.markdown("Soluções reais implementadas pelo time")
        st.markdown(f"**Total:** {total_casos} casos documentados")
        if st.button("Explorar Casos →", key="btn_casos"):
            st.switch_page("pages/casos_de_uso.py")

with col2:
    with st.container(border=True):
        st.markdown("### 📖 Boas Práticas")
        st.markdown("Padrões e diretrizes do time")
        if st.button("Ver Guias →", key="btn_praticas"):
            st.switch_page("pages/boas_praticas.py")

with col3:
    with st.container(border=True):
        st.markdown("### 🛠️ Stack de Ferramentas")
        st.markdown("Ferramentas homologadas")
        if st.button("Ver Stack →", key="btn_stack"):
            st.switch_page("pages/stack_tools.py")

# Botão de contribuição para editores
if can_edit_content:
    st.divider()
    st.subheader("✨ Contribuir com o Hub")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("➕ Novo Caso", use_container_width=True):
            st.switch_page("pages/casos_de_uso.py")
    with col2:
        if st.button("🎥 Nova Pílula", use_container_width=True):
            st.switch_page("pages/pilulas_conhecimento.py")
    with col3:
        if st.button("⚡ Novo Snippet", use_container_width=True):
            if os.path.exists("pages/snippets.py"):
                st.switch_page("pages/snippets.py")
            else:
                st.info("Página de snippets em desenvolvimento")
    with col4:
        if st.button("🛠️ Nova Ferramenta", use_container_width=True):
            st.switch_page("pages/stack_tools.py")