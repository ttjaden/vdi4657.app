from . import views

from django.urls import path, include

app_name = 'economic'
urlpatterns = [
    path('', views.economic, name='economic'),
    #path('show-json-test', views.show_json_test, name='show-json-test'),
    #path('web-rest-test', views.show_json_test, name='web-rest-test'),
    path('dashboard', views.dashboard, name='dashboard'),
    #path('dashboard', views.show_json_test, name='web-rest-test'),
]