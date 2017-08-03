"""events_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from events.views import *
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$',IndexPage.as_view(), name='index_page'),
    url(r'^auto_name/$', GetName.as_view(), name='get_name'),
    url(r'^get_user_data/$', GetUserData.as_view(), name='get_userData'),
    url(r'^register/$',RegisterEvent.as_view(), name='register_event'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

