from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home_page_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/<int:user_id>/', views.user_profile, name='profile'),
]
