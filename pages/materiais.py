import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.menu import render_sidebar
import pandas as pd
from datetime import datetime
from allowed_emails import can_edit, is_admin
from database import get_connection, return_connection

# Verificar autenticação
if not st.session_state.get("authenticated", False):
    st.switch_page("app.py")

st.set_page_config(
    page_title="Biblioteca de Materiais - AE Knowledge Hub",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Renderizar menu lateral
render_sidebar()

# Obter permissões
user_email = st.session_state.get("user_email", "")
can_edit_content = can_edit(user_email)
is_admin_user = is_admin(user_email)

st.title("📚 Biblioteca de Materiais de Referência")
st.markdown("""
*Livros, cursos, artigos, vídeos e ferramentas essenciais para Analytics Engineering*
""")

# Inicializar session state para formulários
if "show_material_form" not in st.session_state:
    st.session_state.show_material_form = False

# ============================================
# SEÇÃO DE BUSCA E FILTROS
# ============================================
st.subheader("🔍 Buscar Materiais")

col1, col2, col3, col4 = st.columns(4)

with col1:
    busca_texto = st.text_input("🔎 Buscar por título ou descrição", placeholder="ex: Power BI, Python, DAX...")

with col2:
    # Obter tipos únicos do banco
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT tipo FROM materiais ORDER BY tipo")
    tipos = [row[0] for row in cursor.fetchall() if row[0]]
    cursor.close()
    return_connection(conn)
    
    tipo_filtro = st.selectbox("📄 Tipo", ["Todos"] + tipos)

with col3:
    # Obter tópicos únicos
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT topicos FROM materiais WHERE topicos IS NOT NULL AND topicos != ''")
    topicos_raw = cursor.fetchall()
    cursor.close()
    return_connection(conn)
    
    # Processar tópicos (podem ter múltiplos separados por ;)
    todos_topicos = set()
    for t in topicos_raw:
        if t[0]:
            for topico in str(t[0]).split(';'):
                todos_topicos.add(topico.strip())
    
    topico_filtro = st.selectbox("🏷️ Tópico", ["Todos"] + sorted(list(todos_topicos)))

with col4:
    ordenar = st.selectbox("📊 Ordenar por", ["Mais recentes", "Mais antigos", "Título (A-Z)"])

st.divider()

# ============================================
# BOTÃO PARA ADICIONAR NOVO MATERIAL
# ============================================
if can_edit_content:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("➕ Adicionar Novo Material", use_container_width=True, type="primary"):
            st.session_state.show_material_form = not st.session_state.show_material_form

# ============================================
# FORMULÁRIO PARA NOVO MATERIAL
# ============================================
if st.session_state.get("show_material_form", False) and can_edit_content:
    with st.form("novo_material_form", clear_on_submit=True):
        st.subheader("📝 Adicionar Novo Material")
        
        col1, col2 = st.columns(2)
        
        with col1:
            titulo = st.text_input("Título*", placeholder="ex: O'Reilly - Python for Data Analysis")
            tipo = st.selectbox("Tipo*", [
                "PDF", "Blog Post", "Website", "E-book", "Tutorial", 
                "LinkedIn Post", "Podcast", "Video", "Internal Material", "Other"
            ])
            topicos = st.text_input("Tópicos (separados por vírgula)", placeholder="ex: Python, Data Analysis, Pandas")
        
        with col2:
            url = st.text_input("URL (se aplicável)", placeholder="https://...")
            autor = st.text_input("Autor/Criador", value=st.session_state.get("user_name", ""))
        
        descricao = st.text_area("Descrição*", height=100, placeholder="Descreva o conteúdo e sua relevância...")
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("💾 Salvar Material", use_container_width=True, type="primary")
        with col2:
            if st.form_submit_button("❌ Cancelar", use_container_width=True):
                st.session_state.show_material_form = False
                st.rerun()
        
        if submitted:
            if titulo and descricao:
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO materiais (titulo, tipo, topicos, descricao, url, autor, autor_email)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (titulo, tipo, topicos, descricao, url, autor, user_email))
                    conn.commit()
                    cursor.close()
                    return_connection(conn)
                    st.success("✅ Material adicionado com sucesso!")
                    st.session_state.show_material_form = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")
            else:
                st.warning("⚠️ Preencha título e descrição")
    
    st.divider()

# ============================================
# BUSCAR MATERIAIS NO BANCO
# ============================================
conn = get_connection()
cursor = conn.cursor()

# Construir query com filtros
query = "SELECT * FROM materiais WHERE 1=1"
params = []

if busca_texto:
    query += " AND (titulo LIKE ? OR descricao LIKE ?)"
    params.extend([f"%{busca_texto}%", f"%{busca_texto}%"])

if tipo_filtro != "Todos":
    query += " AND tipo = ?"
    params.append(tipo_filtro)

if topico_filtro != "Todos":
    query += " AND topicos LIKE ?"
    params.append(f"%{topico_filtro}%")

# Ordenação
if ordenar == "Mais recentes":
    query += " ORDER BY data_criacao DESC"
elif ordenar == "Mais antigos":
    query += " ORDER BY data_criacao ASC"
else:
    query += " ORDER BY titulo ASC"

cursor.execute(query, params)
materiais = cursor.fetchall()
cursor.close()
return_connection(conn)

# ============================================
# EXIBIR RESULTADOS
# ============================================
st.subheader(f"📖 {len(materiais)} materiais encontrados")

# Estatísticas rápidas
if materiais:
    tipos_count = {}
    for m in materiais:
        tipo = m[2] if m[2] else "Outros"
        tipos_count[tipo] = tipos_count.get(tipo, 0) + 1
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📄 PDFs", tipos_count.get("PDF", 0))
    with col2:
        st.metric("📝 Blog Posts", tipos_count.get("Blog Post", 0))
    with col3:
        st.metric("🌐 Websites", tipos_count.get("Website", 0))
    with col4:
        st.metric("📚 E-books", tipos_count.get("E-book", 0))

st.divider()

# Exibir materiais em cards
for material in materiais:
    material_id = material[0]
    titulo = material[1]
    tipo = material[2] or "Outro"
    topicos = material[3] or ""
    descricao = material[4] or ""
    url = material[5] or ""
    autor = material[6] or "Desconhecido"
    data_criacao = material[8][:10] if material[8] else "N/A"
    
    # Ícone baseado no tipo
    icone = {
        "PDF": "📄", "Blog Post": "📝", "Website": "🌐", "E-book": "📚",
        "Tutorial": "🎓", "LinkedIn Post": "🔗", "Podcast": "🎙️", 
        "Video": "🎥", "Internal Material": "🏢", "Other": "📌"
    }.get(tipo, "📌")
    
    with st.container(border=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(f"### {icone} {titulo}")
            st.markdown(f"**Tipo:** {tipo} | **📅 {data_criacao}** | **👤 {autor}**")
            
            if topicos:
                tags = [t.strip() for t in topicos.split(',') if t.strip()]
                st.markdown("**🏷️ Tags:** " + " ".join([f"`{tag}`" for tag in tags[:5]]))
            
            st.markdown(descricao[:200] + ("..." if len(descricao) > 200 else ""))
            
            if url and "http" in url:
                st.markdown(f"[🔗 Acessar material]({url})")
        
        with col2:
            if can_edit_content:
                if st.button("✏️ Editar", key=f"edit_{material_id}"):
                    st.session_state[f"edit_material_{material_id}"] = True
                
                if st.button("🗑️ Excluir", key=f"del_{material_id}"):
                    try:
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM materiais WHERE id = ?", (material_id,))
                        conn.commit()
                        cursor.close()
                        return_connection(conn)
                        st.success("Material removido!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")
            
            # Botão para copiar link
            if url:
                st.button("📋 Copiar Link", key=f"copy_{material_id}", 
                         on_click=lambda: st.info("Link copiado!"))
        
        # Formulário de edição (se ativado)
        if can_edit_content and st.session_state.get(f"edit_material_{material_id}", False):
            with st.form(f"edit_form_{material_id}"):
                st.subheader("✏️ Editar Material")
                
                novo_titulo = st.text_input("Título", value=titulo)
                novo_tipo = st.selectbox("Tipo", ["PDF", "Blog Post", "Website", "E-book", "Tutorial", "Other"], 
                                        index=["PDF", "Blog Post", "Website", "E-book", "Tutorial", "Other"].index(tipo) if tipo in ["PDF", "Blog Post", "Website", "E-book", "Tutorial", "Other"] else 0)
                novos_topicos = st.text_input("Tópicos", value=topicos)
                nova_descricao = st.text_area("Descrição", value=descricao, height=100)
                nova_url = st.text_input("URL", value=url)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("💾 Salvar Alterações"):
                        try:
                            conn = get_connection()
                            cursor = conn.cursor()
                            cursor.execute("""
                                UPDATE materiais 
                                SET titulo = ?, tipo = ?, topicos = ?, descricao = ?, url = ?, data_atualizacao = CURRENT_TIMESTAMP
                                WHERE id = ?
                            """, (novo_titulo, novo_tipo, novos_topicos, nova_descricao, nova_url, material_id))
                            conn.commit()
                            cursor.close()
                            return_connection(conn)
                            st.success("Material atualizado!")
                            st.session_state[f"edit_material_{material_id}"] = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro: {e}")
                with col2:
                    if st.form_submit_button("❌ Cancelar"):
                        st.session_state[f"edit_material_{material_id}"] = False
                        st.rerun()

# ============================================
# FOOTER COM ESTATÍSTICAS
# ============================================
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    st.caption(f"📊 Total de materiais: {len(materiais)}")
with col2:
    st.caption("💡 **Dica:** Use as tags para encontrar conteúdos relacionados")
with col3:
    if can_edit_content:
        st.caption("✏️ **Editores podem adicionar, editar e remover materiais")

# ============================================
# SEÇÃO DE MATERIAIS EM DESTAQUE (Opcional)
# ============================================
with st.expander("⭐ Materiais em Destaque", expanded=False):
    st.markdown("""
    ### Recomendações da Equipe
    
    | Material | Tipo | Por que ler? |
    |----------|------|--------------|
    | **The Data Warehouse Toolkit** (Kimball) | Livro | A bíblia da modelagem dimensional - essencial para qualquer Analytics Engineer |
    | **Designing Data-Intensive Applications** | Livro | Fundamentos de arquitetura de dados para sistemas escaláveis |
    | **Storytelling with Data** | Livro | Como comunicar insights de forma eficaz e impactante |
    | **Fundamentos de Engenharia de Dados** (O'Reilly) | Livro | Guia completo para iniciantes em engenharia de dados |
    | **dbt Analytics Engineer Certification** | Certificação | Validação oficial do conhecimento em dbt |
    """)