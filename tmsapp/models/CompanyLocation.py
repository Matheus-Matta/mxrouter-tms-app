from django.db import models
from django.core.exceptions import ValidationError
import requests
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from simple_history.models import HistoricalRecords
from auditlog.registry import auditlog
from django.contrib.auth.models import User
from tmsapp.action import geocode_endereco

class LocationType(models.TextChoices):
    WAREHOUSE = 'warehouse', 'Armazém'
    STORE = 'store', 'Loja'
    DISTRIBUTION_CENTER = 'distribution_center', 'Centro de Distribuição'
    HUB = 'hub', 'Hub'
    OTHER = 'other', 'Outro'

class CompanyLocation(models.Model):
    name = models.CharField("Nome", max_length=100)
    type = models.CharField(
        "Tipo de Local",
        max_length=30,
        choices=LocationType.choices,
        default=LocationType.OTHER
    )
    address = models.CharField("Endereço", max_length=255)
    city = models.CharField("Cidade", max_length=100)
    number = models.CharField("Número", max_length=10, default=0)
    neighborhood = models.CharField("Bairro", max_length=255, null=True, blank=True)
    state = models.CharField("Estado", max_length=100)
    zip_code = models.CharField("CEP", max_length=20, null=True, blank=True)
    country = models.CharField("País", max_length=100, default='Brasil')
    latitude = models.DecimalField("Latitude", max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField("Longitude", max_digits=9, decimal_places=6, null=True, blank=True)
    is_active = models.BooleanField("Ativo", default=True)
    is_principal = models.BooleanField("Principal", default=False)

    created_at = models.DateTimeField("Data de Cadastro", auto_now_add=True)
    updated_at = models.DateTimeField("Data de Atualização", auto_now=True)
    created_by = models.ForeignKey(
        User,
        verbose_name="Criado por",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="locations_created"
    )
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Local da Empresa"
        verbose_name_plural = "Locais da Empresa"

    def clean(self):
        if self.is_principal:
            other_principal = CompanyLocation.objects.filter(is_principal=True).exclude(pk=self.pk)
            if other_principal.exists():
                raise ValidationError("Já existe um local principal definido. Desmarque o atual antes de definir outro.")
                
    def full_address(self):
        parts = [
            self.address,
            self.number if self.number else '',
            self.neighborhood if self.neighborhood else '',
            self.city,
            self.state,
            self.zip_code if self.zip_code else '',
            self.country
        ]
        return ', '.join(part for part in parts if part)

    def save(self, *args, **kwargs):
        if (self.latitude is None or self.longitude is None):
            full_address = self.full_address()
            lat, lon = geocode_endereco(full_address)
            if lat and lon:
                self.latitude = lat
                self.longitude = lon
        if self.is_principal:
            # Garante que apenas um é principal
            CompanyLocation.objects.filter(is_principal=True).exclude(id=self.id).update(is_principal=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

# Registra no auditlog
auditlog.register(CompanyLocation)