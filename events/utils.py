from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import get_template
# from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import render_to_string
import pdfkit
from django.core.files import File

def create_pdf(event_obj):

	url = 'http://127.0.0.1:8000/invoice/'+str(event_obj.id)
	pdfkit.from_url(url, 'mail.pdf')
	file = open('mail.pdf','rb')
	return file

def send_email(to_email, message, event_obj):
	subject = 'QRT 85 Registration'

	cxt = {'event_register': event_obj }
	content = render_to_string('coupon.html', cxt)	
	from_email = settings.DEFAULT_FROM_EMAIL
	msg = EmailMultiAlternatives(subject, 'hi', from_email, to=[to_email])
	msg.attach_alternative(content, "text/html")
	msg.send()

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

