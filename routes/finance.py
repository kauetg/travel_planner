"""Integração com o Guardiola (app_financeiro) — lê/escreve direto no banco dele
(mesmo cluster Atlas, sem API entre os apps). Só usada pra viagens futuras: cria
um projeto lá quando a viagem nasce e busca as despesas ligadas a esse projeto.
"""

TRAVEL_PROJECT_CATEGORY = "Viagens"

# Mesmas categorias usadas nas activities do travel_planner (ver add_activity em
# routes/trip.py) — assim dá pra comparar planejado (activities) com real
# (Guardiola) categoria a categoria na aba Finances.
FIN_CATEGORIES = [
    ("food", "Food", "bi-cup-hot-fill"),
    ("transportation", "Transportation", "bi-airplane-fill"),
    ("accommodation", "Accommodation", "bi-house-door-fill"),
    ("activity", "Activities", "bi-camera-fill"),
    ("other", "Others", "bi-three-dots"),
]
FIN_CATEGORY_KEYS = [key for key, _, _ in FIN_CATEGORIES]

# O Guardiola tem ~18 categorias de despesa (household-scoped, editáveis lá em
# Configurações), granulares demais pra comparar com as 5 categorias de viagem
# acima. O que não mapeia aqui cai em "other" — não mexe em nada do lado do
# Guardiola, só reagrupa pra exibição.
EXPENSE_CATEGORY_MAP = {
    "Comida": "food",
    "Mercado": "food",
    "Bar tab": "food",
    "Transporte": "transportation",
    "Acomodacao": "accommodation",
    "Entretenimento": "activity",
    "Equipamento de mergulho": "activity",
}
DEFAULT_CATEGORY_KEY = "other"


def get_household_id(finance_db, email):
    user = finance_db.users.find_one({"email": email})
    return user["household_id"] if user else None


def list_travel_projects(finance_db, household_id):
    return list(
        finance_db.projects.find(
            {"household_id": household_id, "category": TRAVEL_PROJECT_CATEGORY}
        ).sort("start_date", -1)
    )


def create_project_for_trip(finance_db, household_id, name, start_date, end_date):
    result = finance_db.projects.insert_one(
        {
            "household_id": household_id,
            "name": name,
            "category": TRAVEL_PROJECT_CATEGORY,
            "start_date": start_date,
            "end_date": end_date,
            "notes": "",
        }
    )
    return result.inserted_id


def get_trip_expenses(finance_db, project_id):
    transactions = list(
        finance_db.transactions.find({"project_id": project_id, "type": "expense"}).sort("date", -1)
    )

    total_usd = 0.0
    category_totals = {key: 0.0 for key in FIN_CATEGORY_KEYS}
    for t in transactions:
        amount_usd = t.get("amount_usd", 0)
        total_usd += amount_usd
        key = EXPENSE_CATEGORY_MAP.get(t["category"], DEFAULT_CATEGORY_KEY)
        category_totals[key] += amount_usd

    return {
        "transactions": transactions,
        "total_usd": round(total_usd, 2),
        "category_totals": {k: round(v, 2) for k, v in category_totals.items()},
    }
