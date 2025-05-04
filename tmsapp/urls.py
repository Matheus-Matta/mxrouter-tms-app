from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView
from .views import create_routes, get_company_locations_api, explore_route, route_compositions_data
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

app_name = 'tmsapp'

urlpatterns = [
  
  # paginas de rotas
  path(
        'scripting/',
        login_required(lambda request: render(request, 'pages/router.html')),
        name='scripting'
  ),
  # pagina de loading rotas
  path(
        'route/loading/<uuid:task_id>/',
        login_required(lambda request, task_id: render(request, 'partials/loading/route_loading.html', {'task_id': task_id})),
        name='route_loading'
  ),

  # pagina de visualizar rotas
  path('route/explore/<int:composition_id>/', explore_route , name='explore_routes'),
  # pegar todas as localizações da empresa
  path('route/get_company_locations', get_company_locations_api, name='get_company_locations'), 
  # criar rotas
  path('route/create_routes', create_routes, name='create_routes'),
  # pegar todas as rotas e composiçoes
  path('route/route_compositions_data/', route_compositions_data, name='route_compositions_data'),
]