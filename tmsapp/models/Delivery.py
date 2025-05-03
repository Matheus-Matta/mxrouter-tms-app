from django.db import models
from simple_history.models import HistoricalRecords
from auditlog.registry import auditlog
from django.contrib.auth.models import User

class Delivery(models.Model):
    customer_name = models.CharField("Nome do Cliente", max_length=255)
    order_number = models.CharField("Número do Pedido", max_length=50)
    street = models.CharField("Rua", max_length=255)
    route_name = models.CharField("Rota", max_length=255, null=True, blank=True)
    number = models.CharField("Número", max_length=20)
    neighborhood = models.CharField("Bairro", max_length=100)
    city = models.CharField("Município", max_length=100)
    state = models.CharField("Estado", max_length=50)
    latitude = models.DecimalField("Latitude", max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField("Longitude", max_digits=9, decimal_places=6, null=True, blank=True)
    phone = models.CharField("Telefone", max_length=20, null=True, blank=True)
    cpf = models.CharField("CPF", max_length=20, null=True, blank=True)
    observation = models.TextField("Observação", null=True, blank=True)
    reference = models.CharField("Ponto de Referência", max_length=255, null=True, blank=True)
    address = models.CharField("Endereço", max_length=255, null=True, blank=True)
    postal_code = models.CharField("CEP", max_length=20, null=True, blank=True)


    created_at = models.DateTimeField("Data de Cadastro", auto_now_add=True)
    updated_at = models.DateTimeField("Data de Atualização", auto_now=True)
    created_by = models.ForeignKey(
        User,
        verbose_name="Criado por",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deliveries_created"
    )
    history = HistoricalRecords()
    @property
    def full_address(self):
        parts = [
            self.address,
            self.number,
            self.neighborhood,
            self.city,
            self.state,
            self.postal_code,
            "Brasil"
        ]
        return ', '.join(filter(None, parts))

    def save(self, *args, **kwargs):
        if (self.latitude is None or self.longitude is None):
            full_address = self.full_address()
            lat, lon = geocode_endereco(full_address)
            if lat and lon:
                self.latitude = lat
                self.longitude = lon
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Entrega"
        verbose_name_plural = "Entregas"

    def __str__(self):
        return f"{self.customer_name} - Pedido {self.order_number}"

# Registra no auditlog
auditlog.register(Delivery)