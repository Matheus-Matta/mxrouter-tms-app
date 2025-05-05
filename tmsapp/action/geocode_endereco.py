import requests
import logging
from decouple import config

GOOGLE_API_KEY = config('GOOGLE_API_KEY', default='NÃO-POSSUI-API-KEY')

def consultar_cep_viacep(cep):
    """Consulta um CEP no ViaCEP e retorna dados estruturados de endereço."""
    cep = ''.join(filter(str.isdigit, str(cep)))

    if len(cep) != 8:
        logging.warning(f"[ViaCEP] CEP inválido: {cep}")
        return None

    url = f"https://viacep.com.br/ws/{cep}/json/"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        if "erro" in data:
            logging.warning(f"[ViaCEP] CEP não encontrado: {cep}")
            return None

        logging.warning(f"[ViaCEP] Resultado para CEP {cep}: {data}")
        return {
            "rua": data.get("logradouro", ""),
            "bairro": data.get("bairro", ""),
            "cidade": data.get("localidade", ""),
            "estado": data.get("uf", ""),
            "cep": data.get("cep", "")
        }

    except Exception as e:
        logging.warning("[ViaCEP] Erro ao consultar CEP", exc_info=e)

    return None

def geocode_endereco(endereco, numero=None, postal_code=None, bairro=None, cidade=None, estado=None):
    """
    Usa Geocoding com components para obter lat/lng.
    Segunda tentativa: via ViaCEP.
    Terceira tentativa: autocomplete + nova consulta geocode.
    """
    geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"

    # Primeira tentativa: geocodificação usando components
    components = []
    if estado:
        components.append(f"administrative_area:{estado}")
    if cidade:
        components.append(f"locality:{cidade}")
    if postal_code:
        components.append(f"postal_code:{postal_code}")
    if components:
        components.append("country:br")

    params = {
        "address": f"{endereco}, {numero if int(numero) > 0 else '1'}, {bairro}",
        "key": GOOGLE_API_KEY
    }

    if components:
        params["components"] = "|".join(components)

    try:
        logging.warning(f"[Geocode] Primeira tentativa com components: {params}")
        response = requests.get(geocode_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data['status'] == 'OK' and data.get('results'):
            loc = data['results'][0]['geometry']['location']
            end_fmt = data['results'][0]['formatted_address']
            print(loc['lat'], loc['lng'])
            return loc['lat'], loc['lng']

    except Exception as e:
        logging.warning("[Geocode] Primeira tentativa falhou", exc_info=e)

    # Segunda tentativa: consulta ao ViaCEP se tiver postal_code
    if postal_code:
        via_cep = consultar_cep_viacep(postal_code)
        if via_cep:
            endereco_cep = f"{via_cep['rua']}, {numero}, {via_cep['bairro']}, {via_cep['cidade']}, {via_cep['estado']}, {via_cep['cep']}, Brasil"
            params_cep = {
                "address": endereco_cep,
                "key": GOOGLE_API_KEY
            }

            try:
                logging.warning(f"[Geocode] Segunda tentativa via ViaCEP: {params_cep}")
                response = requests.get(geocode_url, params=params_cep, timeout=10)
                response.raise_for_status()
                data = response.json()

                if data['status'] == 'OK' and data.get('results'):
                    loc = data['results'][0]['geometry']['location']
                    end_fmt = data['results'][0]['formatted_address']
                    print(loc['lat'], loc['lng'])
                    return loc['lat'], loc['lng']

            except Exception as e:
                logging.warning("[Geocode] Segunda tentativa com ViaCEP falhou", exc_info=e)

    # Terceira tentativa: autocomplete
    params_auto = {
        "address": f"{endereco}, {numero if int(numero) > 0 else '1'}, {bairro}, {cidade}, {postal_code}, {estado}, Brasil",
        "key": GOOGLE_API_KEY
    }

    try:
        logging.warning(f"[Geocode] Terceira tentativa com autocomplete: {params_auto}")
        response = requests.get(geocode_url, params=params_auto, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data['status'] == 'OK' and data.get('results'):
            loc = data['results'][0]['geometry']['location']
            end_fmt = data['results'][0]['formatted_address']
            
            return loc['lat'], loc['lng']

    except Exception as e:
        logging.warning("[Geocode] Terceira tentativa falhou", exc_info=e)

    return None, None


print(geocode_endereco('RUA NOVE' , '0', '24000000', 'PARQUE AURORA', 'ITABORAI', 'RJ'))