"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path

from .views import autocomplete_api, save_user_search, set_geolocation, \
    get_trip_info, get_user_location_initial, get_airports_list, get_city_info

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/autocomplete_airports/', autocomplete_api, name='autocomplete_airports'),
    path('api/set_geolocation/', set_geolocation, name='set_geolocation'),
    path('api/get_trips_info/', get_trip_info, name='get_trip_info'),
    path('api/get_initial_location/', get_user_location_initial, name='get_user_location_initial'),
    # data logging
    path('api/save_search/', save_user_search, name='save_search'),
    path('api/get_airports_list/', get_airports_list, name='get_airports_list'),
    path('api/get_city_info/', get_city_info, name='get_city_info'),
]
