# inserir_casos.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_connection, return_connection, DB_TYPE

# Lista dos casos de uso
casos_de_uso = [
    {
        "titulo": "DAX Studio para remoção de colunas 'órfãs'",
        "contexto": "Performance",
        "tecnologia": "DAX Studio (VertiPaq Analyzer)",
        "descricao": "O modelo de dados estava extremamente lento para carregar e o arquivo .pbix estava muito pesado, dificultando a publicação e o consumo pelos usuários finais.",
        "resultado": "Utilizei o recurso View Metrics do DAX Studio para rodar o VertiPaq Analyzer. Identifiquei que 80% do tamanho do modelo vinha de colunas de 'Data/Hora' com alta cardinalidade (segundos) que não eram usadas em nenhum relatório. Removi essas colunas e reduzi o tamanho do modelo em 65%, melhorando instantaneamente a performance das medidas DAX.",
        "tags": "performance, otimização, dax studio, vertipaq, colunas órfãs",
        "autor": "Camila Machado",
        "autor_email": "camila.machado@artefact.com"
    },
    {
        "titulo": "Power Automate para atualização automática com controle de período crítico",
        "contexto": "Performance",
        "tecnologia": "Power Automate (Cloud Flows)",
        "descricao": "Necessidade de gerir uma atualização mensal de dados que deve ser interrompida em um período crítico (fechamento contábil do dia 25 ao dia 30) para evitar inconsistências, retomando automaticamente no dia 1º do mês seguinte.",
        "resultado": "Criei um fluxo recorrente no Power Automate que, antes de disparar a atualização do dataset no Power BI Service, executa uma condição lógica. Um script verifica a data atual: se estiver entre os dias 25 e 30, o fluxo termina com sucesso sem disparar o refresh; caso contrário, ele inicia a atualização e envia uma confirmação no Teams. Isso garantiu a integridade dos dados sem intervenção manual.",
        "tags": "automação, power automate, refresh, controle, teams, fechamento contábil",
        "autor": "Camila Machado",
        "autor_email": "camila.machado@artefact.com"
    },
    {
        "titulo": "Sincronia entre atualizações de 3 plataformas (Databricks, Power BI e SharePoint)",
        "contexto": "Conectividade",
        "tecnologia": "Azure Databricks, Power BI Service, Power Automate",
        "descricao": "Necessidade de criar um fluxo seamless onde a atualização append quinzenal de uma tabela no Databricks fosse refletida no Power BI e, em seguida, criasse novos itens em uma lista no SharePoint, evitando conflitos de horários.",
        "resultado": "Liguei todas as triggers em eventos, ao invés de horários. A pipeline do Databricks aciona via API a atualização do dataset no Power BI Service. O sucesso da atualização é o trigger para o fluxo do Power Automate que escreve os itens no SharePoint. O fluxo também verifica se a data de atualização da tabela é mais recente que a última data do SharePoint, garantindo que apenas dados novos sejam inseridos.",
        "tags": "integração, databricks, power bi, power automate, sharepoint, eventos",
        "autor": "Ian Cidade",
        "autor_email": "ian.cidade@artefact.com"
    },
    {
        "titulo": "Deneb (Vega-Lite) para visual customizado de Gantt com mudanças de contexto temporal",
        "contexto": "UX/UI",
        "tecnologia": "Deneb, Vega-Lite",
        "descricao": "Necessidade de construir um visual do tipo Gantt no Power BI, não suportado nativamente. O principal desafio era refletir mudanças de contexto ao longo do tempo, especificamente alterações de Target Class em diferentes quarters, baseadas em timestamps.",
        "resultado": "Utilizei o Deneb (Vega-Lite) para criar um visual customizado a partir de uma estrutura declarativa em JSON. Com Vega-Lite, foi possível construir um Gantt totalmente customizado com controle de exibição baseado em timestamps e implementar a lógica de mudança de Target Class ao longo do tempo. A abordagem trouxe flexibilidade total sobre o comportamento do visual.",
        "tags": "deneb, vega-lite, gantt, custom visual, power bi, temporal",
        "autor": "Raissa Azevedo",
        "autor_email": "raissa.azevedo@artefact.com"
    },
    {
        "titulo": "Mudança em massa de SELECT * para SELECT de colunas específicas",
        "contexto": "Performance",
        "tecnologia": "Databricks, .pbip (Power BI), VS Code",
        "descricao": "Necessidade de migrar das queries de SELECT * usadas durante o desenvolvimento para SELECT de colunas específicas durante a produtização do projeto, otimizando performance e reduzindo tamanho do arquivo.",
        "resultado": "Utilizei SHOW COLUMNS no Databricks para listar as colunas e tipos de dados necessários. Em seguida, usei o formato .pbip com VS Code para alterar o código M das tabelas no arquivo expressions.tmdl. Ao salvar a versão alterada, o Power BI atualizou todas as queries de uma só vez, eliminando ajustes manuais. O resultado foi uma redução de aproximadamente 70MB no tamanho do arquivo.",
        "tags": "otimização, databricks, power bi, pbip, performance, select",
        "autor": "Ian Cidade",
        "autor_email": "ian.cidade@artefact.com"
    },
    {
        "titulo": "Garantir que hard requirements do cliente sejam conhecidos e implementados no tempo correto do projeto",
        "contexto": "Governança",
        "tecnologia": "N/A",
        "descricao": "No projeto da Dior, requisitos documentados no início do projeto foram perdidos de vista, retornando nas últimas semanas quando o time já estava apertado de prazo. Isso incluiu padrões de nomenclatura, boas práticas, Design System e restrições de acesso a dados de produção.",
        "resultado": "A lição aprendida foi a necessidade de implementar um processo estruturado de gestão de requirements na fase de discovery: mapeamento claro de todos os requisitos; validação de padrões de nomenclatura para SQL e modelo semântico; alinhamento de boas práticas recomendadas pelo cliente; definição de utilização do Design System; e validação antecipada de acessos a dados de produção. Com esses requisitos claros desde o início, é possível planejar ações de mitigação.",
        "tags": "governança, requirements, discovery, gestão, lições aprendidas, dior",
        "autor": "Henrique Toledo",
        "autor_email": "henrique.toledo@artefact.com"
    }
]

print("🚀 Inserindo casos de uso no banco de dados...")
print(f"📊 Total de casos: {len(casos_de_uso)}")

conn = get_connection()
cursor = conn.cursor()

# Verificar se a tabela existe
cursor.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = 'casos_uso'
    )
""")
tabela_existe = cursor.fetchone()[0]

if not tabela_existe:
    print("❌ Tabela 'casos_uso' não existe!")
    print("📝 Execute primeiro o SQL de criação da tabela:")
    print("""
    CREATE TABLE IF NOT EXISTS casos_uso (
        id SERIAL PRIMARY KEY,
        titulo VARCHAR(500) NOT NULL,
        contexto TEXT NOT NULL,
        tecnologia VARCHAR(100) NOT NULL,
        descricao TEXT NOT NULL,
        resultado TEXT,
        tags TEXT,
        autor VARCHAR(255) NOT NULL,
        autor_email VARCHAR(255) NOT NULL,
        data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    cursor.close()
    conn.close()
    sys.exit(1)

# Inserir os casos
contador = 0
for caso in casos_de_uso:
    cursor.execute("""
        INSERT INTO casos_uso (titulo, contexto, tecnologia, descricao, resultado, tags, autor, autor_email)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (titulo) DO NOTHING
    """, (
        caso['titulo'], 
        caso['contexto'], 
        caso['tecnologia'], 
        caso['descricao'], 
        caso['resultado'], 
        caso['tags'], 
        caso['autor'], 
        caso['autor_email']
    ))
    
    if cursor.rowcount > 0:
        contador += 1
        print(f"   ✅ Inserido: {caso['titulo'][:50]}...")

conn.commit()

# Verificar total
cursor.execute("SELECT COUNT(*) FROM casos_uso")
total = cursor.fetchone()[0]

cursor.close()
return_connection(conn)

print(f"\n✅ Inseridos {contador} novos casos de uso!")
print(f"📊 Total de casos de uso no banco: {total}")

# Listar todos os casos inseridos
print("\n📋 Casos de uso no banco:")
conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT id, titulo, autor FROM casos_uso ORDER BY id")
for row in cursor.fetchall():
    print(f"   {row[0]}. {row[1]} - {row[2]}")
cursor.close()
return_connection(conn)