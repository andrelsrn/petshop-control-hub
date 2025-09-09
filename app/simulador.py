import httpx
import asyncio
import random
from datetime import datetime, timedelta

API_URL = "http://127.0.0.1:8000/api/events"

# Dados de exemplo para simulação
PRODUCTS = ["RacaoSeca01", "BrinquedoBolinha05",
            "ColeiraCouro", "ShampooAntipulgas"]
SERVICES = ["Banho e Tosa Completo", "Consulta de Rotina",
            "Vacinação V10", "Corte de Unhas"]
PET_BREEDS = ["Labrador", "Poodle", "Bulldog Francês",
              "Shih Tzu", "SRD (Sem Raça Definida)"]
CUSTOMER_NAMES = ["Andre", "Beatriz", "Carlos", "Daniela", "Eduardo"]
PET_NAMES = ["Rex", "Luna", "Thor", "Mel", "Fred"]


async def send_event(client: httpx.AsyncClient):
    """Envia um evento aleatório para a API."""
    event_type = random.choice(["new-sale", "new-booking", "new-customer"])

    print(f"\n--- Gerando evento: {event_type} ---")

    if event_type == "new-sale":
        payload = {
            "product_id": random.choice(PRODUCTS),
            "quantity": random.randint(1, 3),
            "total_value": round(random.uniform(30.0, 350.0), 2),
            "customer_id": f"CUST_{random.randint(100, 200)}"
        }
        url = f"{API_URL}/new-sale"

    elif event_type == "new-booking":
        future_time = datetime.now() + timedelta(days=random.randint(1, 10),
                                                 hours=random.randint(1, 8))
        payload = {
            "service_name": random.choice(SERVICES),
            "pet_id": f"PET_{random.randint(1, 50)}",
            "scheduled_time": future_time.isoformat(),
            "employee_id": random.choice(["Juliana", "Marcos"]),
            "delivery": random.choice([True, False])
        }
        url = f"{API_URL}/new-booking"

    else:  # new-customer
        payload = {
            "name": f"{random.choice(CUSTOMER_NAMES)} {random.choice(['Silva', 'Souza', 'Costa'])}",
            "phone": f"219{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
            "address": f"Rua {random.randint(1, 100)}, Bairro {random.choice(['A', 'B', 'C'])}",
            "pet_name": random.choice(PET_NAMES),
            "pet_breed": random.choice(PET_BREEDS)
        }
        url = f"{API_URL}/new-customer"

    try:
        response = await client.post(url, json=payload, timeout=10.0)
        response.raise_for_status()
        print(
            f">>> Evento enviado com sucesso! Status: {response.status_code}")

    except httpx.RequestError as exc:
        print(f"!!! Erro ao enviar evento: {exc}")


async def main():
    print("Iniciando simulador de eventos para o Pet Control Hub...")
    async with httpx.AsyncClient() as client:
        while True:
            await send_event(client)
            sleep_time = random.randint(2, 5)
            await asyncio.sleep(sleep_time)

if __name__ == "__main__":
    asyncio.run(main())
