from django.conf.urls import include, url
from rest_framework import routers

from .views import OtpGenerationViewSet, OtpPostViewSet, TableAndMemberTypeViewSet, RegistrationAmountType, \
    GetHotelList, RegisterViewSet

router = routers.DefaultRouter()

router.register(r'otp-generate', OtpGenerationViewSet, base_name='otp_generate')
router.register(r'otp-post', OtpPostViewSet, base_name='otp_post')
router.register(r'table-member-list', TableAndMemberTypeViewSet, base_name='table_member_list')
router.register(r'reg-amount-list', RegistrationAmountType, base_name='reg_amount_list')
router.register(r'get-hotel-list', GetHotelList, base_name='get_hotel_list')
router.register(r'register-event', RegisterViewSet, base_name='register_event')

urlpatterns = [
    url(r'^', include(router.urls)),

]
