import streamlit as st
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.menu import render_sidebar

if not st.session_state.get("authenticated", False):
    st.switch_page("app.py")

st.set_page_config(page_title="Casos de Uso", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

render_sidebar()

st.title("📊 Casos de Uso e Soluções")
st.markdown("*Repositório de soluções reais implementadas pelo time*")

# Inicializar estado para formulário
if "show_form" not in st.session_state:
    st.session_state.show_form = False

# Filtros
st.subheader("🔍 Filtros")
col1, col2 = st.columns(2)

with col1:
    contexto_filtro = st.multiselect(
        "Contexto",
        ["Todos", "Performance", "Conectividade", "UX/UI", "Governança", "Segurança"],
        default=["Todos"]
    )

with col2:
    tecnologia_filtro = st.multiselect(
        "Tecnologia",
        ["Todos", "DAX", "Tabular Editor", "Python", "SQL", "Power Automate", "DAX Studio"],
        default=["Todos"]
    )

# Botões
col1, col2 = st.columns([6, 1])
with col2:
    if st.button("➕ Novo Caso", use_container_width=True):
        st.session_state.show_form = not st.session_state.show_form

# Formulário para novo caso
if st.session_state.show_form:
    with st.form("novo_caso", clear_on_submit=True):
        st.subheader("📝 Adicionar Novo Caso")
        
        titulo = st.text_input("Título do Caso*")
        
        col1, col2 = st.columns(2)
        with col1:
            contexto = st.selectbox("Contexto*", ["Performance", "Conectividade", "UX/UI", "Governança", "Segurança"])
        with col2:
            tecnologia = st.selectbox("Tecnologia*", ["DAX", "Tabular Editor", "Python", "SQL", "Power Automate", "DAX Studio"])
        
        descricao = st.text_area("Descrição da Solução*", height=100)
        resultado = st.text_area("Resultados Alcançados*", height=100)
        
        tags = st.text_input("Tags (separadas por vírgula)", placeholder="ex: otimização, performance, dax")
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("💾 Salvar Caso", use_container_width=True, type="primary")
        with col2:
            if st.form_submit_button("❌ Cancelar", use_container_width=True):
                st.session_state.show_form = False
                st.rerun()
        
        if submitted:
            st.success("✅ Caso adicionado com sucesso!")
            st.session_state.show_form = False
            st.rerun()
    
    st.divider()

# Lista de casos
casos = [
    {
        "titulo": "Otimização de modelo com 50M+ linhas",
        "contexto": "Performance",
        "tecnologia": "DAX",
        "descricao": "Redução do tempo de refresh de 4h para 45min através de otimização de medidas e particionamento",
        "resultado": "70% de redução no tempo de processamento",
        "data": "2025-03-20",
        "autor": "Rafael Mendes",
        "tags": ["otimização", "performance", "dax"]
    },
    {
        "titulo": "Automação de validação de dados com Python",
        "contexto": "Governança",
        "tecnologia": "Python",
        "descricao": "Script que valida automaticamente a integridade dos dados antes do refresh",
        "resultado": "Redução de 90% nos erros de dados",
        "data": "2025-03-15",
        "autor": "Carolina Lima",
        "tags": ["automação", "python", "validação"]
    },
    {
        "titulo": "Criação de medidas dinâmicas com Tabular Editor",
        "contexto": "UX/UI",
        "tecnologia": "Tabular Editor",
        "descricao": "Script C# para criar automaticamente medidas de time intelligence",
        "resultado": "80% de redução no tempo de desenvolvimento",
        "data": "2025-03-10",
        "autor": "Thiago Souza",
        "tags": ["c#", "tabular editor", "automação"]
    }
]

# Exibir casos
for idx, caso in enumerate(casos):
    with st.container(border=True):
        st.markdown(f"### {caso['titulo']}")
        st.markdown(f"**📌 Contexto:** {caso['contexto']} | **🛠️ Tecnologia:** {caso['tecnologia']}")
        st.markdown(f"**📝 Descrição:** {caso['descricao']}")
        st.markdown(f"**🎯 Resultados:** {caso['resultado']}")
        st.markdown(f"🏷️ **Tags:** {', '.join(caso['tags'])}")
        st.caption(f"👤 {caso['autor']} | 📅 {caso['data']}")
        
        if st.button("🔍 Ver detalhes", key=f"details_{idx}"):
            st.info(f"Case completo: {caso['titulo']}\n\nDetalhes técnicos em desenvolvimento...")