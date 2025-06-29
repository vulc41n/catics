from django.urls import path
from . import views

urlpatterns = [
    path('game/', views.GameView.as_view(), name='core-game'),
    path('play/', views.PlayView.as_view(), name='core-play'),
    path('promote/', views.PromoteView.as_view(), name='core-promote'),
]
