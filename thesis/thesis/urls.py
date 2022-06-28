"""thesis URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include , re_path
from django.conf.urls.i18n import i18n_patterns



urlpatterns = [
    path('admin/', admin.site.urls),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
    path('api/', include('api.urls')),
    # -> new
    path('map/', include('map.urls')),
    path('', include('technology.urls')),
    path('user/', include('user_manage.urls')),
    path('economic/', include('economic.urls')),
    re_path(r'^rosetta/', include('rosetta.urls')),

    # <-
]

urlpatterns += i18n_patterns(
    path('i18n/', include('django.conf.urls.i18n')),
)