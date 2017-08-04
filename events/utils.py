
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import get_template
from django.core.mail import EmailMessage
from django.template import Context
from django.template.loader import render_to_string

def send_email(to_email, message, event_obj):
	subject = 'QRT 85 Registration'
	cxt = {'obj': event_obj }
	content = render_to_string('mail_template/mail_index.html', cxt)

	from_email = settings.DEFAULT_FROM_EMAIL
	msg = EmailMessage(subject, content, from_email, to=[to_email])
	msg.content_subtype = "html"
	msg.send(fail_silently=True)
	# send_mail(subject,message_body,from_email,[to_email], fail_silently=False)
