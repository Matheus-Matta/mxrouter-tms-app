from django.contrib import admin
from .models.CompanyLocation import CompanyLocation

@admin.register(CompanyLocation)
class CompanyLocationAdmin(admin.ModelAdmin):
    list_display = (
        "name", "type", "city", "state", "neighborhood", "number",
        "is_principal", "is_active"
    )
    list_filter = ("type", "is_active", "is_principal", "state")
    search_fields = ("name", "address", "city", "zip_code", "neighborhood")
    list_editable = ("is_active", "is_principal")

    fields = (
        "name", "type", "address", "number", "neighborhood", "city", "state",
        "zip_code", "country", "latitude", "longitude", "is_principal", "is_active"
    )