from django.urls import path
from .views import *

urlpatterns = [
    path('', FetchAllDepartment.as_view(), name="all_department"),
    path('add/', CreateDepartment.as_view(), name="add_department"),
    path('update/<int:pk>/', UpdateDepartment.as_view(), name="update_department"),
    path('edit/<int:pk>', FetchSingleDepartment.as_view(), name="edit_department"),
    path('remove/<int:pk>', DeleteDepartment.as_view(), name="remove_department"),
]