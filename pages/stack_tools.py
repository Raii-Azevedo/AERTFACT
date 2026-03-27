import streamlit as st
from allowed_emails import can_edit
from database import get_connection, return_connection

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.menu import render_sidebar

if not st.session_state.get("authenticated", False):
    st.switch_page("app.py")

st.set_page_config(page_title="Stack de Ferramentas", page_icon="🛠️", layout="wide", initial_sidebar_state="expanded")

render_sidebar()

user_email = st.session_state.get("user_email", "")
can_edit_content = can_edit(user_email)

st.title("🛠️ Stack de Ferramentas")
st.markdown("*Ferramentas homologadas para o time de Analytics Engineering*")

# Botão para adicionar ferramenta
if can_edit_content:
    if st.button("➕ Adicionar Nova Ferramenta", use_container_width=False):
        st.session_state.show_tool_form = True

# Formulário para nova ferramenta
if st.session_state.get("show_tool_form", False) and can_edit_content:
    with st.form("nova_ferramenta_form", clear_on_submit=True):
        st.subheader("🛠️ Adicionar Nova Ferramenta")
        
        nome = st.text_input("Nome da Ferramenta*")
        
        col1, col2 = st.columns(2)
        with col1:
            categoria = st.selectbox("Categoria*", ["Modelagem", "ETL", "Visualização", "Utilitários"])
        with col2:
            nivel = st.selectbox("Nível", ["Iniciante", "Intermediário", "Avançado"])
        
        versao = st.text_input("Versão", placeholder="ex: 3.0")
        descricao = st.text_area("Descrição", height=100)
        documentacao = st.text_input("Link da Documentação", placeholder="https://...")
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("💾 Salvar", use_container_width=True, type="primary")
        with col2:
            if st.form_submit_button("❌ Cancelar", use_container_width=True):
                st.session_state.show_tool_form = False
                st.rerun()
        
        if submitted:
            if nome and categoria:
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO ferramentas (nome, categoria, versao, descricao, nivel, documentacao_link, autor, autor_email)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (nome, categoria, versao, descricao, nivel, documentacao, 
                          st.session_state.get("user_name", ""), user_email))
                    conn.commit()
                    cursor.close()
                    return_connection(conn)
                    st.success("✅ Ferramenta adicionada com sucesso!")
                    st.session_state.show_tool_form = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")
            else:
                st.warning("⚠️ Preencha os campos obrigatórios")
    
    st.divider()

# Buscar ferramentas do banco
conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT * FROM ferramentas ORDER BY data_criacao DESC")
ferramentas_db = cursor.fetchall()
cursor.close()
return_connection(conn)

# Organizar por categoria
categorias = ["Modelagem", "ETL", "Visualização", "Utilitários"]

for categoria in categorias:
    ferramentas_cat = [f for f in ferramentas_db if f[2] == categoria]
    
    if ferramentas_cat:
        st.subheader(f"### {categoria}")
        
        cols = st.columns(2)
        for idx, ferramenta in enumerate(ferramentas_cat):
            with cols[idx % 2]:
                with st.container(border=True):
                    st.markdown(f"**{ferramenta[1]}**")
                    if ferramenta[3]:
                        st.caption(f"Versão: {ferramenta[3]}")
                    st.markdown(ferramenta[4] or "Sem descrição")
                    if ferramenta[5]:
                        st.caption(f"📊 Nível: {ferramenta[5]}")
                    if ferramenta[6]:
                        st.markdown(f"[📚 Documentação]({ferramenta[6]})")
                    st.caption(f"👤 Adicionado por: {ferramenta[8]}")
                    
                    if can_edit_content:
                        if st.button(f"🗑️ Remover", key=f"del_tool_{ferramenta[0]}"):
                            try:
                                conn = get_connection()
                                cursor = conn.cursor()
                                cursor.execute("DELETE FROM ferramentas WHERE id = ?", (ferramenta[0],))
                                conn.commit()
                                cursor.close()
                                return_connection(conn)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro: {e}")
    
    else:
        if categoria == "Modelagem":
            with st.container(border=True):
                st.info(f"Nenhuma ferramenta cadastrada na categoria {categoria}")
                if can_edit_content:
                    st.caption("Clique em 'Adicionar Nova Ferramenta' para começar!")