import requests
import base64
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.contrib.sites.models import Site
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template

from xhtml2pdf import pisa
from events.models import *


def hotelDetails(event_obj):
    try:
        hotel_obj = BookedHotel.objects.get(registered_users=event_obj)
        event = Event.objects.filter()[0]
        data = hotel_obj.room_type.room_type + ", " + str(hotel_obj.tottal_rent) + "/-, Hotel Raviz Kollam, " + str(
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
    content = render_to_string('coupon_mail.html', cxt)
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
        'http://alerts.ebensms.com/api/v3/?method=sms&api_key=A2944970535b7c2ce38ac3593e232a4ee&to=' + phone + '&sender=QrtReg&message=' + message +' You can see your coupon at ' + url)

    return message_status


def encoded_id(user_id):
    return base64.b64encode(str(user_id))


def decode_id(user_id):
    return base64.b64decode(user_id)


def track_payment_details(data):
    print(data)
    payment_details = PaymentDetails.objects.create(**data)
    print('payment_details',data)
    return payment_details


# def render_to_pdf(template_src, context_dict={}):
#     template = get_template(template_src)
#     html = template.render(context_dict)
#     result = BytesIO()
#     pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
#     if not pdf.err:
#         return HttpResponse(result.getvalue(), content_type='application/pdf')
#     return None
