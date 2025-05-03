from tmsapp.models import Delivery, Route, RouteComposition, RouteDelivery
from tmsapp.action import get_geojson_by_ors, read_file_to_dataframe
from django.core.files.storage import default_storage
from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer
from tmsapp.action import geocode_endereco
from asgiref.sync import async_to_sync
from collections import defaultdict
from django.db import transaction
from celery import shared_task
from datetime import datetime
import pandas as pd
import random
import time
import os


User = get_user_model()

def generate_random_color():
    return '#' + ''.join(random.choices('0123456789ABCDEF', k=6))

def sanitize(value):
    if pd.isna(value) or str(value).strip().lower() == 'nan':
        return ''
    return str(value).strip()

def send_task_update(task_id, message, percent, composition_id=None):
    """Envia atualização para WebSocket."""
    channel_layer = get_channel_layer()

    event = {
        'type': 'task_progress_update',
        'progress': message,
        'percent': percent,
    }

    if composition_id is not None:
        event['composition_id'] = composition_id

    async_to_sync(channel_layer.group_send)(
        f'task_progress_{task_id}',
        event
    )

@shared_task(bind=True)
def create_routes_task(self, user_id, sp_router, temp_file_path):
    time.sleep(3)
    user = User.objects.get(id=user_id)
    galpao_coords = [-42.9455242, -22.7920595, 'Seu Galpão']

    task_id = self.request.id

    try:
        send_task_update(task_id, 'Lendo planilha...', 5)

        df = read_file_to_dataframe(temp_file_path) 

        with transaction.atomic():
            send_task_update(task_id, 'Importando entregas...', 6)

            deliveries_objects = []
            total_rows = len(df)
            for index, row in df.iterrows():

                progress_percent = 6 + int((index + 1) / total_rows * (40 - 6))
                send_task_update(task_id, f"Processando entrega {index + 1}/{total_rows}", progress_percent)

                order_number = sanitize(row.get("numerosaida"))
                if not order_number:
                    continue  # pula linhas inválidas

                customer_name = sanitize(row.get('nomecliente'))
                street = sanitize(row.get('ruaentrega'))
                number = sanitize(row.get('numeroentrega'))
                neighborhood = sanitize(row.get('bairroentrega'))
                city = sanitize(row.get('cidadeentrega')).split('-')[0].strip()
                address = sanitize(row.get('enderecoentrega'))
                postal_code = sanitize(row.get('cepentrega')) 
                state = 'Rio de janeiro'  # fixo, pode manter assim

                endereco_formatado = [
                    address,
                    number,
                    neighborhood,
                    city,
                    state,
                    postal_code,
                    "Brasil"
                ]

                endereco_str = ', '.join(filter(None, endereco_formatado))
                latitude, longitude = geocode_endereco(endereco_str)

                deliveries_objects.append(
                    Delivery(
                        customer_name=customer_name,
                        order_number=str(int(float(order_number))),
                        route_name=sanitize(row.get('nomerota')),
                        street=street,
                        number=str(int(float(number))),
                        neighborhood=neighborhood,
                        city=city,
                        state=state,
                        phone=sanitize(row.get('telefoneentrega')),
                        observation=sanitize(row.get('observacao')),
                        address=address,
                        cpf=sanitize(row.get('doctocliente')),
                        reference=sanitize(row.get('pontoreferenciaentrega')),
                        postal_code=str(int(float(postal_code))),
                        latitude=latitude,
                        longitude=longitude,
                        created_by=user
                    )
                )

            Delivery.objects.bulk_create(deliveries_objects, batch_size=1000)

            deliveries = Delivery.objects.filter(created_by=user).order_by('-created_at')[:len(deliveries_objects)]

            send_task_update(task_id, 'Criando composição...', 41)

            composition = RouteComposition.objects.create(
                name=f"Composition {datetime.now().strftime('%d-%m-%Y %H:%M')}",
                type=sp_router,
                created_by=user
            )

            if sp_router == 'unique':
                send_task_update(task_id, 'Otimizando rota única...', 50)

                deliveries_coords = [
                    {
                        'long': float(d.longitude),
                        'lat': float(d.latitude),
                        'order_number': d.order_number
                    }
                    for d in deliveries
                    if d.latitude is not None and d.longitude is not None
                ]

                all_coords = [{'long': galpao_coords[0], 'lat': galpao_coords[1], 'order_number': 'SAIDA'}] + deliveries_coords

                geojson, duration, delivery_ordered = get_geojson_by_ors(all_coords)

                route = Route.objects.create(
                    name="Rota única",
                    color=generate_random_color(),
                    created_by=user,
                    stops=len(deliveries),
                    distance_km=round(duration / 1000, 2),
                    time_min=round(duration / 60, 1),
                    geojson=geojson,
                    points=all_coords,
                )

                order_number_to_delivery = {d.order_number: d for d in deliveries}
                
                for position, stop in enumerate(delivery_ordered):
                    delivery = order_number_to_delivery.get(stop['order_number'])
                    if delivery and not RouteDelivery.objects.filter(route=route, delivery=delivery).exists():
                        RouteDelivery.objects.create(
                            route=route,
                            delivery=delivery,
                            position=position
                        )

                send_task_update(task_id, 'Finalizando...', 92)
                composition.routes.add(route)

            elif sp_router == 'city':

                send_task_update(task_id, 'Otimizando rotas por cidade...', 50)

                deliveries_temp = []
                route_groups = defaultdict(list)

                for delivery in deliveries:
                    if (delivery.route_name or '').lower() == 'marketplace':
                        deliveries_temp.append(delivery)
                    else:
                        route_groups[delivery.route_name].append(delivery)

                for delivery in deliveries_temp:
                    found = False
                    for route_key in route_groups:
                        if (delivery.city or '').lower() in route_key.lower():
                            route_groups[route_key].append(delivery)
                            found = True
                            break
                    if not found:
                        route_groups[f"{delivery.city}"].append(delivery)
                        
                route_groups = dict(sorted(route_groups.items(), key=lambda item: item[0].lower()))
                total_routes = len(route_groups)
                route_count = 0

                for route_name, city_deliveries in route_groups.items():
                    route_count += 1
                    percent = 50 + int(40 * (route_count / total_routes))

                    send_task_update(task_id, f"Otimizando rota {route_name}...", percent)

                    deliveries_coords = [
                        {
                            'long': float(d.longitude),
                            'lat': float(d.latitude),
                            'order_number': d.order_number
                        }
                        for d in city_deliveries
                        if d.latitude is not None and d.longitude is not None
                    ]

                    all_coords = [{'long': galpao_coords[0], 'lat': galpao_coords[1], 'order_number': 'SAIDA'}] + deliveries_coords

                    geojson, duration, delivery_ordered = get_geojson_by_ors(all_coords)

                    route = Route.objects.create(
                        name=f"{route_name}",
                        color=generate_random_color(),
                        created_by=user,
                        stops=len(city_deliveries),
                        distance_km=round(duration / 1000, 2),
                        time_min=round(duration / 60, 1),
                        geojson=geojson,
                        points=all_coords,
                    )

                    order_number_to_delivery = {d.order_number: d for d in city_deliveries}

                    for position, stop in enumerate(delivery_ordered):
                        delivery = order_number_to_delivery.get(stop['order_number'])
                        if delivery and not RouteDelivery.objects.filter(route=route, delivery=delivery).exists():
                            RouteDelivery.objects.create(
                                route=route,
                                delivery=delivery,
                                position=position
                            )

                    composition.routes.add(route)

                send_task_update(task_id, 'Finalizando...', 92)

        send_task_update(task_id, 'Finalizado', 100, composition.id)

        return {'status': 'Concluído', 'composition_id': composition.id}

    except Exception as e:
        send_task_update(task_id, f"❌ Erro: {str(e)}", 0)
        raise e

    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
