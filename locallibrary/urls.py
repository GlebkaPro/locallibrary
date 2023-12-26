"""locallibrary URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include

urlpatterns = [
  path('admin/', admin.site.urls),
]

urlpatterns += [
  path('catalog/', include('catalog.urls')),
]

# Use static() to add url mapping to serve static files during development (only)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Добавьте URL-карты, чтобы перенаправить базовый URL-адрес на наше приложение
from django.views.generic import RedirectView

urlpatterns += [
  path('', RedirectView.as_view(url='/catalog/', permanent=True)),
]

# Добавьте URL-адреса аутентификации сайта Django (для входа в систему, выхода из системы, управления паролями)
urlpatterns += [
  path('accounts/', include('django.contrib.auth.urls')),
]
if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
