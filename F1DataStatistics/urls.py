from django.urls import path
from django.contrib import admin
from main import views
"""F1DataStatistics URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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

urlpatterns = [
    path('', views.inicio),
    path('admin/', admin.site.urls), 
    path('cargar_base_datos/', views.cargar_bd),
    path('ingresar/', views.ingresar),
    path('nuevo_usuario/', views.usuario_nuevo),
    path ('cerrar/', views.cerrar),
    path ('pilotos/', views.lista_pilotos),
    path ('constructores/', views.lista_constructores),
    path('busqueda_nacionalidad/', views.buscar_por_nacionalidad),
    path('busqueda_anyo/', views.buscar_por_anyo)
]
