from django.db import models
from django.contrib.postgres.fields import ArrayField
from simple_history.models import HistoricalRecords
from auditlog.registry import auditlog
from django.db import models
from django.contrib.auth.models import User

COLOR_CHOICES = [
    ("orange", "Laranja"),
    ("green", "Verde"),
    ("blue", "Azul"),
    ("purple", "Roxo"),
    ("darkred", "Vermelho Escuro"),
    ("darkgreen", "Verde Escuro"),
    ("darkblue", "Azul Escuro"),
    ("cadetblue", "Azul Cadete"),
    ("lightred", "Vermelho Claro"),
    ("beige", "Bege"),
    ("lightgreen", "Verde Claro"),
    ("lightblue", "Azul Claro"),
    ("darkpurple", "Roxo Escuro"),
    ("pink", "Rosa"),
    ("gray", "Cinza"),
]

COLOR_HEX_MAP = {
    "orange": "#e37b0e",
    "green": "#0aa344",
    "blue": "#0074D9",
    "purple": "#4f2c56",
    "darkred": "#8f1c1c",
    "darkgreen": "#228B22",
    "darkblue": "#1f5775",
    "cadetblue": "#395b64",
    "lightred": "#ff7f50",
    "beige": "#ffb88c",
    "lightgreen": "#caff70",
    "lightblue": "#87cefa",
    "darkpurple": "#5d2d5d",
    "pink": "#f78fb3",
    "gray": "#808080",
}
STATUS_CHOICES = [
    ("active", "Ativo"),
    ("disabled", "Desabilitado"),
]

class RouteArea(models.Model):
    name = models.CharField(max_length=100)

    geojson = models.TextField(blank=True, null=True)
    neighborhoods = models.JSONField(blank=True, null=True, default=list)
    cities = models.JSONField(blank=True, null=True, default=list)
    cep_start = models.JSONField(blank=True, null=True, default=list)
    cep_end = models.JSONField(blank=True, null=True, default=list)
    areatotal = models.FloatField(null=True, blank=True)
    kmtotal = models.FloatField(null=True, blank=True)

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="active",
        help_text="Status da rota"
    )

    color_name = models.CharField(
        max_length=20,
        choices=COLOR_CHOICES,
        default="blue",
        help_text="Color name for map area (e.g., blue, green)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField("Updated At", auto_now=True)
    created_by = models.ForeignKey(User, verbose_name="Created By", on_delete=models.SET_NULL, null=True, blank=True, related_name="route_areas_created")

    history = HistoricalRecords()

    class Meta:
        db_table = 'route_area'
        verbose_name = "Route Area"
        verbose_name_plural = "Route Areas"

    def __str__(self):
        return self.name

    def color_hex(self):
        """Return the HEX code of the selected color."""
        return COLOR_HEX_MAP.get(self.color_name, "#0074D9")

    def cep_ranges(self):
        """Returns paired CEP ranges like [('22000','22999')]"""
        return list(zip(self.cep_start, self.cep_end))


auditlog.register(RouteArea)