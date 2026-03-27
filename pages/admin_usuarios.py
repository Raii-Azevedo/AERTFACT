import streamlit as st
import sys
import os
import pandas as pd
from datetime import datetime
import hashlib
import base64

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.menu import render_sidebar
from allowed_emails import (
    get_all_allowed_emails, remove_allowed_email, 
    is_admin, get_user_role, add_allowed_email
)
from database import get_connection, return_connection, adicionar_usuario_com_avatar, get_avatar_url, get_nome_usuario, DB_TYPE

# Verificar autenticação
if not st.session_state.get("authenticated", False):
    st.switch_page("app.py")

user_email = st.session_state.get("user_email", "")

if not is_admin(user_email):
    st.error("❌ Acesso negado. Esta página é restrita a administradores.")
    st.stop()

st.set_page_config(
    page_title="Admin - Gerenciar Usuários",
    page_icon="👥",
    layout="wide"
)

# Renderizar menu lateral
render_sidebar()

st.title("👥 Gerenciamento de Usuários")
st.markdown("*Adicione ou remova usuários autorizados a acessar o sistema*")

# ============================================
# FUNÇÃO PARA SALVAR AVATAR COMO BASE64
# ============================================

def salvar_avatar_base64(arquivo):
    """Salva a foto como base64 para armazenar no banco"""
    if arquivo:
        return base64.b64encode(arquivo.read()).decode('utf-8')
    return None

def exibir_avatar(avatar_base64, email, size=100):
    """Exibe avatar a partir do base64 ou gera Gravatar"""
    if avatar_base64:
        return f"data:image/png;base64,{avatar_base64}"
    else:
        email_hash = hashlib.md5(email.lower().encode()).hexdigest()
        return f"https://www.gravatar.com/avatar/{email_hash}?d=identicon&s={size}"

# ============================================
# FORMULÁRIO PARA ADICIONAR NOVO USUÁRIO COM FOTO
# ============================================
with st.container(border=True):
    st.subheader("➕ Adicionar Novo Usuário")
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_email = st.text_input("Email do usuário*", placeholder="nome.sobrenome@artefact.com")
        
        # Extrair nome automaticamente do email
        if new_email and "@" in new_email:
            nome_sugerido = new_email.split('@')[0].replace('.', ' ').title()
            new_nome = st.text_input("Nome completo", value=nome_sugerido)
        else:
            new_nome = st.text_input("Nome completo", placeholder="Nome Sobrenome")
        
        new_role = st.selectbox("Role*", 
                                ["viewer", "user", "admin"], 
                                help="viewer: só visualiza | user: pode editar | admin: pode gerenciar usuários")
    
    with col2:
        st.markdown("### 🖼️ Foto do Usuário")
        st.markdown("**Formatos:** JPG, PNG | **Tamanho:** até 2MB")
        
        new_avatar = st.file_uploader("Escolher foto", type=['jpg', 'jpeg', 'png'], key="avatar_upload")
        
        # Mostrar preview
        if new_avatar:
            st.image(new_avatar, width=150, caption="Preview da foto")
        else:
            # Mostrar preview do avatar padrão baseado no email
            if new_email:
                preview_url = f"https://www.gravatar.com/avatar/{hashlib.md5(new_email.lower().encode()).hexdigest()}?d=identicon&s=150"
                st.image(preview_url, width=150, caption="Avatar padrão (Gravatar)")
            else:
                st.info("👤 Informe o email para ver o preview")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("📧 Adicionar Usuário", type="primary", use_container_width=True):
            if new_email:
                # Verificar formato do email
                if "@artefact.com" in new_email or "admin@aehub.com" in new_email:
                    
                    # Salvar avatar como base64 se foi enviado
                    avatar_base64 = None
                    if new_avatar:
                        avatar_base64 = salvar_avatar_base64(new_avatar)
                        st.success("✅ Foto processada com sucesso!")
                    
                    # Adicionar usuário com avatar no banco
                    resultado = adicionar_usuario_com_avatar(
                        email=new_email,
                        role=new_role,
                        nome=new_nome,
                        avatar_file=avatar_base64,  # Agora armazenamos o base64
                        added_by=user_email
                    )
                    
                    if resultado:
                        st.success(f"✅ Usuário {new_email} adicionado com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Erro ao adicionar usuário")
                else:
                    st.warning("⚠️ O email deve ser do domínio @artefact.com")
            else:
                st.warning("⚠️ Informe o email")

st.divider()

# ============================================
# LISTA DE USUÁRIOS COM FOTOS
# ============================================
st.subheader("📋 Usuários Autorizados")

# Buscar todos os usuários com detalhes
conn = get_connection()
cursor = conn.cursor()
cursor.execute("""
    SELECT email, role, nome, avatar_file, added_by, added_at 
    FROM allowed_emails 
    ORDER BY 
        CASE role 
            WHEN 'admin' THEN 1 
            WHEN 'user' THEN 2 
            ELSE 3 
        END,
        nome
""")
usuarios = cursor.fetchall()
cursor.close()
return_connection(conn)

if usuarios:
    for usuario in usuarios:
        email = usuario[0]
        role = usuario[1]
        nome = usuario[2] if usuario[2] else email.split('@')[0].replace('.', ' ').title()
        avatar_base64 = usuario[3]
        added_by = usuario[4] if usuario[4] else "Sistema"
        added_at = usuario[5][:10] if usuario[5] else "N/A"
        
        with st.container(border=True):
            col1, col2, col3 = st.columns([1, 4, 2])
            
            with col1:
                # Exibir avatar
                avatar_url = exibir_avatar(avatar_base64, email, size=100)
                st.image(avatar_url, width=80)
            
            with col2:
                st.markdown(f"### {nome}")
                st.markdown(f"📧 {email}")
                
                # Badge de role
                if role.upper() == 'ADMIN':
                    st.markdown('<span style="background:#ff6b6b; color:white; padding:4px 12px; border-radius:20px;">🔴 ADMIN</span>', unsafe_allow_html=True)
                elif role.upper() == 'USER':
                    st.markdown('<span style="background:#4ecdc4; color:white; padding:4px 12px; border-radius:20px;">🟢 USER</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span style="background:#95a5a6; color:white; padding:4px 12px; border-radius:20px;">⚪ VIEWER</span>', unsafe_allow_html=True)
            
            with col3:
                st.caption(f"📅 Adicionado em: {added_at}")
                st.caption(f"👤 Por: {added_by}")
                
                # Botão de remover (não permitir remover admin principal ou a si mesmo)
                if email not in ['admin@aehub.com', user_email]:
                    if st.button(f"🗑️ Remover", key=f"del_{email}"):
                        if remove_allowed_email(email):
                            st.success(f"✅ Usuário {email} removido!")
                            st.rerun()
else:
    st.info("Nenhum usuário cadastrado além do admin.")

st.divider()

# ============================================
# EDITAR PERFIL DO USUÁRIO LOGADO
# ============================================
with st.expander("✏️ Editar Meu Perfil"):
    st.subheader("Atualizar sua foto de perfil")
    
    # Buscar dados do usuário atual
    conn = get_connection()
    cursor = conn.cursor()
    placeholder = '%s' if DB_TYPE.lower() == 'postgresql' else '?'
    cursor.execute(f"SELECT nome, avatar_file FROM allowed_emails WHERE email = {placeholder}", (user_email,))
    dados = cursor.fetchone()
    cursor.close()
    return_connection(conn)
    
    nome_atual = dados[0] if dados else user_email.split('@')[0].replace('.', ' ').title()
    avatar_atual = dados[1] if dados else None
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Foto atual:**")
        avatar_url = exibir_avatar(avatar_atual, user_email, size=150)
        st.image(avatar_url, width=150)
        st.caption(f"**Nome:** {nome_atual}")
        st.caption(f"**Email:** {user_email}")
    
    with col2:
        st.markdown("**Alterar foto:**")
        nova_foto = st.file_uploader("Escolher nova foto", type=['jpg', 'jpeg', 'png'], key="edit_avatar")
        
        if nova_foto:
            st.image(nova_foto, width=150, caption="Nova foto")
            
            if st.button("💾 Salvar nova foto", type="primary"):
                # Salvar como base64
                novo_avatar_base64 = salvar_avatar_base64(nova_foto)
                
                # Atualizar banco
                conn = get_connection()
                cursor = conn.cursor()
                placeholder = '%s' if DB_TYPE.lower() == 'postgresql' else '?'
                cursor.execute(f"UPDATE allowed_emails SET avatar_file = {placeholder} WHERE email = {placeholder}",
                             (novo_avatar_base64, user_email))
                conn.commit()
                cursor.close()
                return_connection(conn)
                
                st.success("✅ Foto atualizada com sucesso!")
                st.rerun()

st.divider()
st.caption("💡 **Dica:** Apenas usuários com role 'admin' podem gerenciar outros usuários.")
st.caption("📸 **Fotos:** As fotos são armazenadas diretamente no banco de dados (base64), garantindo persistência.")