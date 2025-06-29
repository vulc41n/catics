from django.urls import path
from django.conf import settings
from knox import views as knox_views
from . import views
from .views import tests

urlpatterns = [
    path('register-request/', views.RegisterRequestView.as_view(), name='auth-register-request'),
    path('register/', views.RegisterView.as_view(), name='auth-register'),
    path('validate/', views.ValidateView.as_view(), name='auth-validate'),
    path('login/', views.LoginView.as_view(), name='auth-login'),
    path('logout/', knox_views.LogoutView.as_view(), name='auth-logout'),
    path('logoutall/', knox_views.LogoutAllView.as_view(), name='auth-logoutall'),
    path('user/', views.GetFromUsernameView.as_view(), name='auth-get_from_username'),
]

if settings.TEST_MODE:
    urlpatterns += [
        path('am_i_logged/', tests.am_i_logged, name='auth-test-am_i_logged'),
        path('is_validated/', tests.is_validated, name='auth-test-is_validated'),
    ]
