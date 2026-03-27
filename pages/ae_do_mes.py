import streamlit as st
from datetime import datetime
import sys
import os
import hashlib
import time

# NO INÍCIO DE CADA PÁGINA
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.menu import render_sidebar
from allowed_emails import get_all_allowed_emails, is_admin, get_user_role
from database import get_connection, return_connection, salvar_ae_mes_historico, get_historico_ae_mes, get_nome_usuario, get_avatar_url, DB_TYPE

st.set_page_config(page_title="AE do Mês", page_icon="🏆", layout="wide", initial_sidebar_state="expanded")

if not st.session_state.get("authenticated", False):
    st.switch_page("app.py")

# Depois do set_page_config
render_sidebar()

st.title("🏆 AE do Mês")
st.caption("Reconhecendo quem mais contribui para o crescimento do time")

def get_placeholder():
    """Retorna o placeholder correto para cada banco"""
    return '%s' if DB_TYPE == 'postgresql' else '?'

# ============================================
# FUNÇÕES PARA CÁLCULO DE PONTUAÇÃO (OTIMIZADAS)
# ============================================

@st.cache_data(ttl=300)  # Cache para 5 minutos
def get_all_contributions():
    """Busca todas as contribuições de uma vez para evitar múltiplas queries"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Buscar todos os emails com contribuições de uma vez
    resultados = {
        'casos': {},
        'videos': {},
        'snippets': {},
        'ferramentas': {},
        'materiais': {}
    }
    
    try:
        # Casos de uso
        cursor.execute("SELECT autor_email, COUNT(*) FROM casos_uso GROUP BY autor_email")
        for row in cursor.fetchall():
            resultados['casos'][row[0]] = row[1]
        
        # Vídeos
        cursor.execute("SELECT autor_email, COUNT(*) FROM videos GROUP BY autor_email")
        for row in cursor.fetchall():
            resultados['videos'][row[0]] = row[1]
        
        # Snippets
        cursor.execute("SELECT autor_email, COUNT(*) FROM snippets GROUP BY autor_email")
        for row in cursor.fetchall():
            resultados['snippets'][row[0]] = row[1]
        
        # Ferramentas
        cursor.execute("SELECT autor_email, COUNT(*) FROM ferramentas GROUP BY autor_email")
        for row in cursor.fetchall():
            resultados['ferramentas'][row[0]] = row[1]
        
        # Materiais
        cursor.execute("SELECT autor_email, COUNT(*) FROM materiais GROUP BY autor_email")
        for row in cursor.fetchall():
            resultados['materiais'][row[0]] = row[1]
        
    except Exception as e:
        print(f"Erro ao buscar contribuições: {e}")
    
    cursor.close()
    return_connection(conn)
    return resultados

def calcular_pontuacao_rapida(autor_email, contribs_cache):
    """Calcula pontuação usando cache"""
    casos = contribs_cache['casos'].get(autor_email, 0)
    videos = contribs_cache['videos'].get(autor_email, 0)
    snippets = contribs_cache['snippets'].get(autor_email, 0)
    ferramentas = contribs_cache['ferramentas'].get(autor_email, 0)
    materiais = contribs_cache['materiais'].get(autor_email, 0)
    
    pontuacao = (casos * 10) + (videos * 15) + (snippets * 5) + (ferramentas * 8) + (materiais * 3)
    total_contribs = casos + videos + snippets + ferramentas + materiais
    
    return pontuacao, {
        'casos': casos,
        'videos': videos,
        'snippets': snippets,
        'ferramentas': ferramentas,
        'materiais': materiais
    }, total_contribs

# ============================================
# CARREGAMENTO DOS DADOS (COM SPINNER)
# ============================================

with st.spinner("🔄 Carregando dados dos contribuidores..."):
    # Buscar todos os usuários autorizados
    todos_usuarios = get_all_allowed_emails()
    
    # Buscar todas as contribuições de uma vez
    contribs_cache = get_all_contributions()
    
    # Processar contribuidores
    usuarios_contribuidores = []
    for usuario in todos_usuarios:
        email = usuario[0]
        role = usuario[1]
        nome = get_nome_usuario(email)
        
        # Incluir users e admins
        if role in ['user', 'admin']:
            pontuacao, detalhes, total_contribs = calcular_pontuacao_rapida(email, contribs_cache)
            
            usuarios_contribuidores.append({
                'email': email,
                'nome': nome,
                'role': role,
                'pontos': pontuacao,
                'contribuicoes': total_contribs,
                'detalhes': detalhes
            })
    
    # Ordenar por pontuação
    usuarios_contribuidores.sort(key=lambda x: x['pontos'], reverse=True)
    
    # Ranking final (apenas quem tem contribuições)
    ranking_com_contrib = [u for u in usuarios_contribuidores if u['contribuicoes'] > 0]
    
    st.success(f"✅ {len(ranking_com_contrib)} contribuidores carregados")

# ============================================
# TABS
# ============================================

tab_atual, tab_ranking, tab_historico = st.tabs(["🏆 AE Atual", "📊 Ranking", "📜 Hall da Fama"])

# ============================================
# TAB 1: AE ATUAL
# ============================================
with tab_atual:
    if ranking_com_contrib:
        ae_mes = ranking_com_contrib[0]  # Primeiro do ranking
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Buscar avatar do banco
            conn = get_connection()
            cursor = conn.cursor()
            placeholder = get_placeholder()
            cursor.execute(f"SELECT avatar_file, nome FROM allowed_emails WHERE email = {placeholder}", (ae_mes['email'],))
            dados = cursor.fetchone()
            cursor.close()
            return_connection(conn)
            
            avatar_file = dados[0] if dados else None
            nome_usuario = dados[1] if dados else ae_mes['nome']
            
            # Mostrar avatar
            if avatar_file:
                try:
                    st.image(avatar_file, width=200, caption=nome_usuario)
                except:
                    email_hash = hashlib.md5(ae_mes['email'].encode()).hexdigest()
                    avatar_url = f"https://www.gravatar.com/avatar/{email_hash}?d=identicon&s=200"
                    st.image(avatar_url, width=200, caption=nome_usuario)
            else:
                email_hash = hashlib.md5(ae_mes['email'].encode()).hexdigest()
                avatar_url = f"https://www.gravatar.com/avatar/{email_hash}?d=identicon&s=200"
                st.image(avatar_url, width=200, caption=nome_usuario)
            
            st.markdown('<div style="text-align: center; font-size: 3rem; margin-top: -30px;">👑</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        border-radius: 20px; padding: 25px; color: white;">
                <h2 style="color: white; margin-top: 0;">{nome_usuario}</h2>
                <p style="font-size: 1.2rem;">🏆 Analytics Engineer do Mês - {datetime.now().strftime('%B %Y')}</p>
                <p>⭐ Pontuação: {ae_mes['pontos']} pontos | 🎯 {ae_mes['contribuicoes']} contribuições</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Métricas de contribuição
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("📚 Cases", ae_mes['detalhes']['casos'])
        with col2:
            st.metric("🎥 Vídeos", ae_mes['detalhes']['videos'])
        with col3:
            st.metric("⚡ Snippets", ae_mes['detalhes']['snippets'])
        with col4:
            st.metric("🛠️ Ferramentas", ae_mes['detalhes']['ferramentas'])
        with col5:
            st.metric("📖 Materiais", ae_mes['detalhes']['materiais'])
        
        st.divider()
        
        # Depoimento
        st.subheader("💬 Depoimento")
        st.info(f"""
        "Parabéns {nome_usuario.split()[0]}! Suas contribuições estão fazendo a diferença no time.
        Continue compartilhando conhecimento e ajudando a construir um hub cada vez mais rico!"
        
        — Time de Analytics Engineering
        """)
    else:
        st.info("🏆 Ainda não há contribuições registradas. Seja o primeiro a contribuir!")

# ============================================
# TAB 2: RANKING
# ============================================
with tab_ranking:
    st.subheader(f"📊 Ranking de Pontuação - {datetime.now().strftime('%B %Y')}")
    
    if ranking_com_contrib:
        for idx, rank in enumerate(ranking_com_contrib[:10]):
            badge = ["🥇", "🥈", "🥉", "⭐", "⭐", "⭐", "⭐", "⭐", "⭐", "⭐"][idx] if idx < 10 else "📌"
            
            # Buscar avatar
            conn = get_connection()
            cursor = conn.cursor()
            placeholder = get_placeholder()
            cursor.execute(f"SELECT avatar_file FROM allowed_emails WHERE email = {placeholder}", (rank['email'],))
            dados = cursor.fetchone()
            cursor.close()
            return_connection(conn)
            avatar_file = dados[0] if dados else None
            
            col1, col2, col3, col4, col5 = st.columns([1, 4, 2, 2, 2])
            with col1:
                st.markdown(f"### {badge}")
            with col2:
                # Mostrar avatar pequeno
                if avatar_file:
                    try:
                        st.image(avatar_file, width=40)
                    except:
                        email_hash = hashlib.md5(rank['email'].encode()).hexdigest()
                        avatar_url = f"https://www.gravatar.com/avatar/{email_hash}?d=identicon&s=40"
                        st.image(avatar_url, width=40)
                else:
                    email_hash = hashlib.md5(rank['email'].encode()).hexdigest()
                    avatar_url = f"https://www.gravatar.com/avatar/{email_hash}?d=identicon&s=40"
                    st.image(avatar_url, width=40)
                st.markdown(f"**{rank['nome']}**")
                st.caption(f"{rank['email']}")
            with col3:
                st.markdown(f"🎯 {rank['pontos']} pontos")
            with col4:
                st.markdown(f"📚 {rank['contribuicoes']} contribuições")
            with col5:
                st.markdown(f"📊 {rank['detalhes']['casos']}C / {rank['detalhes']['videos']}V / {rank['detalhes']['snippets']}S")
            
            # Barra de progresso
            max_pontos = ranking_com_contrib[0]['pontos']
            st.progress(min(rank['pontos'] / max_pontos, 1.0))
    else:
        st.info("📊 Nenhuma contribuição registrada ainda. Comece a contribuir para aparecer no ranking!")

# ============================================
# TAB 3: HALL DA FAMA
# ============================================
with tab_historico:
    st.subheader("🏅 Hall da Fama")
    
    # Buscar histórico do banco
    historico = get_historico_ae_mes()
    
    if historico:
        st.markdown("### 🎖️ Últimos AE do Mês")
        
        for item in historico[:5]:
            with st.container(border=True):
                col1, col2, col3 = st.columns([1, 3, 2])
                with col1:
                    st.markdown(f"### 🏆")
                with col2:
                    st.markdown(f"**{item[0]}**")
                    st.caption(f"{item[1]}/{item[2]}")
                with col3:
                    st.markdown(f"🎯 {item[3]} pontos")
                st.caption(f"📅 Definido em: {str(item[5])[:10] if item[5] else 'N/A'}")
    else:
        st.info("📜 Histórico ainda não disponível. Os AE do Mês aparecerão aqui.")
    
    st.divider()
    
    # Top contribuidores de todos os tempos
    st.markdown("### 🎖️ Maiores Contribuidores de Todos os Tempos")
    
    st.markdown("| Posição | Nome | Pontuação Total | Contribuições |")
    st.markdown("|---------|------|-----------------|---------------|")
    
    for idx, rank in enumerate(ranking_com_contrib[:10]):
        st.markdown(f"| #{idx+1} | {rank['nome']} | {rank['pontos']} pontos | {rank['contribuicoes']} |")
    
    st.divider()
    st.caption("💡 **Dica:** Quanto mais você contribui com casos, vídeos, snippets, ferramentas e materiais, maior sua pontuação!")