from django.urls import path

from . import views

urlpatterns = [
    path('opd/', views.opd_board, name='opd_board'),
    path('opd/check-in/', views.check_in, name='check_in'),
    path('encounters/<uuid:pk>/', views.encounter_detail, name='encounter_detail'),
    path('encounters/<uuid:pk>/vitals/', views.record_vitals, name='record_vitals'),
    path('encounters/<uuid:pk>/queue/', views.queue_action, name='queue_action'),
    path('encounters/<uuid:pk>/consult/', views.consult, name='consult'),
    path('encounters/<uuid:pk>/dispose/', views.dispose, name='dispose'),
    path('encounters/<uuid:pk>/note/', views.add_note, name='add_note'),
]
