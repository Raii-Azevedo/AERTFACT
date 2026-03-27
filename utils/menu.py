import streamlit as st
from datetime import datetime
import sys
import os

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from allowed_emails import can_edit, is_admin


def render_sidebar():
    """Renderiza o menu lateral estilizado para todas as páginas"""
    with st.sidebar:
        st.title("🚀 AE Knowledge Hub")

        # Informações do usuário
        user_email = st.session_state.get("user_email", "")
        user_name = st.session_state.get("user_name", "Usuário")

        st.markdown(f"**Olá, {user_name}!**")
        st.caption(f"📧 {user_email}")

        st.divider()

        # Menu de navegação
        st.subheader("📂 Navegação")

        # Dashboard
        if st.button("🏠 Dashboard", use_container_width=True, key="menu_dashboard"):
            st.switch_page("pages/dashboard.py")

        # Casos de Uso
        if st.button("📊 Casos de Uso", use_container_width=True, key="menu_casos"):
            st.switch_page("pages/casos_de_uso.py")

        # Boas Práticas
        if st.button("📖 Boas Práticas", use_container_width=True, key="menu_praticas"):
            st.switch_page("pages/boas_praticas.py")

        # Stack de Ferramentas
        if st.button("🛠️ Stack de Ferramentas", use_container_width=True, key="menu_stack"):
            st.switch_page("pages/stack_tools.py")

        # Pílulas de Conhecimento
        if st.button("🎥 Pílulas de Conhecimento", use_container_width=True, key="menu_pilulas"):
            st.switch_page("pages/pilulas_conhecimento.py")

        # AE do Mês
        if st.button("🏆 AE do Mês", use_container_width=True, key="menu_ae_mes"):
            st.switch_page("pages/ae_do_mes.py")

        # Roadmap
        if st.button("🗺️ Roadmap", use_container_width=True, key="menu_roadmap"):
            st.switch_page("pages/roadmap.py")

        # Materiais (se existir)
        if os.path.exists("pages/materiais.py"):
            if st.button("📚 Materiais", use_container_width=True, key="menu_materiais"):
                st.switch_page("pages/materiais.py")

        # ========== NOVO: IMPORTAR DADOS ==========
        # Importar Dados (apenas para admin)
        if is_admin(user_email):
            if st.button("📥 Importar Dados", use_container_width=True, key="menu_importar"):
                st.switch_page("pages/importar_dados.py")

        st.divider()

        # Área administrativa (apenas para admins)
        
        if is_admin(user_email):
            st.subheader("⚙️ Administração")
            if st.button("👥 Gerenciar Usuários", use_container_width=True, key="menu_admin_users"):
                st.switch_page("pages/admin_usuarios.py")

        # Logout
        st.divider()
        if st.button("🚪 Logout", use_container_width=True, key="menu_logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.switch_page("app.py")