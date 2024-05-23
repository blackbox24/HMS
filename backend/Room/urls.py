from django.urls import path
from .views import *

urlpatterns = [
    path('', FetchAllRoom.as_view(), name="all_room"),
    path('add/', CreateRoom.as_view(), name="add_room"),
    path('update/<int:pk>/', UpdateRoom.as_view(), name="update_room"),
    path('edit/<int:pk>/', FetchSingleRoom.as_view(), name="edit_room"),
    path('remove/<int:pk>/', DeleteRoom.as_view(), name="remove_room"),
]