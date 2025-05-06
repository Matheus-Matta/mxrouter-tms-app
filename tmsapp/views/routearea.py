from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from tmsapp.models import RouteArea
import json

@login_required
def create_routearea(request):
    if request.method == 'POST':
        name = request.POST.get('nomeRota')
        status = request.POST.get('statusRota')  # você pode guardar em outro campo se necessário
        color = request.POST.get('corRota')

        rota = RouteArea.objects.create(
            name=name,
            color_name=color,
            created_by=request.user,
        )

        return redirect('tmsapp:route_view', route_id=rota.id)

    return redirect('tmsapp:route_create')


@login_required
def route_view(request, route_id):
    rota = get_object_or_404(RouteArea, id=route_id)
    outras_rotas = RouteArea.objects.exclude(id=rota.id).exclude(geojson__isnull=True).exclude(geojson="")

    outras = []
    for r in outras_rotas:
        try:
            outras.append({
                "geojson": json.loads(r.geojson),
                "name": r.name,
            })
        except json.JSONDecodeError:
            pass

    return render(request, 'pages/routes/view_routearea.html', {
        "rota": rota,
        "outras": json.dumps(outras),
    })


@login_required
def edit_routearea(request, route_id):
    rota = get_object_or_404(RouteArea, id=route_id)
    if request.method == 'POST':
        try:
            rota.name = request.POST.get('nomeRota') or None
            rota.status = request.POST.get('statusRota') or None
            rota.color_name = request.POST.get('corRota') or None
            rota.areatotal = float(request.POST.get('areatotal').replace(',', '.')) if request.POST.get('areatotal') else None
            rota.kmtotal = float(request.POST.get('kmtotal').replace(',', '.')) if request.POST.get('kmtotal') else None

            geojson_raw = request.POST.get('geojson')
            # Tenta carregar e salvar como JSON serializado corretamente
            geojson_obj = json.loads(geojson_raw)
            print(geojson_obj, json.dumps(geojson_obj))
            rota.geojson = json.dumps(geojson_obj)
        except Exception as e:
            print(f"Erro ao carregar geojson: {e}")
            rota.geojson = None  # ou opcional: log do erro

        rota.save()
        return redirect('tmsapp:route_view', route_id=rota.id)

    return redirect('tmsapp:route')


@login_required
def delete_routearea(request, route_id):
    rota = get_object_or_404(RouteArea, id=route_id)

    if request.method == "POST":
        if rota.created_by == request.user or request.user.is_superuser:
            rota.delete()
            return redirect('tmsapp:route')  # redirecione para sua lista de rotas
        else:
            return redirect('tmsapp:route_view', route_id=route_id)  # sem permissão

    return redirect('tmsapp:route_view', route_id=route_id)