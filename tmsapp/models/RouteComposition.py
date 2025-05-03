
from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords
from .Route import Route
from auditlog.registry import auditlog

class RouteType(models.TextChoices):
    CITY = 'city', 'Rotas por cidade'
    UNIQUE = 'unique', 'Rota unica'
    OTHER = 'other', 'Outro'


class RouteComposition(models.Model):
    name = models.CharField("Name", max_length=100)
    type = models.CharField(
        "Tipo de Rota",
        max_length=30,
        choices=RouteType.choices,
        default=RouteType.OTHER
    )
    created_at = models.DateTimeField("Created At", auto_now_add=True)
    updated_at = models.DateTimeField("Updated At", auto_now=True)
    created_by = models.ForeignKey(User, verbose_name="Created By", on_delete=models.SET_NULL, null=True, blank=True, related_name="route_compositions_created")
    
    routes = models.ManyToManyField(Route, related_name="compositions", verbose_name="Routes")
    observations = models.TextField("Observations", blank=True, null=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Composição de rota"
        verbose_name_plural = "Composições de rotas"

    def __str__(self):
        return self.name

    @property
    def total_deliveries(self):
        return sum(route.stops for route in self.routes.all())

    @property
    def total_distance(self):
        return round(sum(route.distance_km for route in self.routes.all()), 2)

    @property
    def total_time(self):
        if not self.routes.exists():
            return "Sem dados"

        # Pega o maior tempo (em minutos) entre todas as rotas
        longest_time_min = max(route.time_min for route in self.routes.all())

        # Converte para segundos para formatar melhor
        total_seconds = int(longest_time_min * 60)

        # Converte para horas, minutos e segundos
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        parts = []
        if hours > 0:
            parts.append(f"{hours} hr{'s' if hours > 1 else ''}")
        if minutes > 0:
            parts.append(f"{minutes} min{'s' if minutes > 1 else ''}")
        if seconds > 0:
            parts.append(f"{seconds} seg{'s' if seconds > 1 else ''}")

        return " ".join(parts) if parts else "0 seg"

auditlog.register(RouteComposition)