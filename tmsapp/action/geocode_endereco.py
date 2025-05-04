import requests
from decouple import config

GOOGLE_API_KEY = config('GOOGLE_API_KEY', default='NÃO-POSSUI-API-KEY')

def geocode_endereco(endereco):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": endereco,
        "key": GOOGLE_API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data['status'] == 'OK' and data['results']:
            location = data['results'][0]['geometry']['location']
            return location['lat'], location['lng']
        else:
            print("Erro na resposta:", data.get('status'), data.get('error_message'))
            return None, None

    except requests.RequestException as e:
        print("Erro na requisição:", e)
        return None, None