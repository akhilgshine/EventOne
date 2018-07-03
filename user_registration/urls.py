from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from .views import UserSignupView, OtpPostView, SetPassWordView, UserLoginView, UserTableRegistrationView, \
    ProfileRegistrationView, AjaxHotelRentCalculation, HotelRegistrationView, PaymentRegistrationView, \
    CouponSuccessView, UserProfileView, ResetPassword

urlpatterns = [
    url(r'^user_signup/', UserSignupView.as_view(), name='user_signup'),
    url(r'^otp-post/', OtpPostView.as_view(), name='otp_post'),
    url(r'^set-password/', SetPassWordView.as_view(), name='set_password'),
    url(r'^user-login/', UserLoginView.as_view(), name='user_login'),
    url(r'^event-register/', UserTableRegistrationView.as_view(), name='event_register'),
    url(r'^profile-register/', ProfileRegistrationView.as_view(), name='profile_register'),
    url(r'^hotel-rent/', AjaxHotelRentCalculation.as_view(), name='hotel_rent'),
    url(r'^hotel-booking/', HotelRegistrationView.as_view(), name='hotel_booking'),
    url(r'^payment-registration/', PaymentRegistrationView.as_view(), name='payment_registration'),
    url(r'^coupon-success/', CouponSuccessView.as_view(), name='coupon_success'),
    url(r'^user-profile/', UserProfileView.as_view(), name='user_profile'),
    url(r'^reset-password/', ResetPassword.as_view(), name='reset_password'),
    url(r'^contact-us/', TemplateView.as_view(template_name='user_registration/contact-us.html'), name='contact_us'),
    url(r'^hotel-list/', TemplateView.as_view(template_name='user_registration/hotel_list.html'), name='hotel_list'),

]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
