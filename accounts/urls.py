from django.contrib.auth.views import LogoutView
from django.urls import path

from . import lockout, views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('locked/', lockout.locked, name='locked'),
    path('session-ended/', views.session_ended, name='session_ended'),
    path('password-reset/', views.password_reset_request,
         name='password_reset_request'),
    path('password-reset/sent/', views.password_reset_requested,
         name='password_reset_requested'),
    path('password-change/', views.HMSPasswordChangeView.as_view(),
         name='password_change'),
    path('password-resets/', views.password_resets, name='password_resets'),
    path('password-resets/<int:pk>/issue/', views.issue_temp_password,
         name='issue_temp_password'),
    path('password-resets/<int:pk>/handed-over/', views.mark_handed_over,
         name='mark_handed_over'),
    path('password-resets/unlock/<str:username>/', views.unlock_account,
         name='unlock_account'),
]
