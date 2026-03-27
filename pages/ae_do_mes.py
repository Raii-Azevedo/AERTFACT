import streamlit as st
from datetime import datetime
import sys
import os
import hashlib

# NO INÍCIO DE CADA PÁGINA
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.menu import render_sidebar
from allowed_emails import get_all_allowed_emails, is_admin, get_user_role
from database import get_connection, return_connection, salvar_ae_mes_historico, get_historico_ae_mes, get_nome_usuario, get_avatar_url

st.set_page_config(page_title="AE do Mês", page_icon="🏆", layout="wide", initial_sidebar_state="expanded")

if not st.session_state.get("authenticated", False):
    st.switch_page("app.py")

# Depois do set_page_config
render_sidebar()

st.title("🏆 AE do Mês")
st.caption("Reconhecendo quem mais contribui para o crescimento do time")

# ============================================
# FUNÇÕES PARA CÁLCULO DE PONTUAÇÃO
# ============================================

def calcular_pontuacao_contribuicoes(autor_email):
    """Calcula a pontuação total de um usuário baseado nas contribuições"""
    conn = get_connection()
    cursor = conn.cursor()
    
    pontuacao = 0
    contribuicoes = {}
    
    # Casos de uso (10 pontos cada)
    cursor.execute("SELECT COUNT(*) FROM casos_uso WHERE autor_email = ?", (autor_email,))
    casos = cursor.fetchone()[0]
    pontuacao += casos * 10
    contribuicoes['casos'] = casos
    
    # Vídeos (15 pontos cada)
    cursor.execute("SELECT COUNT(*) FROM videos WHERE autor_email = ?", (autor_email,))
    videos = cursor.fetchone()[0]
    pontuacao += videos * 15
    contribuicoes['videos'] = videos
    
    # Snippets (5 pontos cada)
    cursor.execute("SELECT COUNT(*) FROM snippets WHERE autor_email = ?", (autor_email,))
    snippets = cursor.fetchone()[0]
    pontuacao += snippets * 5
    contribuicoes['snippets'] = snippets
    
    # Ferramentas (8 pontos cada)
    cursor.execute("SELECT COUNT(*) FROM ferramentas WHERE autor_email = ?", (autor_email,))
    ferramentas = cursor.fetchone()[0]
    pontuacao += ferramentas * 8
    contribuicoes['ferramentas'] = ferramentas
    
    # Materiais (3 pontos cada)
    cursor.execute("SELECT COUNT(*) FROM materiais WHERE autor_email = ?", (autor_email,))
    materiais = cursor.fetchone()[0]
    pontuacao += materiais * 3
    contribuicoes['materiais'] = materiais
    
    cursor.close()
    return_connection(conn)
    
    return pontuacao, contribuicoes

def get_contribuicoes_detalhadas(autor_email, limite=10):
    """Retorna contribuições detalhadas de um usuário"""
    conn = get_connection()
    cursor = conn.cursor()
    
    contribuicoes = []
    
    # Buscar casos do usuário
    cursor.execute("""
        SELECT titulo, 'Case' as tipo, data_criacao 
        FROM casos_uso 
        WHERE autor_email = ? 
        ORDER BY data_criacao DESC LIMIT ?
    """, (autor_email, limite))
    
    for row in cursor.fetchall():
        contribuicoes.append({
            'titulo': row[0],
            'tipo': row[1],
            'data': row[2][:10] if row[2] else 'N/A'
        })
    
    # Buscar vídeos
    cursor.execute("""
        SELECT titulo, 'Vídeo' as tipo, data_criacao 
        FROM videos 
        WHERE autor_email = ? 
        ORDER BY data_criacao DESC LIMIT ?
    """, (autor_email, limite))
    
    for row in cursor.fetchall():
        contribuicoes.append({
            'titulo': row[0],
            'tipo': row[1],
            'data': row[2][:10] if row[2] else 'N/A'
        })
    
    # Buscar snippets
    cursor.execute("""
        SELECT titulo, 'Snippet' as tipo, data_criacao 
        FROM snippets 
        WHERE autor_email = ? 
        ORDER BY data_criacao DESC LIMIT ?
    """, (autor_email, limite))
    
    for row in cursor.fetchall():
        contribuicoes.append({
            'titulo': row[0],
            'tipo': row[1],
            'data': row[2][:10] if row[2] else 'N/A'
        })
    
    # Buscar ferramentas
    cursor.execute("""
        SELECT nome, 'Ferramenta' as tipo, data_criacao 
        FROM ferramentas 
        WHERE autor_email = ? 
        ORDER BY data_criacao DESC LIMIT ?
    """, (autor_email, limite))
    
    for row in cursor.fetchall():
        contribuicoes.append({
            'titulo': row[0],
            'tipo': row[1],
            'data': row[2][:10] if row[2] else 'N/A'
        })
    
    # Buscar materiais
    cursor.execute("""
        SELECT titulo, 'Material' as tipo, data_criacao 
        FROM materiais 
        WHERE autor_email = ? 
        ORDER BY data_criacao DESC LIMIT ?
    """, (autor_email, limite))
    
    for row in cursor.fetchall():
        contribuicoes.append({
            'titulo': row[0],
            'tipo': row[1],
            'data': row[2][:10] if row[2] else 'N/A'
        })
    
    cursor.close()
    return_connection(conn)
    
    # Ordenar por data (mais recentes primeiro)
    contribuicoes.sort(key=lambda x: x['data'], reverse=True)
    
    return contribuicoes[:limite]

# ============================================
# OBTENÇÃO DOS USUÁRIOS E PONTUAÇÕES
# ============================================

# Buscar todos os usuários autorizados
todos_usuarios = get_all_allowed_emails()

# Filtrar apenas usuários com role 'user' ou 'admin' (contribuidores)
usuarios_contribuidores = []
for usuario in todos_usuarios:
    email = usuario[0]
    role = usuario[1]
    nome = get_nome_usuario(email)
    
    # Incluir users e admins (admins também podem contribuir)
    if role in ['user', 'admin']:
        usuarios_contribuidores.append({
            'email': email,
            'nome': nome,
            'role': role
        })

# Calcular pontuação para cada contribuidor
ranking = []
for usuario in usuarios_contribuidores:
    pontuacao, contribs = calcular_pontuacao_contribuicoes(usuario['email'])
    total_contribs = contribs['casos'] + contribs['videos'] + contribs['snippets'] + contribs['ferramentas'] + contribs['materiais']
    
    ranking.append({
        'email': usuario['email'],
        'nome': usuario['nome'],
        'role': usuario['role'],
        'pontos': pontuacao,
        'contribuicoes': total_contribs,
        'detalhes': contribs
    })

# Ordenar por pontuação
ranking.sort(key=lambda x: x['pontos'], reverse=True)

# ============================================
# TABS
# ============================================

tab_atual, tab_ranking, tab_historico = st.tabs(["🏆 AE Atual", "📊 Ranking", "📜 Hall da Fama"])

# ============================================
# TAB 1: AE ATUAL
# ============================================
with tab_atual:
    if ranking:
        # Definir o AE do Mês (o primeiro do ranking com contribuições)
        ae_mes = None
        for r in ranking:
            if r['contribuicoes'] > 0:
                ae_mes = r
                break
        
        if ae_mes:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Buscar avatar do banco
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT avatar_file, nome FROM allowed_emails WHERE email = ?", (ae_mes['email'],))
                dados = cursor.fetchone()
                cursor.close()
                return_connection(conn)
                
                avatar_file = dados[0] if dados else None
                nome_usuario = dados[1] if dados else ae_mes['nome']
                
                # Mostrar avatar
                if avatar_file and os.path.exists(avatar_file):
                    st.image(avatar_file, width=200, caption=nome_usuario)
                else:
                    # Gerar avatar padrão via Gravatar
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
            
            # Contribuições detalhadas
            st.subheader("📝 Contribuições Recentes")
            
            contribs_detalhadas = get_contribuicoes_detalhadas(ae_mes['email'], limite=10)
            
            if contribs_detalhadas:
                for contrib in contribs_detalhadas:
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([4, 1, 1])
                        with col1:
                            st.markdown(f"**{contrib['titulo']}**")
                        with col2:
                            st.markdown(f"📌 {contrib['tipo']}")
                        with col3:
                            st.markdown(f"📅 {contrib['data']}")
            else:
                st.info("Ainda não há contribuições detalhadas para este usuário.")
            
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
    else:
        st.info("👥 Nenhum contribuidor encontrado. Adicione usuários com role 'user' ou 'admin' no gerenciamento de usuários.")

# ============================================
# TAB 2: RANKING
# ============================================
with tab_ranking:
    st.subheader(f"📊 Ranking de Pontuação - {datetime.now().strftime('%B %Y')}")
    
    if ranking:
        # Filtrar apenas quem tem contribuições
        ranking_com_contrib = [r for r in ranking if r['contribuicoes'] > 0]
        
        if ranking_com_contrib:
            for idx, rank in enumerate(ranking_com_contrib[:10]):
                badge = ["🥇", "🥈", "🥉", "⭐", "⭐", "⭐", "⭐", "⭐", "⭐", "⭐"][idx] if idx < 10 else "📌"
                
                # Buscar avatar do banco
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT avatar_file FROM allowed_emails WHERE email = ?", (rank['email'],))
                dados = cursor.fetchone()
                cursor.close()
                return_connection(conn)
                avatar_file = dados[0] if dados else None
                
                col1, col2, col3, col4, col5 = st.columns([1, 4, 2, 2, 2])
                with col1:
                    st.markdown(f"### {badge}")
                with col2:
                    # Mostrar avatar pequeno
                    if avatar_file and os.path.exists(avatar_file):
                        st.image(avatar_file, width=40)
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
                max_pontos = ranking_com_contrib[0]['pontos'] if ranking_com_contrib else 1
                st.progress(min(rank['pontos'] / max_pontos, 1.0))
        else:
            st.info("📊 Nenhuma contribuição registrada ainda. Comece a contribuir para aparecer no ranking!")
    else:
        st.info("👥 Nenhum contribuidor encontrado.")

# ============================================
# TAB 3: HALL DA FAMA
# ============================================
with tab_historico:
    st.subheader("🏅 Hall da Fama")
    
    # Buscar histórico do banco
    historico = get_historico_ae_mes()
    
    if historico:
        st.markdown("### 🎖️ Últimos AE do Mês")
        
        for item in historico:
            with st.container(border=True):
                col1, col2, col3 = st.columns([1, 3, 2])
                with col1:
                    st.markdown(f"### 🏆")
                with col2:
                    st.markdown(f"**{item[0]}**")
                    st.caption(f"{item[1]}/{item[2]}")  # mês/ano
                with col3:
                    st.markdown(f"🎯 {item[3]} pontos")
                st.caption(f"📅 Definido em: {item[5][:10] if item[5] else 'N/A'}")
    else:
        st.info("📜 Histórico ainda não disponível. Os AE do Mês aparecerão aqui.")
    
    st.divider()
    
    # Top contribuidores de todos os tempos
    st.markdown("### 🎖️ Maiores Contribuidores de Todos os Tempos")
    
    st.markdown("| Posição | Nome | Pontuação Total | Contribuições |")
    st.markdown("|---------|------|-----------------|---------------|")
    
    for idx, rank in enumerate(ranking[:10]):
        st.markdown(f"| #{idx+1} | {rank['nome']} | {rank['pontos']} pontos | {rank['contribuicoes']} |")
    
    st.divider()
    st.caption("💡 **Dica:** Quanto mais você contribui com casos, vídeos, snippets, ferramentas e materiais, maior sua pontuação!")
    
    # Seção de admin para definir AE do Mês manualmente
    if is_admin(st.session_state.get("user_email", "")):
        st.divider()
        with st.expander("🔧 **Admin: Definir AE do Mês Manualmente**"):
            st.warning("⚠️ Área restrita para administradores")
            
            col1, col2 = st.columns(2)
            with col1:
                opcoes = [f"{r['nome']} ({r['pontos']} pts - {r['contribuicoes']} contribuições)" 
                         for r in ranking if r['contribuicoes'] > 0]
                if opcoes:
                    selecionado = st.selectbox("Selecionar AE do Mês", opcoes)
                    
                    if st.button("✅ Definir AE do Mês", type="primary"):
                        # Encontrar o usuário selecionado
                        for r in ranking:
                            if f"{r['nome']} ({r['pontos']} pts - {r['contribuicoes']} contribuições)" == selecionado:
                                import json
                                contrib_json = json.dumps(r['detalhes'])
                                salvar_ae_mes_historico(
                                    email=r['email'],
                                    nome=r['nome'],
                                    pontuacao=r['pontos'],
                                    contribuicoes=contrib_json,
                                    definido_por=st.session_state.get("user_email", "")
                                )
                                st.success(f"✅ AE do Mês definido como {r['nome']}!")
                                st.rerun()
                else:
                    st.info("Nenhum contribuidor com pontuação para selecionar")