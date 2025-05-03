import requests
import json

# Endereços dos serviços
ORS_URL = "http://10.0.0.4:8080/ors/v2/directions/driving-car/geojson"
VROOM_URL = "http://10.0.0.4:8282/"

# Dados para a requisição ao ORS
ors_payload = {
    "coordinates": [
        [-43.36556, -22.971964],  # Copacabana
        [-43.2075, -22.90278]     # Centro do Rio
    ],
    "profile": "driving-hgv"
}

# Dados para a requisição ao VROOM
vroom_payload = {
    "jobs": [
        { "id": 1, "location": [-43.36556, -22.971964] },  # Copacabana
        { "id": 2, "location": [-43.2075, -22.90278] }     # Centro
    ],
    "vehicles": [
        { "id": 1, "start": [-43.36556, -22.971964], "profile": "driving-hgv" }
    ]
}


# Cabeçalhos comuns
headers = {
    "Content-Type": "application/json"
}

# Função para testar o ORS
def test_ors():
    try:
        response = requests.post(ORS_URL, headers=headers, json=ors_payload)
        data = response.json()
        print("Resposta do ORS:")
        print(json.dumps(data, indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar ao ORS: {e}")

# Função para testar o VROOM
def test_vroom():
    try:
        response = requests.post(VROOM_URL, headers=headers, json=vroom_payload)
        data = response.json()
        print(json.dumps(data, indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar ao VROOM: {e}")

if __name__ == "__main__":
    print("Testando o OpenRouteService (ORS)...")
    test_ors()
    print("\nTestando o VROOM...")
    test_vroom()
