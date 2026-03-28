import streamlit as st
from datetime import datetime
import sys
import os
import pandas as pd  
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.menu import render_sidebar
from allowed_emails import can_edit, is_admin
from database import get_connection, return_connection

if not st.session_state.get("authenticated", False):
    st.switch_page("app.py")

st.set_page_config(page_title="Casos de Uso", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

render_sidebar()

# Obter permissões
user_email = st.session_state.get("user_email", "")
user_name = st.session_state.get("user_name", "")
can_edit_content = can_edit(user_email)

st.title("📊 Casos de Uso e Soluções")
st.markdown("*Repositório de soluções reais implementadas pelo time*")

# Inicializar estado para formulário
if "show_form" not in st.session_state:
    st.session_state.show_form = False

if "detalhes_abertos" not in st.session_state:
    st.session_state.detalhes_abertos = None

# ============================================
# FUNÇÕES PARA GERENCIAR CASOS NO BANCO
# ============================================

def get_casos_do_banco():
    """Busca os casos de uso do banco de dados"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, titulo, contexto, tecnologia, descricao, resultado, tags, autor, autor_email, data_criacao
        FROM casos_uso 
        ORDER BY data_criacao DESC
    """)
    resultados = cursor.fetchall()
    cursor.close()
    return_connection(conn)
    
    casos = []
    for row in resultados:
        casos.append({
            'id': row[0],
            'titulo': row[1],
            'contexto': row[2],
            'tecnologia': row[3],
            'descricao': row[4],
            'resultado': row[5] if row[5] else "",
            'tags': row[6].split(',') if row[6] else [],
            'autor': row[7],
            'autor_email': row[8],
            'data': str(row[9])[:10] if row[9] else "N/A"
        })
    return casos

def get_contextos_unicos():
    """Retorna lista de contextos únicos do banco"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT contexto FROM casos_uso WHERE contexto IS NOT NULL AND contexto != ''")
    resultados = cursor.fetchall()
    cursor.close()
    return_connection(conn)
    return sorted([row[0] for row in resultados])

def get_tecnologias_unicas():
    """Retorna lista de tecnologias únicas do banco"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT tecnologia FROM casos_uso WHERE tecnologia IS NOT NULL AND tecnologia != ''")
    resultados = cursor.fetchall()
    cursor.close()
    return_connection(conn)
    return sorted([row[0] for row in resultados])

def adicionar_caso(titulo, contexto, tecnologia, descricao, resultado, tags, autor, autor_email):
    """Adiciona um novo caso de uso"""
    conn = get_connection()
    cursor = conn.cursor()
    
    tags_str = ', '.join(tags) if isinstance(tags, list) else tags
    
    cursor.execute("""
        INSERT INTO casos_uso (titulo, contexto, tecnologia, descricao, resultado, tags, autor, autor_email)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (titulo, contexto, tecnologia, descricao, resultado, tags_str, autor, autor_email))
    
    conn.commit()
    cursor.close()
    return_connection(conn)

def remover_caso(caso_id):
    """Remove um caso de uso"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM casos_uso WHERE id = %s", (caso_id,))
    conn.commit()
    cursor.close()
    return_connection(conn)

# ============================================
# FUNÇÕES PARA FEEDBACK
# ============================================

def get_media_avaliacao(caso_id):
    """Retorna a média de avaliações de um caso"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COALESCE(AVG(avaliacao), 0) as media, COUNT(*) as total 
        FROM feedback_casos 
        WHERE caso_id = %s
    """, (caso_id,))
    resultado = cursor.fetchone()
    cursor.close()
    return_connection(conn)
    return resultado[0] if resultado else 0, resultado[1] if resultado else 0

def ja_avaliou(caso_id, usuario_email):
    """Verifica se o usuário já avaliou este caso"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM feedback_casos 
        WHERE caso_id = %s AND usuario_email = %s
    """, (caso_id, usuario_email))
    resultado = cursor.fetchone()
    cursor.close()
    return_connection(conn)
    return resultado is not None

def salvar_feedback(caso_id, usuario_email, avaliacao, utilidade, comentario):
    """Salva o feedback de um caso - versão corrigida para PostgreSQL"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verificar se já existe
    cursor.execute("""
        SELECT id FROM feedback_casos 
        WHERE caso_id = %s AND usuario_email = %s
    """, (caso_id, usuario_email))
    existe = cursor.fetchone()
    
    if existe:
        # Atualizar existente
        cursor.execute("""
            UPDATE feedback_casos 
            SET avaliacao = %s, utilidade = %s, comentario = %s, data_criacao = CURRENT_TIMESTAMP
            WHERE caso_id = %s AND usuario_email = %s
        """, (avaliacao, utilidade, comentario, caso_id, usuario_email))
    else:
        # Inserir novo
        cursor.execute("""
            INSERT INTO feedback_casos (caso_id, usuario_email, avaliacao, utilidade, comentario)
            VALUES (%s, %s, %s, %s, %s)
        """, (caso_id, usuario_email, avaliacao, utilidade, comentario))
    
    conn.commit()
    cursor.close()
    return_connection(conn)
    

# ============================================
# FILTROS DINÂMICOS BASEADOS NO BANCO
# ============================================
st.subheader("🔍 Filtros")
col1, col2 = st.columns(2)

# Obter opções únicas do banco
contextos_existentes = get_contextos_unicos()
tecnologias_existentes = get_tecnologias_unicas()

# Adicionar opção "Todos" no início
contextos_opcoes = ["Todos"] + contextos_existentes
tecnologias_opcoes = ["Todos"] + tecnologias_existentes

with col1:
    contexto_filtro = st.multiselect(
        "Contexto",
        contextos_opcoes,
        default=["Todos"],
        help="Selecione um ou mais contextos para filtrar"
    )

with col2:
    tecnologia_filtro = st.multiselect(
        "Tecnologia",
        tecnologias_opcoes,
        default=["Todos"],
        help="Selecione uma ou mais tecnologias para filtrar"
    )

# Mostrar resumo dos filtros ativos
filtros_ativos = []
if "Todos" not in contexto_filtro and contexto_filtro:
    filtros_ativos.append(f"Contexto: {', '.join(contexto_filtro)}")
if "Todos" not in tecnologia_filtro and tecnologia_filtro:
    filtros_ativos.append(f"Tecnologia: {', '.join(tecnologia_filtro)}")

if filtros_ativos:
    st.caption(f"🎯 Filtros ativos: {' | '.join(filtros_ativos)}")

# ============================================
# BOTÃO PARA ADICIONAR NOVO CASO
# ============================================
col1, col2 = st.columns([6, 1])
with col2:
    if can_edit_content:
        if st.button("➕ Novo Caso", use_container_width=True):
            st.session_state.show_form = not st.session_state.show_form

# ============================================
# FORMULÁRIO PARA NOVO CASO (COM INPUT LIVRE)
# ============================================
if st.session_state.get("show_form", False) and can_edit_content:
    
    st.subheader("📝 Adicionar Novo Caso")
    
    titulo = st.text_input("Título do Caso*", placeholder="ex: Otimização de performance com Python", key="titulo_input")
    
    col1, col2 = st.columns(2)
    
    contexto_selecionado = None
    tecnologia_selecionada = None
    
    with col1:
        contextos_sugeridos = contextos_existentes if contextos_existentes else ["Performance", "Conectividade", "UX/UI", "Governança", "Segurança"]
        contexto_opcao = st.selectbox(
            "Contexto*",
            contextos_sugeridos + ["➕ Adicionar novo contexto..."],
            help="Selecione um contexto existente ou escolha a última opção para digitar um novo",
            key="contexto_select"
        )
        
        if contexto_opcao == "➕ Adicionar novo contexto...":
            contexto_selecionado = st.text_input("Digite o novo contexto", placeholder="ex: Machine Learning, Infraestrutura", key="contexto_novo")
        else:
            contexto_selecionado = contexto_opcao
    
    with col2:
        tecnologias_sugeridas = tecnologias_existentes if tecnologias_existentes else ["DAX", "Python", "SQL", "Power BI", "Databricks"]
        tecnologia_opcao = st.selectbox(
            "Tecnologia*",
            tecnologias_sugeridas + ["➕ Adicionar nova tecnologia..."],
            help="Selecione uma tecnologia existente ou escolha a última opção para digitar uma nova",
            key="tecnologia_select"
        )
        
        if tecnologia_opcao == "➕ Adicionar nova tecnologia...":
            tecnologia_selecionada = st.text_input("Digite a nova tecnologia", placeholder="ex: Spark, Airflow, dbt", key="tecnologia_nova")
        else:
            tecnologia_selecionada = tecnologia_opcao
    
    descricao = st.text_area("Descrição da Solução*", height=100, 
                              placeholder="Descreva o problema enfrentado e como foi abordado...", key="descricao_input")
    resultado = st.text_area("Resultados Alcançados*", height=100,
                              placeholder="Quais foram os benefícios? Redução de tempo? Melhoria de performance?", key="resultado_input")
    
    tags_input = st.text_input("Tags (separadas por vírgula)", placeholder="ex: otimização, performance, python", key="tags_input")
    
    col1, col2 = st.columns(2)
    with col1:
        submitted = st.button("💾 Salvar Caso", use_container_width=True, type="primary", key="submit_caso")
    with col2:
        if st.button("❌ Cancelar", use_container_width=True, key="cancel_caso"):
            st.session_state.show_form = False
            st.rerun()
    
    if submitted:
        if not titulo:
            st.warning("⚠️ Preencha o título")
        elif not descricao:
            st.warning("⚠️ Preencha a descrição")
        elif not resultado:
            st.warning("⚠️ Preencha os resultados")
        elif not contexto_selecionado:
            st.warning("⚠️ Selecione ou digite um contexto")
        elif not tecnologia_selecionada:
            st.warning("⚠️ Selecione ou digite uma tecnologia")
        else:
            try:
                tags_list = [t.strip() for t in tags_input.split(',')] if tags_input else []
                adicionar_caso(titulo, contexto_selecionado, tecnologia_selecionada, descricao, resultado, tags_list, user_name, user_email)
                st.success("✅ Caso adicionado com sucesso!")
                st.session_state.show_form = False
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")
    
    st.divider()

# ============================================
# BUSCAR E FILTRAR CASOS
# ============================================
todos_casos = get_casos_do_banco()

# Aplicar filtros
casos_filtrados = []
for caso in todos_casos:
    if "Todos" not in contexto_filtro and caso['contexto'] not in contexto_filtro:
        continue
    if "Todos" not in tecnologia_filtro and caso['tecnologia'] not in tecnologia_filtro:
        continue
    casos_filtrados.append(caso)

# ============================================
# EXIBIR RESULTADOS
# ============================================
st.subheader(f"📖 {len(casos_filtrados)} casos encontrados")

if casos_filtrados:
    for caso in casos_filtrados:
        with st.container(border=True):
            # ============================================
            # CABEÇALHO DO CARD
            # ============================================
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"### {caso['titulo']}")
                st.markdown(f"**📌 Contexto:** {caso['contexto']} | **🛠️ Tecnologia:** {caso['tecnologia']}")
                
                if len(caso['descricao']) > 200:
                    st.markdown(f"**📝 Descrição:** {caso['descricao'][:200]}...")
                else:
                    st.markdown(f"**📝 Descrição:** {caso['descricao']}")
                
                if len(caso['resultado']) > 150:
                    st.markdown(f"**🎯 Resultados:** {caso['resultado'][:150]}...")
                else:
                    st.markdown(f"**🎯 Resultados:** {caso['resultado']}")
                
                if caso['tags']:
                    st.markdown("**🏷️ Tags:** " + " ".join([f"`{tag}`" for tag in caso['tags'][:5]]))
                
                st.caption(f"👤 {caso['autor']} | 📅 {caso['data']}")
            
            with col2:
                if can_edit_content:
                    if st.button("🗑️ Excluir", key=f"del_{caso['id']}"):
                        try:
                            remover_caso(caso['id'])
                            st.success("Caso removido!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro: {e}")
                
                if st.button("🔍 Ver detalhes", key=f"details_{caso['id']}"):
                    st.session_state.detalhes_abertos = caso['id']
                    st.rerun()
            
            # ============================================
            # SEÇÃO DE FEEDBACK E AVALIAÇÃO
            # ============================================
            st.markdown("---")
            
            # Buscar média de avaliações
            media, total_avaliacoes = get_media_avaliacao(caso['id'])
            
            col_estrelas, col_info = st.columns([1, 3])
            with col_estrelas:
                if total_avaliacoes > 0:
                    estrelas = "⭐" * min(5, round(media))
                    st.markdown(f"### {estrelas}")
                else:
                    st.markdown("### ⭐")
            
            with col_info:
                if total_avaliacoes > 0:
                    st.caption(f"📊 {media:.1f} de 5 estrelas ({total_avaliacoes} avaliações)")
                else:
                    st.caption("📊 Seja o primeiro a avaliar este caso!")
            
            # Verificar se usuário já avaliou
            usuario_ja_avaliou = ja_avaliou(caso['id'], user_email)
            
            if not usuario_ja_avaliou:
                with st.expander("⭐ Avaliar este caso", expanded=False):
                    col_rating, col_utilidade, col_comentario = st.columns([1, 1, 2])
                    
                    with col_rating:
                        avaliacao = st.select_slider(
                            "Nota",
                            options=[1, 2, 3, 4, 5],
                            value=3,
                            key=f"rating_{caso['id']}"
                        )
                    
                    with col_utilidade:
                        utilidade = st.selectbox(
                            "Utilidade",
                            ["Muito útil", "Útil", "Pouco útil"],
                            key=f"utilidade_{caso['id']}"
                        )
                    
                    with col_comentario:
                        comentario = st.text_input(
                            "Comentário (opcional)", 
                            key=f"comentario_{caso['id']}",
                            placeholder="Deixe seu feedback sobre este caso..."
                        )
                    
                    if st.button("📝 Enviar feedback", key=f"feedback_{caso['id']}"):
                        try:
                            salvar_feedback(caso['id'], user_email, avaliacao, utilidade, comentario)
                            st.success("✅ Feedback enviado! Obrigado por contribuir.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao enviar feedback: {e}")
            else:
                st.info("✅ Você já avaliou este caso. Obrigado!")
            
            # ============================================
            # DETALHES COMPLETOS (EXPANDIDO)
            # ============================================
            if st.session_state.detalhes_abertos == caso['id']:
                st.markdown("---")
                with st.container(border=True):
                    col_close, col_title = st.columns([1, 11])
                    with col_close:
                        if st.button("❌", key=f"close_{caso['id']}"):
                            st.session_state.detalhes_abertos = None
                            st.rerun()
                    with col_title:
                        st.markdown("### 📋 Detalhes Completos do Caso")
                    
                    st.markdown("---")
                    
                    col_info1, col_info2 = st.columns(2)
                    with col_info1:
                        st.markdown(f"**📌 Título:** {caso['titulo']}")
                        st.markdown(f"**🏷️ Contexto:** {caso['contexto']}")
                        st.markdown(f"**🛠️ Tecnologia:** {caso['tecnologia']}")
                    with col_info2:
                        st.markdown(f"**👤 Autor:** {caso['autor']}")
                        st.markdown(f"**📧 Email:** {caso['autor_email']}")
                        st.markdown(f"**📅 Data:** {caso['data']}")
                    
                    st.markdown("---")
                    
                    st.markdown("### 📝 Descrição Completa")
                    st.markdown(f"{caso['descricao']}")
                    
                    st.markdown("### 🎯 Resultados Alcançados")
                    st.markdown(f"{caso['resultado']}")
                    
                    if caso['tags']:
                        st.markdown("### 🏷️ Tags")
                        st.markdown(" ".join([f"`{tag}`" for tag in caso['tags']]))
                    
                    # Mostrar feedbacks de outros usuários
                    st.markdown("---")
                    st.markdown("### 💬 Feedbacks da Comunidade")
                    
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT usuario_email, avaliacao, utilidade, comentario, data_criacao
                        FROM feedback_casos 
                        WHERE caso_id = %s 
                        ORDER BY data_criacao DESC
                        LIMIT 5
                    """, (caso['id'],))
                    feedbacks = cursor.fetchall()
                    cursor.close()
                    return_connection(conn)
                    
                    if feedbacks:
                        for fb in feedbacks:
                            with st.container():
                                estrelas_fb = "⭐" * fb[1]
                                st.markdown(f"**{estrelas_fb}** - *{fb[3][:100] if fb[3] else 'Sem comentário'}*")
                                st.caption(f"👤 {fb[0].split('@')[0]} | {fb[2]} | 📅 {str(fb[4])[:10]}")
                                st.markdown("---")
                    else:
                        st.info("Nenhum feedback ainda. Seja o primeiro a comentar!")
                    
                    st.markdown("---")
                    st.caption("💡 *Este caso foi contribuído para o conhecimento do time.*")
else:
    st.info("📭 Nenhum caso encontrado com os filtros selecionados.")
    
    if not todos_casos:
        st.info("💡 Seja o primeiro a contribuir! Clique em 'Novo Caso' para adicionar sua solução.")

# ============================================
# ESTATÍSTICAS DINÂMICAS
# ============================================
if todos_casos:
    st.divider()
    st.subheader("📊 Estatísticas")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📚 Total de Casos", len(todos_casos))
    
    with col2:
        contextos_count = {}
        for caso in todos_casos:
            contextos_count[caso['contexto']] = contextos_count.get(caso['contexto'], 0) + 1
        top_contexto = max(contextos_count, key=contextos_count.get) if contextos_count else "N/A"
        st.metric("🏷️ Contexto Mais Comum", top_contexto)
    
    with col3:
        tecnologias_count = {}
        for caso in todos_casos:
            tecnologias_count[caso['tecnologia']] = tecnologias_count.get(caso['tecnologia'], 0) + 1
        top_tecnologia = max(tecnologias_count, key=tecnologias_count.get) if tecnologias_count else "N/A"
        st.metric("🛠️ Tecnologia Mais Usada", top_tecnologia)
    
    with col4:
        contribuidores = len(set(caso['autor'] for caso in todos_casos))
        st.metric("👥 Contribuidores", contribuidores)
    
    # Gráfico de distribuição de contextos
    st.divider()
    st.subheader("📈 Distribuição por Contexto")
    
    if todos_casos:
        df_dist = pd.DataFrame([(c['contexto'], 1) for c in todos_casos], columns=['Contexto', 'Contagem'])
        df_dist = df_dist.groupby('Contexto').count().reset_index()
        df_dist = df_dist.sort_values('Contagem', ascending=False)
        st.bar_chart(df_dist.set_index('Contexto'))
    else:
        st.info("Sem dados para exibir")