from django.contrib import admin

from .models import Server, Model


@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = ("id", "plat_name", "company", "base_url", "homepage")
    search_fields = ("plat_name", "company")


@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
    list_display = ("id", "svc", "model_name", "in_token_fee", "out_token_fee", "unit", "type")
    list_filter = ("unit", "type")
    search_fields = ("model_name",)
