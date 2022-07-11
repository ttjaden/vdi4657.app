# -> new
from . import views
from django.urls import path


app_name = 'map'
urlpatterns = [
  path('', views.map, name='map'),  
]
