import streamlit as st
import sys
import os
import pandas as pd
from datetime import datetime

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.menu import render_sidebar
from allowed_emails import can_edit, is_admin
from database import get_connection, return_connection

# Verificar autenticação
if not st.session_state.get("authenticated", False):
    st.switch_page("app.py")

st.set_page_config(
    page_title="Boas Práticas - AE Knowledge Hub",
    page_icon="📖",
    layout="wide"
)

# Renderizar menu lateral
render_sidebar()

# Obter permissões
user_email = st.session_state.get("user_email", "")
can_edit_content = can_edit(user_email)
is_admin_user = is_admin(user_email)

st.title("📖 Manual de Boas Práticas em Analytics Engineering")
st.markdown("""
*Padrões, diretrizes e checklists para projetos de alta qualidade, baseados nas melhores práticas do mercado.*
""")

# Versão e atualização
col1, col2 = st.columns([3, 1])
with col1:
    st.caption(f"📅 Última atualização: {datetime.now().strftime('%d/%m/%Y')}")
with col2:
    st.caption("📌 Versão 2.0 | Baseado em Data Goblins")

st.divider()

# ============================================
# SEÇÃO 1: SEMANTIC MODEL DESIGN
# ============================================
with st.expander("🏗️ **Semantic Model Design** - Planejamento e Arquitetura", expanded=False):
    st.markdown("""
    O design do modelo semântico é a base para um projeto de sucesso. Defina claramente:
    - **Escopo do negócio**: Quais processos serão modelados?
    - **Fontes de dados**: Quais sistemas e quais níveis de granularidade?
    - **Conceitos-chave**: Quais métricas e dimensões são críticas?
    - **Segurança**: Quem pode ver o quê? (RLS)
    """)
    
    # Checklist interativa
    st.subheader("✅ Checklist de Design")
    
    design_items = [
        "✅ Escopo do modelo documentado e aprovado",
        "✅ Mapeamento de fontes de dados concluído",
        "✅ Granularidade definida por tabela fato",
        "✅ Dimensões conformadas identificadas",
        "✅ Estratégia de segurança (RLS) definida",
        "✅ Nível de agregação alinhado com necessidades de negócio",
        "✅ Ciclo de vida dos dados (retenção, atualização) planejado"
    ]
    
    completed_design = []
    for item in design_items:
        if can_edit_content:
            checked = st.checkbox(item, key=f"design_{item[:20]}")
            if checked:
                completed_design.append(item)
        else:
            st.markdown(f"- {item}")
    
    if can_edit_content and completed_design:
        st.success(f"Progresso: {len(completed_design)}/{len(design_items)} itens concluídos")
        st.progress(len(completed_design) / len(design_items))

# ============================================
# SEÇÃO 2: POWER QUERY & DATA SOURCES
# ============================================
with st.expander("🔌 **Power Query & Data Sources** - ETL e Conectividade", expanded=False):
    st.markdown("""
    A camada de ingestão e transformação deve ser eficiente, rastreável e performática.
    """)
    
    tabs = st.tabs(["📋 Checklist", "🎯 Boas Práticas", "⚠️ Armadilhas Comuns"])
    
    with tabs[0]:
        st.subheader("✅ Checklist de Power Query")
        
        pq_items = [
            "✅ Folding de consultas habilitado quando possível",
            "✅ Filtros aplicados o mais cedo possível",
            "✅ Remoção de colunas não utilizadas",
            "✅ Tipos de dados explicitamente definidos",
            "✅ Nomes de colunas padronizados (snake_case)",
            "✅ Parâmetros utilizados para fontes variáveis",
            "✅ Incremental refresh configurado para tabelas grandes",
            "✅ Validação de dados implementada"
        ]
        
        for item in pq_items:
            if can_edit_content:
                st.checkbox(item, key=f"pq_{item[:20]}")
            else:
                st.markdown(f"- {item}")
    
    with tabs[1]:
        st.markdown("""
        ### 🎯 Boas Práticas Essenciais
        
        1. **Query Folding**: Sempre que usar SQL, verifique se as transformações são "foldadas" para a fonte.
        2. **Particionamento**: Use incremental refresh para tabelas grandes (>100M linhas).
        3. **Parâmetros**: Centralize valores como datas, caminhos e credenciais em parâmetros.
        4. **Documentação**: Adicione etapas de comentário explicando transformações complexas.
        """)
        
        st.code("""
        // Exemplo: Parâmetros no Power Query
        let
            Fonte = Sql.Database(ParamServidor, ParamBanco),
            Consulta = Value.NativeQuery(Fonte, "
                SELECT * FROM vendas 
                WHERE data >= @DataInicio 
                AND data < @DataFim",
                [DataInicio=ParamDataInicio, DataFim=ParamDataFim]
            )
        in
            Consulta
        """, language="powerquery")
    
    with tabs[2]:
        st.error("""
        ### ⚠️ Armadilhas Comuns
        
        - **Expansão prematura**: Expandir tabelas antes de filtrar gera dados desnecessários.
        - **Ignorar o folding**: Forçar transferência de todos os dados para o Power BI.
        - **Colunas calculadas no Power Query**: Prefira transformações na fonte ou DAX para cálculos simples.
        - **Falta de validação**: Não verificar nulos, duplicatas e outliers na carga.
        """)

# ============================================
# SEÇÃO 3: MODEL OBJECTS (TABELAS, COLUNAS, MEDIDAS)
# ============================================
with st.expander("📊 **Model Objects** - Tabelas, Colunas e Medidas", expanded=True):
    st.markdown("""
    A estrutura do modelo deve ser clara, consistente e otimizada para consumo.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Nomenclatura")
        
        naming_rules = {
            "Tabelas Dimensão": "dim_",
            "Tabelas Fato": "fato_",
            "Tabelas Auxiliares": "aux_",
            "Medidas Básicas": "m_",
            "Medidas Temporais": "mt_",
            "Medidas Percentuais": "mp_",
            "Colunas Calculadas": "c_"
        }
        
        for name, prefix in naming_rules.items():
            st.markdown(f"- **{name}:** `{prefix}`")
    
    with col2:
        st.subheader("📂 Organização")
        st.markdown("""
        **Estrutura de Pastas Recomendada:**
📁 Medidas
├── 📁 01_Basicas
├── 📁 02_Tempo
├── 📁 03_Percentuais
└── 📁 04_Auxiliares

📁 Tabelas
├── 📁 Dimensões
├── 📁 Fatos
└── 📁 Auxiliares

text
""")

    # Medidas de exemplo
    st.subheader("📐 Exemplos de Medidas Padronizadas")

    example_measures = """
```dax
// Medida Básica
m_total_vendas = SUMX(fato_vendas, [quantidade] * [preco])

// Medida Temporal (YTD)
mt_vendas_ytd = TOTALYTD([m_total_vendas], dim_data[data])

// Medida Percentual
mp_margem_lucro = DIVIDE([m_lucro], [m_total_vendas], 0)

// Medida com Variáveis (recomendado para performance)
m_vendas_ultimo_mes = 
VAR UltimoDia = MAX(dim_data[data])
VAR DataInicio = EOMONTH(UltimoDia, -1) + 1
VAR DataFim = EOMONTH(UltimoDia, 0)
RETURN
CALCULATE(
    [m_total_vendas],
    dim_data[data] >= DataInicio,
    dim_data[data] <= DataFim
)
```
"""
    st.code(example_measures, language="dax")

# ============================================
# SEÇÃO 4: DAX & PERFORMANCE
# ============================================
with st.expander("⚡ DAX & Performance - Otimização e Boas Práticas", expanded=False):
    st.markdown("""
    O código DAX deve ser performático, legível e seguir padrões consistentes.
    """)

    performance_items = [
        "✅ Prefira medidas a colunas calculadas",
        "✅ Use variáveis para cálculos repetidos",
        "✅ Evite funções iteradoras (SUMX, AVERAGEX) em modelos grandes",
        "✅ Utilize CALCULATE com moderação",
        "✅ Evite filtros em colunas com alta cardinalidade (> 1M valores)",
        "✅ Use KEEPFILTERS para respeitar filtros existentes",
        "✅ Colunas calculadas devem ser criadas no Power Query, se possível"
    ]

    st.subheader("✅ Checklist de Performance DAX")
    for item in performance_items:
        if can_edit_content:
            st.checkbox(item, key=f"dax_{item[:20]}")
        else:
            st.markdown(f"- {item}")

    st.subheader("📈 Monitoramento de Performance")
    st.markdown("""
    Ferramentas úteis:

    DAX Studio - Análise de planos de consulta

    Performance Analyzer (Power BI) - Identificar visuais lentos

    VertiPaq Analyzer - Analisar compressão de colunas

    Métricas de referência:

    Tempo de resposta de visuais < 3 segundos

    Modelo < 1GB (preferencialmente)

    Uso de CPU < 70% em horário de pico
    """)

# ============================================
# SEÇÃO 5: DOCUMENTAÇÃO & HANDOVER
# ============================================
with st.expander("📚 Documentação & Handover - Entrega e Manutenção", expanded=False):
    st.markdown("""
    Um modelo bem documentado é sustentável e facilita a evolução do projeto.
    """)

    doc_items = [
        "Diagrama do modelo (Star Schema)",
        "Dicionário de dados com descrições",
        "Lista de medidas com fórmulas e propósito",
        "Documentação de segurança (RLS)",
        "Instruções de refresh e dependências",
        "Lista de contatos do time responsável",
        "Guia de solução de problemas comuns"
    ]

    st.subheader("📋 Documentação Obrigatória")
    for item in doc_items:
        if can_edit_content:
            st.checkbox(item, key=f"doc_{item[:20]}")
        else:
            st.markdown(f"- {item}")

    st.subheader("🛠️ Ferramentas de Documentação")
    st.markdown("""
    Model Documenter (SQLBI) - Gera documentação HTML automática

    Power BI REST API - Extrai metadados programaticamente

    Tabular Editor - Adicionar descrições e anotações
    """)

    # Template de handover - sem expander aninhado, apenas markdown
    st.subheader("📄 Template de Handover")
    st.markdown("""
    markdown
    # Handover - [Nome do Projeto]

    ## 1. Visão Geral
    - **Objetivo:** [descrição]
    - **Stakeholders:** [lista]
    - **Última atualização:** [data]

    ## 2. Modelo
    - **Tabelas:** [quantidade]
    - **Medidas:** [quantidade]
    - **Fontes de dados:** [lista]

    ## 3. Manutenção
    - **Refresh:** [horário/frequência]
    - **Alertas:** [como receber notificações]
    - **Backup:** [local e procedimento]

    ## 4. Problemas Conhecidos
    - [descrição e workaround]

    ## 5. Contatos
    - **Autor:** [email]
    - **Suporte:** [email/time]
    """)

# ============================================
# SEÇÃO 6: VISUALIZAÇÃO E UX
# ============================================
with st.expander("🎨 Visualização e UX - Relatórios e Dashboards", expanded=False):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("✅ Boas Práticas")
        st.markdown("""
        Tipografia: Inter ou Segoe UI (12pt corpo, 18pt títulos)

        Cores: Paleta corporativa, máximo 6 cores por visual

        Layout: Responsivo, espaço em branco adequado

        Tooltips: Descritivos e relevantes

        Acessibilidade: Alto contraste, suporte a leitores de tela
        """)

    with col2:
        st.subheader("❌ Evitar")
        st.markdown("""
        Cores neon ou muito vibrantes

        Gráficos 3D sem necessidade

        Rolagem horizontal excessiva

        Mais de 5 categorias em gráficos de pizza

        Elementos não interativos sem explicação
        """)

    st.subheader("📊 Escolha do Visual por Objetivo")
    chart_data = pd.DataFrame({
        "Objetivo": ["Comparação", "Tendência", "Composição", "Distribuição", "Relacionamento"],
        "Recomendado": ["Barras, Colunas", "Linhas, Áreas", "Empilhado, Pizza (≤5)", "Histograma, Box Plot", "Dispersão, Bolhas"],
        "Evitar": ["Pizza", "3D", "Anéis (donut)", "Tabela densa", "Barras empilhadas"]
    })
    st.dataframe(chart_data, use_container_width=True, hide_index=True)

# ============================================
# SEÇÃO 7: SEÇÃO ADMIN (APENAS PARA EDITORES/ADMIN)
# ============================================
if can_edit_content or is_admin_user:
    st.divider()
    with st.expander("🔧 Administração de Conteúdo (Editar Boas Práticas)", expanded=False):
        st.warning("⚠️ Área restrita para editores e administradores")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("➕ Adicionar Nova Boa Prática")
            nova_categoria = st.selectbox("Categoria", [
                "Design", "Power Query", "Model Objects", "DAX", "Documentação", "Visualização"
            ])
            novo_titulo = st.text_input("Título")
            novo_conteudo = st.text_area("Conteúdo", height=150)

            if st.button("💾 Salvar Nova Boa Prática", type="primary"):
                if novo_titulo and novo_conteudo:
                    try:
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("""
                        INSERT INTO boas_praticas (titulo, categoria, conteudo, autor, autor_email)
                        VALUES (?, ?, ?, ?, ?)
                        """, (novo_titulo, nova_categoria, novo_conteudo,
                              st.session_state.get("user_name", ""), user_email))
                        conn.commit()
                        cursor.close()
                        return_connection(conn)
                        st.success("✅ Boa prática adicionada com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")
                else:
                    st.warning("Preencha título e conteúdo")

        with col2:
            st.subheader("📋 Boas Práticas Existentes")
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, titulo, categoria, autor FROM boas_praticas ORDER BY data_criacao DESC")
            praticas = cursor.fetchall()
            cursor.close()
            return_connection(conn)

            if praticas:
                for p in praticas:
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.markdown(f"{p[1]} - {p[2]} (por {p[3]})")
                    with col_b:
                        if st.button("🗑️", key=f"del_bp_{p[0]}"):
                            conn = get_connection()
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM boas_praticas WHERE id = ?", (p[0],))
                            conn.commit()
                            cursor.close()
                            return_connection(conn)
                            st.rerun()
            else:
                st.info("Nenhuma boa prática personalizada ainda")

st.divider()
st.caption("💡 Referência: Baseado nas melhores práticas do Data Goblins e Microsoft Power BI")
st.caption("📚 Documentação oficial: Microsoft Learn - Power BI")