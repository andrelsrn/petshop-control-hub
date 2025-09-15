import httpx
import asyncio
import random
from datetime import datetime, timedelta

API_URL = "http://127.0.0.1:8000"

# Dados de exemplo para simulação
PRODUCTS = ["RacaoSeca01", "BrinquedoBolinha05", "ColeiraCouro", "ShampooAntipulgas"]
EMPLOYEE_NAMES = ["Juliana", "Marcos"]
SERVICES = ["Banho e Tosa Completo", "Consulta de Rotina", "Vacinação V10", "Corte de Unhas"]
PET_BREEDS = ["Labrador", "Poodle", "Bulldog Francês", "Shih Tzu", "SRD (Sem Raça Definida)"]
CUSTOMER_NAMES = ["Andre", "Beatriz", "Carlos", "Daniela", "Eduardo"]
PET_NAMES = ["Rex", "Luna", "Thor", "Mel", "Fred"]

# Listas para rastrear os IDs criados e garantir a integridade dos dados
created_customers = []
created_pets = []
created_employees = []
created_inventory = []

async def post_to_api(client, url, payload):
    try:
        response = await client.post(url, json=payload, timeout=10.0)
        response.raise_for_status()
        return response.json()
    except httpx.RequestError as exc:
        print(f"!!! Erro ao enviar evento para {url}: {exc}")
        return None
    except httpx.HTTPStatusError as exc:
        print(f"!!! Erro na resposta da API: {exc.response.text}")
        return None

async def create_base_resources(client: httpx.AsyncClient):
    
    # 1. Cria itens de inventário
    for product_name in PRODUCTS:
        payload = {
            "product_name": product_name,
            "quantity": random.randint(10, 50),
            "price": round(random.uniform(25.0, 150.0), 2),
            "low_stock_threshold": random.randint(5, 10)
        }
        res = await post_to_api(client, f"{API_URL}/api/inventory/", payload)
        if res:
            created_inventory.append(res["id"])
    
    # 2. Cria clientes 
    for name in CUSTOMER_NAMES:
        payload = {
            "name": f"{name} {random.choice(['Silva', 'Souza', 'Costa'])}",
            "phone": f"219{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
            "address": f"Rua {random.randint(1, 100)}, Bairro {random.choice(['A', 'B', 'C'])}"
        }
        res = await post_to_api(client, f"{API_URL}/api/events/new-customer", payload)
        if res:
            created_customers.append(res["id"])

    # 3. Cria funcionários
    for name in EMPLOYEE_NAMES:
        payload = {
            "name": name,
            "job_title": "Tosador",
            "phone": f"219{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
        }
        res = await post_to_api(client, f"{API_URL}/api/events/new-employee", payload)
        if res:
            created_employees.append(res["id"])

    # 4. Cria pets (agora associados a clientes válidos)
    for pet_name in PET_NAMES:
        if created_customers:
            payload = {
                "name": pet_name,
                "breed": random.choice(PET_BREEDS),
                "date_of_birth": (datetime.now() - timedelta(days=random.randint(100, 1500))).isoformat(),
                "customer_id": random.choice(created_customers)
            }
            res = await post_to_api(client, f"{API_URL}/api/pets/", payload)
            if res:
                created_pets.append(res["id"])

async def send_random_event(client: httpx.AsyncClient):
    event_type = random.choice(["new-sale", "new-booking"])
    
    if event_type == "new-sale":
        if not created_inventory or not created_customers:
            return

        payload = {
            # Altere para usar 'product_name' e 'customer_id' como int
            "product_name": random.choice(PRODUCTS),
            "quantity": random.randint(1, 3),
            "total_value": round(random.uniform(30.0, 350.0), 2),
            "customer_id": random.choice(created_customers)
        }
        await post_to_api(client, f"{API_URL}/api/events/new-sale", payload)


    elif event_type == "new-booking":
        if not created_pets or not created_employees:
            return

        future_time = datetime.now() + timedelta(days=random.randint(1, 10), hours=random.randint(1, 8))
        payload = {
            "service_name": random.choice(SERVICES),
            "pet_id": random.choice(created_pets),
            "scheduled_time": future_time.isoformat(),
            "employee_id": random.choice(created_employees),
            "delivery": random.choice([True, False])
        }
        await post_to_api(client, f"{API_URL}/api/events/new-booking", payload)

async def main():
    print("Iniciando simulador de eventos...")
    async with httpx.AsyncClient() as client:
        await create_base_resources(client)
        print("Recursos base criados. Iniciando o fluxo de eventos.")

        while True:
            await send_random_event(client)
            sleep_time = random.randint(2, 5)
            await asyncio.sleep(sleep_time)

if __name__ == "__main__":
    asyncio.run(main())