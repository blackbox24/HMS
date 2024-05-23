from django.urls import path
from .views import *

urlpatterns = [
    path('', FetchAllAppointment.as_view(), name="all_appointment"),
    path('add/', CreateAppointment.as_view(), name="add_appointment"),
    path('update/<int:pk>/', UpdateAppointment.as_view(), name="update_appointment"),
    path('edit/<int:pk>/', FetchSingleAppointment.as_view(), name="edit_appointment"),
    path('remove/<int:pk>/', DeleteAppointment.as_view(), name="remove_appointment"),
]