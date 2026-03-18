import asyncio
import os
import sys

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.postgres import db
from app.rag.indexer import DocumentIndexer

# Base de conhecimento mockada para a versão de testes
MOCK_KNOWLEDGE = [
    {
        "source": "internacionalizacao_paraguai.pdf",
        "theme": "O Fim das Fronteiras Geográficas - Zonas Francas",
        "totem_tag": "TOTEM_INTERNACIONALIZACAO",
        "content": """
A globalização como conhecíamos mudou, mas o fim das fronteiras representa uma oportunidade extrema para redução de custo. 
Muitas empresas utilizam warehouses no Paraguai, não como indústrias engessadas, mas como zonas francas rápidas de negócios (maquila).
Isso garante segurança patrimonial off-shore e resolve a clássica 'Asfixia Tributária' que corrói margens no Brasil. 
O Custo Brasil é minimizado quando a montagem e importação ocorrem via zona franca paraguaia, garantindo um fôlego financeiro para escala.
        """
    },
    {
        "source": "vulcabras_e_sucessao.pdf",
        "theme": "O Gargalo do Fundador - Sucessão e Governança",
        "totem_tag": "TOTEM_SUCESSAO_GOVERNANCA",
        "content": """
A Vulcabras enfrentou uma quase falência e se reergueu através de uma sucessão ágil e governança de excelência. 
O princípio base na ViDi é claro: o CEO precisa sair da operação, ou a empresa morrerá com ele. O operacional aniquila o tático.
Na 'Guerra Infinita', o executivo sofre do 'Gargalo do Fundador' - trabalhando 14h por dia e centralizando liberação de pagamentos. 
Para resolver a 'Inércia do Sucesso', é exigido a instituição imediata de um conselho consultivo que retire do CEO o fardo do micro-gerenciamento.
        """
    },
    {
        "source": "arsenal_financeiro_cripto.pdf",
        "theme": "Arsenal Financeiro e Capital Inteligente",
        "totem_tag": "TOTEM_CAPITAL_INTELIGENTE",
        "content": """
No Brasil, a 'Dependência do FCO' e do crédito bancário de porta giratória destrói o caixa das empresas.
A solução está em Fundos Estruturados (FIDC), que entram no risco junto com o negócio de forma desburocratizada, com custos justos ao longo de prazos estendidos.
Além disso, a proteção do patrimônio exige alocação em Bitcoin e Criptomoedas como defesa contra inflação fiduciária e o 'Risco Brasil'.
Não confie sua proteção apenas aos gerentes de banco; dolarize via ativos puramente descentralizados e inconfiscáveis.
        """
    }
]

async def seed():
    print("Iniciando indexação da base de conhecimento (RAG)...")
    await db.connect()
    indexer = DocumentIndexer()

    # Limpa tabela para evitar duplicatas em re-run
    await db.execute("TRUNCATE TABLE knowledge_chunks RESTART IDENTITY;")
    print("🧹 Tabela knowledge_chunks limpa.")

    for doc in MOCK_KNOWLEDGE:
        print(f"📥 Indexando: {doc['source']}")
        await indexer.index_text(
            text=doc["content"],
            source=doc["source"],
            theme=doc["theme"],
            totem_tag=doc["totem_tag"]
        )

    await db.disconnect()
    print("✅ Indexação RAG concluída.")

if __name__ == "__main__":
    asyncio.run(seed())
