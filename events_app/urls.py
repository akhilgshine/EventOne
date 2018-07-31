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
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from events.views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', IndexPage.as_view(), name='index_page'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    
    # Hotel
    url(r'^hotel/login/$', RestaurantLoginView.as_view(), name='restaurant_login'),
    url(r'^hotel/registered-users/$', ListRegisteredUsers.as_view(), name='registered_user_list'),
    # Set Room No
    url(r'^hotel/add-room-no/(?P<pk>\d+)$', HotelAddRoomNo.as_view(), name='hotel_add_room_no'),
    
    url(r'^logout/$', logout_view, name='logout'),
    url(r'^auto_name/$', GetName.as_view(), name='get_name'),
    url(r'^get_user_data/$', GetUserData.as_view(), name='get_userData'),
    # url(r'^check_mail_phone/$',checkRegform, name='check_mail_phone'),
    url(r'^register/$', RegisterEvent.as_view(), name='register_event'),
    url(r'^users/$', ListUsers.as_view(), name='list_users'),
    url(r'^dashboard/$', DashBoardView.as_view(), name='dash_board'),
    # url(r'^download-csv/$', DownloadCSVView.as_view(), name='download_csv'),
    url(r'^invoice/(?P<pk>.*)$', InvoiceView.as_view(), name='invoice_view'),
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
    url(r'^approve-registration/(?P<pk>\d+)$', ApproveRegistrationView.as_view(), name='approve-registration'),
    url(r'^hotel-due-payment/(?P<pk>\d+)$', UpdateHotelDue.as_view(), name='hotel_due_payment'),
    url(r'^get-hotel-calculation/', get_total_hotel_rent_calculation, name='get-hotel-calculation'),
    url(r'^un-registered_users/', GetNotRegisteredUsers.as_view(), name='un_registered_users'),
    url(r'^un-registered_users-csv/', DownloadUnRegisteredUserCSVView.as_view(), name='un_registered_users_csv'),
    url(r'^proxy-hotel/', ProxyHotelBookingView.as_view(), name='proxy-hotel'),
    url(r'^proxy-listing/', ProxyHotelListingView.as_view(), name='proxy-listing'),
    url(r'^user-registration-list/', UserRegistrationListView.as_view(), name='user_registration_list'),
    url(r'^get-hotel-booking-details/', GetHotelBookingDetailsView.as_view(), name='get_hotel_booking_details'),
    url(r'^t-shirt-update/(?P<pk>\d+)$', AddTShirtView.as_view(), name='t_shirt_update'),

    # Set Room No
    url(r'^add-room-no/(?P<pk>\d+)$', AddRoomNo.as_view(), name='add_room_no'),

    url(r'^list-of-attendees/', ListOfAttendees.as_view(), name='list_of_attendees'),
    url(r'^adding-of-event-attendees/', AjaxAttendeesAddingView.as_view(), name='adding_of_event_attendees'),
    url(r'^get-user-data-json/', UserListJson.as_view(), name='get_user_data_json'),
    url(r'^increment-decrement-ajax/', IncrementDecrementAmountAjaxView.as_view(), name='increment_decrement_ajax'),
    url(r'^friday-coupon-booking/', FridayDinnerBookingView.as_view(), name='friday_coupon_booking'),
    url(r'^api-auth/', include('rest_framework.urls')),
    url(r'^api/', include('letsgonuts_api.urls')),
    url(r'^user/', include('user_registration.urls')),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
