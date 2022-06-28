from . import views

from django.urls import path

app_name ="api"
urlpatterns = [
    path('', views.apiOverview, name='api-overview'),
    path('list-buildingProfile/', views.buildingProfileList, name='list-buildingProfile'),
    path('list-address/', views.addressList, name='list-address'),
    path('list-tos/', views.tosList, name='list-tos'),
    path('list-all/', views.allList, name='list-all'),
    path('list-all-user/<int:user_id>', views.allListUser, name='list-all-user'),
    path('res-api/', views.apiResults,name='apiResults'), 
]