from django.contrib import admin
from django.utils.html import format_html
from simple_history.admin import SimpleHistoryAdmin
from tmsapp.models import RouteArea, COLOR_HEX_MAP
from .models.CompanyLocation import CompanyLocation

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
