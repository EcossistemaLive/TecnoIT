import asyncio
import os
import sys

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.postgres import db
import json

PARTICIPANTS = [
    {
        "full_name": "Carlos Mendes",
        "cpf": "11144477735",
        "whatsapp_primary": "5562999990001",
        "company": "TechLog",
        "role": "CEO",
        "upsell_category": "A",
        "annual_revenue_bracket": "R$ 5M - 10M",
        "diagnosis": {
            "pain_label": "Gargalo do Fundador",
            "pain_description": "Trabalho 14h por dia apagando incêndios. A empresa não funciona se eu não estiver presente.",
            "governance_score": 3.0,
            "succession_urgency": 9.0,
            "financial_stress": 5.0,
            "work_hours_per_day": 14.0
        }
    },
    {
        "full_name": "Ana Ferreira",
        "cpf": "22255588866",
        "whatsapp_primary": "5511988880002",
        "company": "AgroBraz",
        "role": "Diretora Financeira",
        "upsell_category": "B",
        "annual_revenue_bracket": "R$ 1M - 5M",
        "diagnosis": {
            "pain_label": "Dependência do FCO",
            "pain_description": "Fluxo de caixa apertado. Dependência total de linhas de crédito tradicionais como o FCO, sem alternativas para escalar.",
            "governance_score": 6.0,
            "succession_urgency": 4.0,
            "financial_stress": 8.0,
            "work_hours_per_day": 10.0
        }
    },
    {
        "full_name": "Roberto Silva",
        "cpf": "33366699997",
        "whatsapp_primary": "5519977770003",
        "company": "Silva Import",
        "role": "Sócio Fundador",
        "upsell_category": "C",
        "annual_revenue_bracket": "Até R$ 1M",
        "diagnosis": {
            "pain_label": "Asfixia Tributária",
            "pain_description": "Interesse forte em internacionalização. A alta carga de impostos no Brasil está asfixiando nossas margens.",
            "governance_score": 5.0,
            "succession_urgency": 2.0,
            "financial_stress": 7.0,
            "work_hours_per_day": 9.0
        }
    }
]

async def seed():
    print("Iniciando seed de participantes de teste...")
    await db.connect()

    for p in PARTICIPANTS:
        try:
            # Insere Participante
            query_p = """
                INSERT INTO participants (full_name, cpf, whatsapp_primary, company, role, upsell_category, annual_revenue_bracket)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (cpf) DO UPDATE SET 
                    upsell_category = EXCLUDED.upsell_category 
                RETURNING id;
            """
            participant_id = await db.fetchrow(
                query_p,
                p["full_name"], p["cpf"], p["whatsapp_primary"], p["company"],
                p["role"], p["upsell_category"], p["annual_revenue_bracket"]
            )
            
            p_id = participant_id['id']
            diag = p["diagnosis"]

            # Insere Diagnóstico
            query_d = """
                INSERT INTO diagnoses (
                    participant_id, pain_label, pain_description, governance_score, 
                    succession_urgency, financial_stress, work_hours_per_day, raw_responses
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """
            await db.execute(
                query_d,
                p_id, diag["pain_label"], diag["pain_description"], diag["governance_score"],
                diag["succession_urgency"], diag["financial_stress"], diag["work_hours_per_day"], json.dumps(diag)
            )

            print(f"✅ Inserido: {p['full_name']} (CPF: {p['cpf']})")
            
        except Exception as e:
            print(f"❌ Erro ao inserir {p['full_name']}: {e}")

    await db.disconnect()
    print("Seed concluído.")

if __name__ == "__main__":
    asyncio.run(seed())
