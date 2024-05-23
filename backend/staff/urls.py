from django.urls import path
from .views import *

urlpatterns = [
    path('', FetchAllStaff.as_view(), name="all_staff"),
    path('add/', CreateStaff.as_view(), name="add_staff"),
    path('update/<int:pk>/', UpdateStaff.as_view(), name="update_staff"),
    path('edit/<int:pk>/', FetchSingleStaff.as_view(), name="edit_staff"),
    path('remove/<int:pk>/', DeleteStaff.as_view(), name="remove_staff"),
]