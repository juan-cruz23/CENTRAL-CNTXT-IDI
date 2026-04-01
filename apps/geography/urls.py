from django.urls import path

from apps.geography import views

app_name = "geography"

urlpatterns = [
    # Index
    path("", views.MaestrosIndexView.as_view(), name="index"),
    # Countries
    path("paises/", views.CountryListView.as_view(), name="country_list"),
    path("paises/crear/", views.CountryCreateView.as_view(), name="country_create"),
    path("paises/<int:pk>/editar/", views.CountryUpdateView.as_view(), name="country_update"),
    path("paises/<int:pk>/eliminar/", views.CountryDeleteView.as_view(), name="country_delete"),
    # Municipalities
    path("municipios/", views.MunicipalityListView.as_view(), name="municipality_list"),
    path("municipios/crear/", views.MunicipalityCreateView.as_view(), name="municipality_create"),
    path("municipios/<int:pk>/editar/", views.MunicipalityUpdateView.as_view(), name="municipality_update"),
    path("municipios/<int:pk>/eliminar/", views.MunicipalityDeleteView.as_view(), name="municipality_delete"),
    # HTMX API
    path("api/municipios/<int:country_id>/", views.municipalities_by_country, name="municipalities_by_country"),
]
