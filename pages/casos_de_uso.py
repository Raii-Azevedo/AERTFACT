import streamlit as st
from datetime import datetime
import sys
import os
import pandas as pd  
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.menu import render_sidebar
from allowed_emails import can_edit, is_admin
from database import get_connection, return_connection, DB_TYPE

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

def get_placeholder():
    return '%s' if DB_TYPE == 'postgresql' else '?'

# Inicializar estado para formulário
if "show_form" not in st.session_state:
    st.session_state.show_form = False

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
    placeholder = get_placeholder()
    
    tags_str = ', '.join(tags) if isinstance(tags, list) else tags
    
    cursor.execute(f"""
        INSERT INTO casos_uso (titulo, contexto, tecnologia, descricao, resultado, tags, autor, autor_email)
        VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
    """, (titulo, contexto, tecnologia, descricao, resultado, tags_str, autor, autor_email))
    
    conn.commit()
    cursor.close()
    return_connection(conn)

def remover_caso(caso_id):
    """Remove um caso de uso"""
    conn = get_connection()
    cursor = conn.cursor()
    placeholder = get_placeholder()
    cursor.execute(f"DELETE FROM casos_uso WHERE id = {placeholder}", (caso_id,))
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
# FORMULÁRIO PARA NOVO CASO (COM INPUT LIVRE - CORRIGIDO)
# ============================================
if st.session_state.get("show_form", False) and can_edit_content:
    
    st.subheader("📝 Adicionar Novo Caso")
    
    titulo = st.text_input("Título do Caso*", placeholder="ex: Otimização de performance com Python", key="titulo_input")
    
    col1, col2 = st.columns(2)
    
    # Variáveis para armazenar valores
    contexto_selecionado = None
    tecnologia_selecionada = None
    
    with col1:
        # Contexto com input livre
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
        # Tecnologia com input livre
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
    
    # Descrição e resultado
    descricao = st.text_area("Descrição da Solução*", height=100, 
                              placeholder="Descreva o problema enfrentado e como foi abordado...", key="descricao_input")
    resultado = st.text_area("Resultados Alcançados*", height=100,
                              placeholder="Quais foram os benefícios? Redução de tempo? Melhoria de performance?", key="resultado_input")
    
    tags_input = st.text_input("Tags (separadas por vírgula)", placeholder="ex: otimização, performance, python", key="tags_input")
    
    # Botões
    col1, col2 = st.columns(2)
    with col1:
        submitted = st.button("💾 Salvar Caso", use_container_width=True, type="primary", key="submit_caso")
    with col2:
        if st.button("❌ Cancelar", use_container_width=True, key="cancel_caso"):
            st.session_state.show_form = False
            st.rerun()
    
    if submitted:
        # Validar campos
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
    # Filtro de contexto
    if "Todos" not in contexto_filtro and caso['contexto'] not in contexto_filtro:
        continue
    
    # Filtro de tecnologia
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
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"### {caso['titulo']}")
                st.markdown(f"**📌 Contexto:** {caso['contexto']} | **🛠️ Tecnologia:** {caso['tecnologia']}")
                st.markdown(f"**📝 Descrição:** {caso['descricao'][:200]}..." if len(caso['descricao']) > 200 else f"**📝 Descrição:** {caso['descricao']}")
                st.markdown(f"**🎯 Resultados:** {caso['resultado'][:150]}..." if len(caso['resultado']) > 150 else f"**🎯 Resultados:** {caso['resultado']}")
                
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
                    with st.expander("📋 Detalhes completos", expanded=True):
                        st.markdown(f"**Título:** {caso['titulo']}")
                        st.markdown(f"**Contexto:** {caso['contexto']}")
                        st.markdown(f"**Tecnologia:** {caso['tecnologia']}")
                        st.markdown(f"**Descrição:** {caso['descricao']}")
                        st.markdown(f"**Resultados:** {caso['resultado']}")
                        st.markdown(f"**Tags:** {', '.join(caso['tags'])}")
                        st.markdown(f"**Autor:** {caso['autor']} ({caso['autor_email']})")
                        st.markdown(f"**Data:** {caso['data']}")
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
    
    # Preparar dados para o gráfico (com verificação se há dados)
    if todos_casos:
        df_dist = pd.DataFrame([(c['contexto'], 1) for c in todos_casos], columns=['Contexto', 'Contagem'])
        df_dist = df_dist.groupby('Contexto').count().reset_index()
        df_dist = df_dist.sort_values('Contagem', ascending=False)
        st.bar_chart(df_dist.set_index('Contexto'))
    else:
        st.info("Sem dados para exibir")