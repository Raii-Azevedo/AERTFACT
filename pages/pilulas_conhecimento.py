import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.menu import render_sidebar
from datetime import datetime
from allowed_emails import can_edit
from database import get_connection, return_connection

if not st.session_state.get("authenticated", False):
    st.switch_page("app.py")

st.set_page_config(page_title="Pílulas de Conhecimento", page_icon="🎥", layout="wide", initial_sidebar_state="expanded")

render_sidebar()

user_email = st.session_state.get("user_email", "")
can_edit_content = can_edit(user_email)

st.title("🎥 Pílulas de Conhecimento")
st.markdown("*Vídeos curtos de 5-10 minutos com cases práticos*")

# Filtros
st.subheader("🔍 Filtros")
col1, col2, col3 = st.columns(3)

with col1:
    tema = st.selectbox("Tema", ["Todos", "DAX", "Tabular Editor", "Python/SQL", "Power Automate", "Performance"])

with col2:
    nivel = st.selectbox("Nível", ["Todos", "Iniciante", "Intermediário", "Avançado"])

with col3:
    duracao = st.selectbox("Duração", ["Todos", "Até 5 min", "5-10 min", "10-15 min"])

st.divider()

# Botão para adicionar vídeo (apenas para editores)
if can_edit_content:
    if st.button("📹 + Adicionar Nova Pílula", use_container_width=False):
        st.session_state.show_video_form = True

# Formulário para novo vídeo
if st.session_state.get("show_video_form", False) and can_edit_content:
    with st.form("novo_video_form", clear_on_submit=True):
        st.subheader("📝 Adicionar Nova Pílula")
        
        titulo = st.text_input("Título do Vídeo*")
        descricao = st.text_area("Descrição", height=100)
        
        col1, col2 = st.columns(2)
        with col1:
            tema_video = st.selectbox("Tema*", ["DAX", "Tabular Editor", "Python/SQL", "Power Automate", "Performance"])
        with col2:
            nivel_video = st.selectbox("Nível*", ["Iniciante", "Intermediário", "Avançado"])
        
        col1, col2 = st.columns(2)
        with col1:
            duracao_video = st.text_input("Duração", placeholder="ex: 8:32")
        with col2:
            youtube_id = st.text_input("ID do YouTube", placeholder="ex: dQw4w9WgXcQ")
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("💾 Salvar Vídeo", use_container_width=True, type="primary")
        with col2:
            if st.form_submit_button("❌ Cancelar", use_container_width=True):
                st.session_state.show_video_form = False
                st.rerun()
        
        if submitted:
            if titulo and tema_video:
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO videos (titulo, descricao, tema, nivel, duracao, youtube_id, autor, autor_email)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (titulo, descricao, tema_video, nivel_video, duracao_video, youtube_id, 
                          st.session_state.get("user_name", ""), user_email))
                    conn.commit()
                    cursor.close()
                    return_connection(conn)
                    st.success("✅ Vídeo adicionado com sucesso!")
                    st.session_state.show_video_form = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")
            else:
                st.warning("⚠️ Preencha os campos obrigatórios")
    
    st.divider()

# Buscar vídeos do banco
conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT * FROM videos ORDER BY data_criacao DESC")
videos_db = cursor.fetchall()
cursor.close()
return_connection(conn)

if videos_db:
    # Converter para lista de dicionários
    videos = []
    for v in videos_db:
        videos.append({
            "id": v[0],
            "titulo": v[1],
            "descricao": v[2],
            "tema": v[3],
            "nivel": v[4],
            "duracao": v[5],
            "youtube_id": v[6],
            "autor": v[8],
            "data": v[10]
        })
    
    # Aplicar filtros
    if tema != "Todos":
        videos = [v for v in videos if v["tema"] == tema]
    if nivel != "Todos":
        videos = [v for v in videos if v["nivel"] == nivel]
    
    # Exibir vídeos em grid
    cols = st.columns(3)
    
    for idx, video in enumerate(videos):
        with cols[idx % 3]:
            with st.container(border=True):
                # Thumbnail
                if video.get("youtube_id"):
                    st.image(f"https://img.youtube.com/vi/{video['youtube_id']}/mqdefault.jpg", 
                            use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/320x180.png?text=Em+Breve", 
                            use_container_width=True)
                
                st.markdown(f"### {video['titulo']}")
                st.caption(f"🎯 {video['tema']} | 📊 {video['nivel']} | ⏱️ {video.get('duracao', 'N/A')}")
                st.markdown(video.get("descricao", "Sem descrição")[:100] + "...")
                st.caption(f"👤 {video['autor']} | 📅 {video['data'][:10] if video['data'] else 'N/A'}")
                
                if video.get("youtube_id"):
                    if st.button(f"▶️ Assistir", key=f"watch_{video['id']}"):
                        st.video(f"https://www.youtube.com/watch?v={video['youtube_id']}")
                
                # Botão de remover para admin/editor
                if can_edit_content:
                    if st.button(f"🗑️ Remover", key=f"del_{video['id']}"):
                        try:
                            conn = get_connection()
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM videos WHERE id = ?", (video['id'],))
                            conn.commit()
                            cursor.close()
                            return_connection(conn)
                            st.success("Vídeo removido!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro: {e}")
else:
    st.info("📹 Nenhuma pílula cadastrada ainda. Seja o primeiro a contribuir!")
    
    if can_edit_content:
        st.markdown("""
        **Como contribuir:**
        1. Clique no botão "+ Adicionar Nova Pílula"
        2. Preencha as informações do vídeo
        3. Adicione o ID do YouTube (ex: dQw4w9WgXcQ)
        4. Compartilhe seu conhecimento com o time!
        """)