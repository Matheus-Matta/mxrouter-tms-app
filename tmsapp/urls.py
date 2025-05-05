from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView
from .views import create_routes, get_company_locations_api, explore_route, route_compositions_data, CreateRoutesView, route_loading_view
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

app_name = 'tmsapp'

urlpatterns = [
  
  ####### SCRIPTING PATH 
  path(
        'scripting/create',
        login_required(lambda request: render(request, 'pages/router.html')),
        name='create_scripting'
  ),
  # pagina de loading rotas
  path(
    'scripting/loading/<uuid:task_id>/',
    route_loading_view,
    name='route_loading'
  ),
  # pagina de visualizar rotas
  path('scripting/explore/<int:composition_id>/', explore_route , name='explore_routes'),
  # pegar todas as localizações da empresa
  path('scripting/get_company_locations', get_company_locations_api, name='get_company_locations'), 
  # criar rotas
  path('scripting/create_routes', create_routes, name='create_routes'),
  # pegar todas as rotas e composiçoes
  path('scripting/route_compositions_data/', route_compositions_data, name='route_compositions_data'),


 

  ####### ROUTE PATH 
  path('route/create/', CreateRoutesView.as_view(), name='route_create'),




]