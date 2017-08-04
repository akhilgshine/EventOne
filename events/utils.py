
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import get_template
from django.core.mail import EmailMessage
from django.template import Context
from django.template.loader import render_to_string
import imgkit
from django.core.files import File
from django.contrib.sites.shortcuts import get_current_site

def get_current_url(request):
	current_site = get_current_site(request)
	domain = current_site.domain
	protocol = 'https' if request.is_secure() else 'http'
	return '%s://%s' % (protocol, domain)

def createimage(html,event_obj,request):
	try:
		imgkit.from_file(html, 'out.jpg')
	except:
		#pass imgkit exception
		pass
	file = open('out.jpg')
	image_file = File(file)
	event_obj.confirm_image = image_file
	event_obj.save()
	img_url = event_obj.confirm_image.url
	url = get_current_url(request)
	url = url + img_url
	return url

def send_email(to_email, message, event_obj):
	subject = 'QRT 85 Registration'

	# img_url = createimage('mail_template/mail_index.html', event_obj, request)

	cxt = {'obj': event_obj }
	content = render_to_string('mail_template/mail_index__.html', cxt)

	from_email = settings.DEFAULT_FROM_EMAIL
	msg = EmailMessage(subject, content, from_email, to=[to_email])
	msg.content_subtype = "html"
	msg.send(fail_silently=True)
	# send_mail(subject,message_body,from_email,[to_email], fail_silently=False)


