from django.urls import path
from apps.calendar_sync import views

app_name = "calendar_sync"

urlpatterns = [
    path("", views.CalendarDashboardView.as_view(), name="dashboard"),
    path("eventos/", views.CalendarEventListView.as_view(), name="event_list"),
    path("eventos/<int:pk>/asignar/", views.AssignEventToProjectView.as_view(), name="assign_event"),
    path("palabras-clave/crear/", views.KeywordMappingCreateView.as_view(), name="keyword_create"),
    path("palabras-clave/<int:pk>/eliminar/", views.KeywordMappingDeleteView.as_view(), name="keyword_delete"),
]
