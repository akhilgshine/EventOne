from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import get_template
# from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import render_to_string
import pdfkit
from django.core.files import File
from events.models import *

def hotelDetails(event_obj):
	try:
		hotel_obj = Hotels.objects.get(registered_users=event_obj)
		if hotel_obj.book_friday:
			data = hotel_obj.room_type.room_type+","+" (2018.08.03 & 2018.08.04)"
		else:
			data = hotel_obj.room_type.room_type+","+" (2018.08.04)"
	except:
		data = ''
	return data

def send_email(to_email, message, event_obj):
	cxt = {'event_register': event_obj }
	cxt['hotel'] = hotelDetails(event_obj)
	subject = 'QRT 85 Registration'	
	content = render_to_string('coupon_mail.html', cxt)	
	from_email = settings.DEFAULT_FROM_EMAIL
	msg = EmailMultiAlternatives(subject, 'hi', from_email, to=[to_email])
	msg.attach_alternative(content, "text/html")
	msg.send()
	print("mail --> ",to_email)

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

