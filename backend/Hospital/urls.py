from django.urls import path
from .views import *

urlpatterns = [
    path('', FetchAllHospital.as_view(), name="all_hospital"),
    path('add/', CreateHospital.as_view(), name="add_hospital"),
    path('update/<int:pk>/', UpdateHospital.as_view(), name="update_hospital"),
    path('edit/<int:pk>/', FetchSingleHospital.as_view(), name="edit_hospital"),
    path('remove/<int:pk>/', DeleteHospital.as_view(), name="remove_hospital"),
]