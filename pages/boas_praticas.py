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
*Padrões, diretrizes e checklists para projetos de alta qualidade*
""")

# Versão e atualização
col1, col2 = st.columns([3, 1])
with col1:
    st.caption(f"📅 Última atualização: {datetime.now().strftime('%d/%m/%Y')}")
with col2:
    st.caption("📌 Versão 2.0")

st.divider()

# ============================================
# TABS PRINCIPAIS - ORGANIZAÇÃO LIMPA
# ============================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏗️ Design & Modelagem", 
    "🔌 Power Query & ETL", 
    "⚡ DAX & Performance", 
    "📊 Visualização & UX", 
    "📚 Documentação & Handover"
])

# ============================================
# TAB 1: DESIGN & MODELAGEM
# ============================================
with tab1:
    st.subheader("🎯 Princípios de Design")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.markdown("### 📐 Star Schema")
            st.markdown("""
            **Princípios Fundamentais:**
            - ✅ Tabelas fato no centro (transações)
            - ✅ Tabelas dimensão ao redor (descritivas)
            - ✅ Relacionamentos 1:N da dimensão para a fato
            - ✅ Evitar relacionamentos entre dimensões
            """)
    
    with col2:
        with st.container(border=True):
            st.markdown("### 🏷️ Nomenclatura")
            st.markdown("""
            | Tipo | Prefixo | Exemplo |
            |------|---------|---------|
            | Dimensão | `dim_` | `dim_cliente` |
            | Fato | `fato_` | `fato_vendas` |
            | Auxiliar | `aux_` | `aux_calendario` |
            | Medidas | `m_` | `m_total_vendas` |
            | Medidas Temporais | `mt_` | `mt_ytd` |
            | Medidas Percentuais | `mp_` | `mp_margem` |
            """)
    
    with st.container(border=True):
        st.markdown("### 📅 Dimensão de Data")
        st.markdown("**Colunas obrigatórias:**")
        st.code("""
        dim_data:
        - data (PK)
        - ano
        - trimestre
        - mes_numero
        - mes_nome
        - semana_ano
        - dia_mes
        - dia_semana
        - feriado (bool)
        - fim_de_semana (bool)
        """, language="sql")
    
    with st.container(border=True):
        st.markdown("### 📐 Exemplos de Medidas Padronizadas")
        st.code("""
        // Medida Básica
        m_total_vendas = SUMX(fato_vendas, [quantidade] * [preco])
        
        // Medida Temporal (YTD)
        mt_vendas_ytd = TOTALYTD([m_total_vendas], dim_data[data])
        
        // Medida Percentual
        mp_margem_lucro = DIVIDE([m_lucro], [m_total_vendas], 0)
        
        // Medida com Variáveis (recomendado)
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
        """, language="dax")

# ============================================
# TAB 2: POWER QUERY & ETL
# ============================================
with tab2:
    st.subheader("🔌 Boas Práticas em Power Query")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.markdown("### ✅ Checklist")
            st.markdown("""
            - [ ] Folding de consultas habilitado quando possível
            - [ ] Filtros aplicados o mais cedo possível
            - [ ] Remoção de colunas não utilizadas
            - [ ] Tipos de dados explicitamente definidos
            - [ ] Nomes de colunas padronizados (snake_case)
            - [ ] Parâmetros utilizados para fontes variáveis
            - [ ] Incremental refresh configurado
            - [ ] Validação de dados implementada
            """)
    
    with col2:
        with st.container(border=True):
            st.markdown("### 🎯 Boas Práticas Essenciais")
            st.markdown("""
            1. **Query Folding**: Sempre que usar SQL, verifique se as transformações são "foldadas"
            2. **Particionamento**: Use incremental refresh para tabelas grandes (>100M linhas)
            3. **Parâmetros**: Centralize valores como datas e caminhos
            4. **Documentação**: Adicione comentários explicando transformações complexas
            """)
    
    with st.container(border=True):
        st.markdown("### 📝 Exemplo: Parâmetros no Power Query")
        st.code("""
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
    
    with st.container(border=True):
        st.error("""
        ### ⚠️ Armadilhas Comuns
        
        - **Expansão prematura**: Expandir tabelas antes de filtrar
        - **Ignorar o folding**: Forçar transferência de todos os dados
        - **Colunas calculadas no Power Query**: Prefira transformações na fonte ou DAX
        - **Falta de validação**: Não verificar nulos, duplicatas e outliers
        """)

# ============================================
# TAB 3: DAX & PERFORMANCE
# ============================================
with tab3:
    st.subheader("⚡ Otimização de Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.markdown("### 🚀 Boas Práticas DAX")
            st.markdown("""
            1. **Prefira medidas** a colunas calculadas
            2. **Use variáveis** para cálculos repetidos
            3. **Evite funções iteradoras** (SUMX, AVERAGEX) em modelos grandes
            4. **Utilize CALCULATE com moderação**
            5. **Evite filtros** em colunas com alta cardinalidade (> 1M valores)
            6. **Use KEEPFILTERS** para respeitar filtros existentes
            """)
    
    with col2:
        with st.container(border=True):
            st.markdown("### 📈 Monitoramento")
            st.markdown("""
            **Ferramentas úteis:**
            - **DAX Studio** - Análise de planos de consulta
            - **Performance Analyzer** - Identificar visuais lentos
            - **VertiPaq Analyzer** - Analisar compressão de colunas
            
            **Métricas de referência:**
            - Tempo de resposta de visuais < 3 segundos
            - Modelo < 1GB (preferencialmente)
            - Uso de CPU < 70% em horário de pico
            """)
    
    with st.container(border=True):
        st.markdown("### 📊 Comparação: Medidas vs Colunas Calculadas")
        st.markdown("""
        | Aspecto | Medidas | Colunas Calculadas |
        |---------|---------|-------------------|
        | **Performance** | ⭐⭐⭐⭐⭐ | ⭐⭐ |
        | **Memória** | Calculada sob demanda | Armazenada no modelo |
        | **Filtros** | Dinâmicos | Estáticos |
        | **Recomendação** | Sempre que possível | Apenas quando necessário |
        """)

# ============================================
# TAB 4: VISUALIZAÇÃO & UX
# ============================================
with tab4:
    st.subheader("🎨 Design de Dashboards")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.markdown("### ✅ Boas Práticas")
            st.markdown("""
            - **Tipografia**: Inter ou Segoe UI (12pt corpo, 18pt títulos)
            - **Cores**: Paleta corporativa, máximo 6 cores por visual
            - **Layout**: Responsivo, espaço em branco adequado
            - **Tooltips**: Descritivos e relevantes
            - **Acessibilidade**: Alto contraste, suporte a leitores de tela
            """)
    
    with col2:
        with st.container(border=True):
            st.markdown("### ❌ Evitar")
            st.markdown("""
            - Cores neon ou muito vibrantes
            - Gráficos 3D sem necessidade
            - Rolagem horizontal excessiva
            - Mais de 2 categorias em gráficos de pizza
            - Elementos não interativos sem explicação
            """)
    
    with st.container(border=True):
        st.markdown("### 📊 Escolha do Visual por Objetivo")
        chart_data = pd.DataFrame({
            "Objetivo": ["Comparação", "Tendência", "Composição", "Distribuição", "Relacionamento"],
            "Recomendado": ["Barras, Colunas", "Linhas, Áreas", "Empilhado, Pizza (≤5)", "Histograma, Box Plot", "Dispersão, Bolhas"],
            "Evitar": ["Pizza", "3D", "Anéis (donut)", "Tabela densa", "Barras empilhadas"]
        })
        st.dataframe(chart_data, use_container_width=True, hide_index=True)
    
    with st.container(border=True):
        st.markdown("### 🎨 Recursos de Design")
        st.markdown("""
        - [Coolors](https://coolors.co/) - Gerador de paletas de cores
        - [Power Portal Temas](https://powerportal.com.br/temas.php) - Gerador de temas Power BI
        - [Data Viz Catalogue](https://datavizcatalogue.com/) - Catálogo de visuais
        - [Storytelling with Data](https://www.storytellingwithdata.com/) - Comunicação visual
        """)

# ============================================
# TAB 5: DOCUMENTAÇÃO & HANDOVER
# ============================================
with tab5:
    st.subheader("📚 Documentação e Entrega")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.markdown("### ✅ Checklist de Documentação")
            st.markdown("""
            - [ ] Diagrama do modelo (Star Schema)
            - [ ] Dicionário de dados com descrições
            - [ ] Lista de medidas com fórmulas e propósito
            - [ ] Documentação de segurança (RLS)
            - [ ] Instruções de refresh e dependências
            - [ ] Lista de contatos do time responsável
            - [ ] Guia de solução de problemas comuns
            """)
    
    with col2:
        with st.container(border=True):
            st.markdown("### 🛠️ Ferramentas")
            st.markdown("""
            - **Model Documenter** (SQLBI) - Documentação HTML automática
            - **Power BI REST API** - Extrai metadados programaticamente
            - **Tabular Editor** - Adicionar descrições e anotações
            - **Power BI Helper** - Exporta metadados completos
            """)
    
    with st.container(border=True):
        st.markdown("### 📄 Template de Handover")
        st.code("""
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
        """, language="markdown")

# ============================================
# SEÇÃO ADMIN (APENAS PARA EDITORES/ADMIN)
# ============================================
if can_edit_content or is_admin_user:
    st.divider()
    with st.expander("🔧 **Administração de Conteúdo**", expanded=False):
        st.warning("⚠️ Área restrita para editores e administradores")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("➕ Adicionar Nova Boa Prática")
            nova_categoria = st.selectbox("Categoria", [
                "Design", "Power Query", "DAX", "Visualização", "Documentação"
            ])
            novo_titulo = st.text_input("Título")
            novo_conteudo = st.text_area("Conteúdo", height=150)
            
            if st.button("💾 Salvar Nova Boa Prática", type="primary"):
                if novo_titulo and novo_conteudo:
                    try:
                        conn = get_connection()
                        cursor = conn.cursor()
                        from database import DB_TYPE
                        placeholder = '%s' if DB_TYPE == 'postgresql' else '?'
                        cursor.execute(f"""
                            INSERT INTO boas_praticas (titulo, categoria, conteudo, autor, autor_email)
                            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
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
                        st.markdown(f"**{p[1]}** - *{p[2]}* (por {p[3]})")
                    with col_b:
                        if st.button("🗑️", key=f"del_bp_{p[0]}"):
                            conn = get_connection()
                            cursor = conn.cursor()
                            from database import DB_TYPE
                            placeholder = '%s' if DB_TYPE == 'postgresql' else '?'
                            cursor.execute(f"DELETE FROM boas_praticas WHERE id = {placeholder}", (p[0],))
                            conn.commit()
                            cursor.close()
                            return_connection(conn)
                            st.rerun()
            else:
                st.info("Nenhuma boa prática personalizada ainda")

st.divider()
st.caption("💡 **Referência:** Baseado nas melhores práticas do Data Goblins, Microsoft Power BI e comunidade Analytics Engineering")
st.caption("📚 **Documentação oficial:** [Microsoft Learn - Power BI](https://learn.microsoft.com/power-bi/)")