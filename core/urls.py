from django.urls import path

from . import views

urlpatterns = [
    path("servers/", views.server_list, name="server_list"),
    path("servers/add/", views.server_add, name="server_add"),
    path("servers/<int:pk>/", views.server_detail, name="server_detail"),
    path("models/", views.model_list, name="model_list"),
    path("models/add/", views.model_add, name="model_add"),
    path("debug/", views.debug, name="debug"),
    path("", views.server_list, name="home"),
]
