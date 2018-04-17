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
from django.conf.urls import url, include
from django.contrib import admin
from events.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', IndexPage.as_view(), name='index_page'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', logout_view, name='logout'),
    url(r'^auto_name/$', GetName.as_view(), name='get_name'),
    url(r'^get_user_data/$', GetUserData.as_view(), name='get_userData'),
    # url(r'^check_mail_phone/$',checkRegform, name='check_mail_phone'),
    url(r'^register/$', RegisterEvent.as_view(), name='register_event'),
    url(r'^users/$', ListUsers.as_view(), name='list_users'),
    url(r'^dashboard/$', DashBoardView.as_view(), name='dash_board'),
    url(r'^download-csv/$', DownloadCSVView.as_view(), name='download_csv'),
    url(r'^invoice/(?P<pk>\d+)$', InvoiceView.as_view(), name='invoice_view'),
    url(r'^register/success/(?P<pk>\d+)$', RegSuccessView.as_view(), name='invoice_views'),
    url(r'^edit_user_registered/(?P<pk>\d+)$', UserRegisterUpdate.as_view(), name='edit_user'),
    url(r'^delete_user_registered/(?P<pk>\d+)$', DeleteRegisteredUsers.as_view(), name='delete_user'),
    url(r'^update_hotel/(?P<pk>\d+)$', UpdateHotelView.as_view(), name='update_hotel_view'),
    url(r'^delete_hotel/(?P<pk>\d+)$', DeleteHotelView.as_view(), name='delete_hotel_view'),
    url(r'^update-contribute-payment/(?P<pk>\d+)$', UpdateContributionPaymentView.as_view(), name='update_contribute_payment'),
    url(r'^contribute-payment/$', AddContributionListPage.as_view(), name='add-contribution-list'),
    url(r'^update-due-payment/(?P<pk>\d+)$', DuePaymentView.as_view(), name='due_payment_update'),
    url(r'^upgrade-reg-status/(?P<pk>\d+)$', UpgradeStatusView.as_view(), name='upgrade_reg_status'),
    url(r'^add-to-registration/(?P<pk>\d+)$', AddToRegistrationView.as_view(), name='add_to_registration'),
    url(r'^edit-registration/(?P<pk>\d+)$', EditRegistrationView.as_view(), name='edit-registration'),
    url(r'^api-auth/', include('rest_framework.urls')),
    url(r'^api/', include('letsgonuts_api.urls')),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
