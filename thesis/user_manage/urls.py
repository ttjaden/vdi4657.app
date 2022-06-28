from . import views

from django.urls import path

app_name="user_manage"
urlpatterns = [
    path('login', views.loginPage, name='login'),
    path('logout', views.logoutUser, name='logout'),
    path ('register', views.registerPage, name='register'),

]