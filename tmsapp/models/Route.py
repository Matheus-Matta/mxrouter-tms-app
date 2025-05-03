from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords
from .Delivery import Delivery
from auditlog.registry import auditlog

class Route(models.Model):
    color = models.CharField("Color", max_length=7, default='#3498db')
    name = models.CharField("Name", max_length=100, null=True)
    created_at = models.DateTimeField("Created At", auto_now_add=True)
    updated_at = models.DateTimeField("Updated At", auto_now=True)
    created_by = models.ForeignKey(User, verbose_name="Created By", on_delete=models.SET_NULL, null=True, blank=True, related_name="routes_created")

    stops = models.IntegerField("Stops")
    distance_km = models.FloatField("Distance (km)")
    time_min = models.FloatField("Time (minutes)")
    geojson = models.JSONField("GeoJSON")
    points = models.JSONField("Points")
    
    deliveries = models.ManyToManyField(
        Delivery,
        through='RouteDelivery',
        related_name="routes",
        verbose_name="Deliveries"
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Rota"
        verbose_name_plural = "Rotas"

    def __str__(self):
        return self.name or "Unnamed Route"

class RouteDelivery(models.Model):
    route = models.ForeignKey('Route', on_delete=models.CASCADE)
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE)
    position = models.PositiveIntegerField("Order in Route")
    created_at = models.DateTimeField("Created At", auto_now_add=True)
    updated_at = models.DateTimeField("Updated At", auto_now=True)
    history = HistoricalRecords()
    class Meta:
        unique_together = ('route', 'delivery')  # Garante que não tenha entrega duplicada na mesma rota
        ordering = ['position']  # Sempre ordena pela posição
        verbose_name = "Parada de Rota"
        verbose_name_plural = "Paradas de Rota"

    def __str__(self):
        return f"{self.route.name} - {self.delivery.customer_name} (Posição {self.position})"

auditlog.register(Route)
auditlog.register(RouteDelivery)