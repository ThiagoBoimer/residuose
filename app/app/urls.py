"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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

from home import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('logout/', views.user_logout, name='logout'),
    path('home/', views.user_home, name='home'),
    path('localizador_residuo/', views.localizador_residuo, name='localizador_residuo'),
    path('get_capitulos/', views.get_capitulos, name='get_capitulos'),
    path('get_subcapitulos/', views.get_subcapitulos, name='get_subcapitulos'),
    path('get_codigos/', views.get_codigos, name='get_codigos'),
    path('get_municipios/', views.get_municipios, name='get_municipios'),
    path('match/', views.match, name='match'),
    path('get_popup_content/', views.get_popup_content, name='get_popup_content'),
    path('mapa-geracao-sc/', views.get_mapa_residuos, name='get_mapa_residuos')
]
