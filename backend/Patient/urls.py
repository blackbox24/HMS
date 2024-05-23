from django.urls import path
from .views import *

urlpatterns = [
    path('', FetchAllPatient.as_view(), name="all_patient"),
    path('add/', CreatePatient.as_view(), name="add_patient"),
    path('update/<int:pk>/', UpdatePatient.as_view(), name="update_patient"),
    path('edit/<int:pk>/', FetchSinglePatient.as_view(), name="edit_patient"),
    path('remove/<int:pk>/', DeletePatient.as_view(), name="remove_patient"),
]