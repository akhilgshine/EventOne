from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import get_template
from django.core.mail import EmailMessage
from django.template import Context
from django.template.loader import render_to_string
import pdfkit
from django.core.files import File


def create_pdf(event_obj):	
	url = 'http://127.0.0.1:8000/invoice/'+str(event_obj.id)
	# pdfkit.from_url(url, 'mail_data/'+str(event_obj.qrcode)+'.pdf')
	pdfkit.from_url(url, 'mail.pdf')
	# file = open('mail_data/'+str(event_obj.qrcode)+'.pdf')
	file = open('mail.pdf')
	pdf_file = File(file)
	return pdf_file

def send_email(to_email, message, event_obj,url):
	subject = 'QRT 85 Registration'

	pdf_file = create_pdf(event_obj)

	to_email = 'salam104104@gmail.com'

	cxt = {'obj': event_obj }

	content = render_to_string('mail_template/mail_index.html', cxt)
	from_email = settings.DEFAULT_FROM_EMAIL
	msg = EmailMessage(subject, content, from_email, to=[to_email])
	msg.content_subtype = "application/pdf"
	msg.attach(pdf_file.name, 'r')
	# msg.attach('mail.pdf', pdf_file, 'application/pdf')
	msg.send()
	# fail_silently=True
	# send_mail(subject,message_body,from_email,[to_email], fail_silently=False)