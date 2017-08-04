
from django.core.mail import send_mail
from django.conf import settings


def send_email(to_email, message, event_obj):
	to_email = 'abdul.salamtemp124@gmail.com'
	print("Sending mail...", to_email)
	subject = 'Event Register'
	event_title = " "
	date = ''
	message_body = 'You are successfully registered for the event '+event_title+' on'+str(date)+',  Thank you'
	from_email = settings.DEFAULT_FROM_EMAIL
	send_mail(subject,message_body,from_email,[to_email], fail_silently=False)