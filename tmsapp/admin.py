from django.contrib import admin
from django.utils.html import format_html
from simple_history.admin import SimpleHistoryAdmin
from tmsapp.models import RouteArea, COLOR_HEX_MAP
from .models.CompanyLocation import CompanyLocation
from .models.Delivery import Delivery
from .models.Route import Route, RouteDelivery
from .models.RouteComposition import RouteComposition


@admin.register(CompanyLocation)
class CompanyLocationAdmin(SimpleHistoryAdmin):
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

@admin.register(Delivery)
class DeliveryAdmin(SimpleHistoryAdmin):
    list_display = (
        "customer_name", "order_number", "street", "route_name", "number", "neighborhood", "city",
        "state", "latitude", "longitude", "phone", "cpf", "observation", "reference", "address",
        "postal_code", "is_check", "created_at", "updated_at", "created_by", "history"
    )
    list_filter = ("route_name", "city", "is_check", "created_at", "updated_at")
    search_fields = (
        "customer_name", "order_number", "street", "route_name", "number", "neighborhood",
        "latitude", "longitude", "phone", "cpf", "is_check", "created_at", "updated_at", "created_by", "history"
    )
    list_editable = (
        "route_name",
    )

    fields = (
        "customer_name", "order_number", "street", "route_name", "number", "neighborhood", "city",
        "state", "latitude", "longitude", "phone", "cpf", "observation", "reference", "address",
        "postal_code", "is_check", "created_at", "updated_at", "created_by"
    )

@admin.register(Route)
class RouteAdmin(SimpleHistoryAdmin):

    list_display = (
        "id", "name", "created_at", "updated_at", "created_by", "stops", "distance_km", "time_min"
    )
    list_filter = (
        "name", "stops"
    )
    search_fields = (
        "name", "deliveries"
    )
    list_editable = (
        "name",
    )
    fields = (
        "color", "name", "created_by", "stops", "distance_km", "time_min", "geojson", "points"
    )
    history_list_display = (
        "color", "created_at", "history"
        )

@admin.register(RouteDelivery)
class RouteDeliveryAdmin(SimpleHistoryAdmin):

    list_display = (
        "id", "route", "delivery", "position", "updated_at"
    )
    list_filter = (
    )
    search_fields = (
        "id", "delivery"
    )
    list_editable = (
    )

    fields = (
        
    )

@admin.register(RouteArea)
class RouteAreaAdmin(SimpleHistoryAdmin):
    list_display = ("name", "color_display", "city_count", "neighborhood_count", "created_at", "updated_at")
    search_fields = ("name", "cities", "neighborhoods")
    list_filter = ("color_name", "created_at")
    readonly_fields = ("created_at", "color_preview", "geojson")
    history_list_display = ["color_name", "created_at", "history_user"]

    fieldsets = (
        (None, {
            "fields": ("name", "color_name", "color_preview")
        }),
        ("Geographic Data", {
            "fields": ("geojson", "cities", "neighborhoods", "cep_start", "cep_end")
        }),
        ("Metadata", {
            "fields": ("created_at",)
        }),
    )

    def color_display(self, obj):
        return obj.get_color_name_display()
    color_display.short_description = "Color"

    def city_count(self, obj):
        return len(obj.cities)
    city_count.short_description = "Cities"

    def neighborhood_count(self, obj):
        return len(obj.neighborhoods)
    neighborhood_count.short_description = "Neighborhoods"

    def color_preview(self, obj):
        hex_color = obj.cor_hex()  # ou obj.color_hex(), depende do nome do método
        return format_html(
            '<div style="width: 40px; height: 20px; background-color: {}; border: 1px solid #ccc;"></div>',
            hex_color
        )
    color_preview.short_description = "Preview"

@admin.register(RouteComposition)
class RouteCompositionAdmin(SimpleHistoryAdmin):
    list_display = (
        "name", "type", "created_at", "updated_at", "created_by", "observations"
    )
    search_fields = (
        "name", "type", "observations"
    )
    list_filter = (
        "created_by",
    )
    readonly_fields = (
        "created_at", "updated_at", "created_by"
    )
    history_list_display = [

    ]