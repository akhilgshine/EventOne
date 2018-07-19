import base64

import requests
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string

from events.models import BookedHotel, Event, OtpModel, PaymentDetails


def hotelDetails(event_obj):
    try:
        hotel_obj = BookedHotel.objects.get(registered_users=event_obj)
        event = Event.objects.filter()[0]
        data = hotel_obj.room_type.room_type + ", " + str(
            hotel_obj.tottal_rent) + "/-, " + hotel_obj.hotel.name + " " + "" + str(
            hotel_obj.checkin_date.strftime("%B %d, %Y")) + " to " + str(hotel_obj.checkout_date.strftime("%B %d, %Y"))
    # if hotel_obj.book_friday:
    # 	data = hotel_obj.room_type.room_type+", "+str(hotel_obj.tottal_rent)+"/-, Hotel Raviz Kollam, "+str(hotel_obj.checkin_date)+" to "++str(hotel_obj.checkout_date)
    # else:
    # 	data = hotel_obj.room_type.room_type+", "+str(hotel_obj.tottal_rent)+"/-, Hotel Raviz Kollam, 4th Aug 2018 to 5th Aug 2018 (one night)."
    except:
        data = ''
    return data


def send_email(to_email, message, event_obj):
    cxt = {'event_register': event_obj}
    cxt['hotel'] = hotelDetails(event_obj)

    # if event_obj.amount_paid < 5000:
    # 	cxt['partial'] = 'Partial'

    subject = 'QRT 85 Registration'
    content = render_to_string('coupon_second.html', cxt)
    from_email = settings.DEFAULT_FROM_EMAIL

    msg = EmailMultiAlternatives(subject, 'Hi', from_email, to=[to_email, 'registration@letsgonuts2018.com'])
    msg.attach_alternative(content, "text/html")
    msg.send()

    print("mail --> ", to_email)


def set_status(event_reg):
    amount_paid = int(event_reg.amount_paid)
    if amount_paid >= 6000:
        event_reg.event_status = 'Couple'
        event_reg.save()
    elif amount_paid >= 5000:
        event_reg.event_status = 'Stag'
        event_reg.save()
    else:
        event_reg.event_status = 'Not Mentioned'
        event_reg.save()


# send sms to user
def send_sms_message(phone, message, user_id):
    domain = Site.objects.get_current().domain
    url = domain + str(reverse_lazy('invoice_view', kwargs={'pk': encoded_id(user_id)}))
    message_status = requests.get(
        "http://unifiedbuzz.com/api/insms/format/json/?mobile=" + phone + "&text=" + message +
        '. You can see your coupon at ' + url + "&flash=0&type=1&sender=QrtReg",
        headers={"X-API-Key": "918e0674e62e01ec16ddba9a0cea447b"})
    return message_status


def encoded_id(user_id):
    return base64.b64encode(str(user_id))


def decode_id(user_id):
    return base64.b64decode(user_id)


def track_payment_details(data):
    print(data)
    payment_details = PaymentDetails.objects.create(**data)
    print('payment_details', data)
    return payment_details


# send otp message to mobile
def send_otp(obj):
    otp_number = get_random_string(length=6, allowed_chars='1234567890')
    OtpModel.objects.create(mobile=obj.mobile, otp=otp_number)
    message = "OTP for Letsgonuts login is %s" % (otp_number,)
    message_status = requests.get(
        "http://unifiedbuzz.com/api/insms/format/json/?mobile=" + obj.mobile + "&text=" + message +
        "&flash=0&type=1&sender=QrtReg",
        headers={"X-API-Key": "918e0674e62e01ec16ddba9a0cea447b"})
