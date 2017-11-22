# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import FormView, TemplateView, View,UpdateView
from django.core.urlresolvers import reverse
from django.contrib import messages
from events.models import *
# Create your views here.
import json
from events.forms import *
from events.models import *
from events.utils import send_email, set_status, hotelDetails
from django.contrib.auth import authenticate, login
import requests
from django.contrib.auth import logout
import re

class IndexPage(TemplateView):

	template_name = 'index.html'
	def get_context_data(self, **kwargs):

		context = super(IndexPage, self).get_context_data(**kwargs)

		context['events'] = Event.objects.filter()[:1]
		context['tables'] = Table.objects.all()
		return context

"""
    Login View
    """
class LoginView(View):
    template_name = "login.html"
    
    def get(self, request, *args, **kwargs):
        form = LoginForm()
        return render(request, self.template_name, {'form':form})

    # def authenticate_user(self, username=None, password=None):
        
    #     if '@' in username:
    #         kwargs = {'email': username}
    #     else:
    #         kwargs = {'username': username}
    #     try:
    #         user = CustomUser.objects.get(**kwargs)
    #         if user.check_password(password):
    #             return user
    #     except:
    #         return None

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)

            if user is not None:
            	try:
	            	if user.is_active:
	            		login(request, user)	
	            		return HttpResponseRedirect(reverse('register_event'))
            	except:
            		return render(self.request,self.template_name,{'form':form})
            else:
            	return render(self.request,self.template_name,{'form':form})

class RegisterEvent(TemplateView):	
	template_name = 'register.html'
	
	def get(self, request, *args, **kwargs):
		context = {}
		if not request.user.is_authenticated():
			return HttpResponseRedirect(reverse('login'))

		context['form'] = EventRegisterForm()
		context['room_types'] = RoomType.objects.all()
		context['tables'] = Table.objects.all() #.order_by('table_order')
		return render(request, self.template_name, context)

	def check_balance(self, amount):

		balance_amount = 0
		if int(amount) < 5000:
			balance_amount = 5000 - int(amount)
			if balance_amount > 0:
				return balance_amount
		return 0

	def post(self, request, *args, **kwargs):
		context = {}
		message = ''
		try:
			name = request.POST.get('first_name', '')
			last_name = request.POST.get('last_name', '')
			email = request.POST.get('email', '')
			phone = request.POST.get('phone', '')
			table = request.POST.get('table_val', '')

			payment = request.POST.get('payment', '')
			amount_paid = request.POST.get('amount_paid', 0)

			hotel_name = request.POST.get('hotel_name','')
			room_rent = request.POST.get('room_rent','')
			room_type = request.POST.get('room_type','')
			book_friday = request.POST.get('book_friday','')
			if book_friday:
				book_friday = True
				text = " for two days"
			else:
				book_friday = False
				text =" for a day"

			event = Event.objects.filter()[0]			
			try:				
				new_table = request.POST.get('other_table', '')				
				if not new_table:
					new_table = request.POST.get('table_val', '')
			except:
				new_table = ''

			if new_table:
				table, created = Table.objects.get_or_create(table_name=new_table,
					event=event)
				if created:
					try:
						table_order = int(re.search(r'\d+', new_table).group())
						table.table_order = table_order
						table.save()
					except:
						table.table_order = ''
						table.save()
			else:
				table = Table.objects.get(table_name=table)

			event_user, created = EventUsers.objects.get_or_create(table=table,
				email=email)

			if created:
				event_user.first_name = name
				event_user.last_name = last_name
				event_user.mobile = phone
				event_user.save()
			try:
				event_reg, created = RegisteredUsers.objects.get_or_create(event_user=event_user,
					event=event,
					table= table)

				if created:
					try:
						qrcode =  RegisteredUsers.objects.latest('qrcode').qrcode
						if not qrcode.split('QRT')[1].startswith('8'):
							qrcode = 'QRT8001'
						else:
							qrcode_updated = qrcode[-3:]
							qrcode_updated_increment = int(qrcode_updated) + 1
							qrcode_updated_length = len(str(qrcode_updated_increment))
							if qrcode_updated_length == 1:
								qrcode = str('QRT8') + '00' + str(qrcode_updated_increment)
							if qrcode_updated_length == 2:
								qrcode = str('QRT8') + '0' + str(qrcode_updated_increment)
					except:
						qrcode = 'QRT8001'

					print("amount_paid : ", amount_paid)
					balance_amount = self.check_balance(amount_paid)

					event_reg.payment = payment
					event_reg.amount_paid = amount_paid
					event_reg.balance_amount = balance_amount
					event_reg.qrcode = qrcode
					event_reg.save()

				else:					
					last_pay = event_reg.amount_paid
					if not last_pay:
						last_pay = 0
					tottal_paid = int(last_pay) + int(amount_paid)

					balance_amount = self.check_balance(tottal_paid)
					event_reg.payment = payment
					event_reg.amount_paid = tottal_paid
					event_reg.balance_amount = balance_amount
					event_reg.save()
				
				if amount_paid :
					PaymentDetails.objects.create(reg_event=event_reg,
						amount = amount_paid
						)
				if room_type:
					room = RoomType.objects.get(id=room_type)
					hotel, created = Hotels.objects.get_or_create(registered_users=event_reg)
					hotel.hotel_name = hotel_name
					hotel.tottal_rent = room_rent
					hotel.book_friday = book_friday
					hotel.room_type = room
					hotel.save()
					room.rooms_available = room.rooms_available - 1
					room.save()
					message_hotel = "You have successfully booked room in Raviz Restaurant for the event, Area 1 Agm of Round Table India hosted by QRT85 'Lets Go Nuts'. You have choosen : '"+room.room_type+"'"
					message_hotel += text+ " And your tottal rent is Rs."+str(room_rent)+"/-"


			except Exception as e:

				if created and event_reg:
					event_reg.delete()				
				event_reg = None

			if event_reg:
				set_status(event_reg)
				message = "You are successfully registered for the event, Area 1 Agm of Round Table India hosted by QRT85 'Lets Go Nuts'. Your registration ID is : "+event_reg.qrcode+ " And you have paid Rs."+str(event_reg.amount_paid)+"/-"				
				message_status = requests.get('http://alerts.ebensms.com/api/v3/?method=sms&api_key=A2944970535b7c2ce38ac3593e232a4ee&to='+phone+'&sender=QrtReg&message='+message)
				try:
					send_email(email,message,event_reg)
				except:
					pass
				context['event_register'] = event_reg
				context['payment_details'] = PaymentDetails.objects.filter(reg_event=event_reg)
				return HttpResponseRedirect("/register/success/"+str(event_reg.id))
				# return render(request, 'invoice.html', context)
			else:
				message = "There is an issue with your registration. Please try again"
				
		except:
			message = "There is an issue with your registration. Please try again."
			messages.success(self.request, message)
			return HttpResponseRedirect(reverse('register_event'))

class RegSuccessView(TemplateView):
	# template_name = 'invoice.html'
	# template_name = 'coupon_mail.html'
	template_name = 'invoice.html'
	def get(self, request, *args, **kwargs):
		context = {}
		pk = kwargs.pop('pk')
		event_reg = RegisteredUsers.objects.get(id=pk)
		context['hotel'] = hotelDetails(event_reg)
		context['event_register'] = event_reg
		context['payment_details'] = PaymentDetails.objects.filter(reg_event=event_reg)
		return render(request, self.template_name, context)

class GetName(TemplateView):

	def get(self, request, *args, **kwargs):
		if request.is_ajax():
			results = []
			q = request.GET.get('term', '')
			table_name = request.GET.get('table', '')
			table = Table.objects.get(table_name=table_name)

			users = EventUsers.objects.filter(table = table)

			users = users.filter(first_name__icontains=q)

			for user in users:
				user_json = {}
				user_json['id'] = user.id
				user_json['label'] = user.first_name+ ' ' +user.last_name
				user_json['value'] = user.first_name+ ' ' +user.last_name
				results.append(user_json)

			data = json.dumps(results)

			mimetype = 'application/json'	

			return HttpResponse(data , mimetype)

# def checkRegform(request):

# 	data  = {}
# 	if request.is_ajax():
# 		email = request.GET.get('email', '')

# 		users = RegisteredUsers.objects.filter(event_user__email=email)

# 		if len(users) > 0:
# 			data['success'] = "True"			
# 		else:
# 			data['message'] = "Email already exists. Please enter new mail !."
# 			data['success'] = "False"

# 		return HttpResponse(json.dumps(data), content_type='application/json')
# 	else:
# 		data['success'] = "False"	
# 	return HttpResponse(json.dumps(data), content_type='application/json')



class GetUserData(TemplateView):

    def get(self, request):
    	data = {}
    	django_messages = []
    	data['user_exist'] = ''
    	try:
    		username = request.GET['username']
    		selected_table = request.GET.get('selected_table', '')
    		new_table = request.GET.get('new_table', '')

    		if new_table:
    			table_other, created = Table.objects.create(table_name=new_table)
    			# data['other_table'] = 'Other'
    			data['success'] = "True"
    			return HttpResponse(json.dumps(data), content_type='application/json')

    		elif selected_table == 'Other':
    			tables = Table.objects.filter(table_name='Other')
    			if len(tables) == 1:
    				table = tables[0]
    		else:
    			table = Table.objects.get(table_name=selected_table)

    		name_list = username.split(' ', 1)
    		user = EventUsers.objects.get(first_name=name_list[0],last_name=name_list[1] )
    		# user = EventUsers.objects.get(first_name=username, table=table)

    		
    		# Checks user exist
    		try:
    			registered_user = RegisteredUsers.objects.get(event_user=user ,table=table)
    			# data['balance'] = int(registered_user.balance_amount)
    			hotel_obj = Hotels.objects.get(registered_users=registered_user)
    			data['paid_amount'] = registered_user.amount_paid
    			data['payment_type'] = registered_user.payment
    			data['user_exist'] = 'true'
    			data['hotel_name'] = hotel_obj.hotel_name
    			data['hotel_room_number'] = hotel_obj.room_number
    			data['hotel_type'] = hotel_obj.room_type
    			print("TYPE : "+ str(hotel_obj.room_type))
    			print("User exist")
    		except:
    			print("user not exist")
    			data['user_exist'] = 'false'
    			data['other_table'] = ''    		
    		data['email'] = user.email
    		data['mobile'] = user.mobile
    		data['first_name'] = user.first_name
    		data['last_name'] = user.last_name    		
    		data['success'] = "True"
    		print("Data : ", data)

    		return HttpResponse(json.dumps(data), content_type='application/json')
    	except:
    		print("except from GetUserData")
    		data['success'] = "False"
    		data['error_msg'] = "something went WRONG"
    		return HttpResponse(json.dumps(data), content_type='application/json')

    	return HttpResponse(json.dumps(data), content_type='application/json')

def logout_view(request):
	logout(request)
	return HttpResponseRedirect('/')

class ListUsers(TemplateView):
	template_name = 'user_list.html'

	def get(self, request, *args, **kwargs):
		context ={}
		registered_users = RegisteredUsers.objects.all()
		hotels = []
		for user in registered_users :
			try:
				hotels.append(user.hotel.all().first())
			except:
				hotels.append('Not Booked')
		print(hotels)
		context['hotels'] = hotels
		context['users'] = registered_users
		# user_list = []
		# for user in registered_users:
		# 	data = {}
		# 	data['name'] = user.event_user.first_name+' '+user.event_user.last_name
		# 	user_list.append(data)
		return render(request, self.template_name, context)

class InvoiceView(TemplateView):
	# template_name = 'invoice.html'
	# template_name = 'coupon_mail.html'
	template_name = 'coupon.html'
	def get(self, request, *args, **kwargs):
		context = {}
		pk = kwargs.pop('pk')
		event_reg = RegisteredUsers.objects.get(id=pk)
		context['hotel'] = hotelDetails(event_reg)
		context['event_register'] = event_reg
		context['payment_details'] = PaymentDetails.objects.filter(reg_event=event_reg)
		return render(request, self.template_name, context)

class UserRegisterUpdate(TemplateView):
	template_name = 'register.html'

	def get(self,request, *args,**kwargs):
		context={}
		pk = kwargs.pop('pk')
		event_registered_user = RegisteredUsers.objects.get(id=pk)
		try:
			hotel_obj = Hotels.objects.get(registered_users=event_registered_user)
		except:
			hotel_obj = None

		context['room_types'] = RoomType.objects.all()
		context['event_registered_user'] = event_registered_user
		context['hotel_obj'] = hotel_obj
		return render(request, self.template_name, context)

	def post(self,request,*args,**kwargs):
		try:
			room_updates = False
			message_hotel = ''
			name = request.POST.get('first_name', '')
			last_name = request.POST.get('last_name', '')
			email = request.POST.get('email', '')
			phone = request.POST.get('phone', '')
			# table = request.POST.get('table_val', '')
			update_id = request.POST.get('update_id', '')

			payment = request.POST.get('payment', '')
			amount_paid = request.POST.get('amount_paid', '')
			room_type = request.POST.get('room_type','')
			hotel_name = request.POST.get('hotel_name', '')
			room_rent = request.POST.get('room_rent','')
			book_friday = request.POST.get('book_friday', '')
			
			if book_friday:
				book_friday = True
				text = " for two days"
			else:
				text = " for a day"
				book_friday = False

			reg_user_obj  = RegisteredUsers.objects.get(id=update_id)

			user = EventUsers.objects.get(id=reg_user_obj.event_user.id)

			if amount_paid :
				PaymentDetails.objects.create(reg_event=reg_user_obj,
					amount = amount_paid)		
			try:
				room = RoomType.objects.get(id=room_type)
				hotel_obj, created = Hotels.objects.get_or_create(registered_users=reg_user_obj)
				if created:
					hotel_obj.hotel_name = hotel_name
					# hotel_obj.room_number = hotel_room_number	
					hotel_obj.tottal_rent = int(room_rent)
					hotel_obj.book_friday = book_friday
					hotel_obj.room_type = room
					hotel_obj.save()
					room.rooms_available = room.rooms_available - 1
					room.save()
					room_updates = True
					message_hotel = "You have successfully booked room in Raviz Restaurant for the event, Area 1 Agm of Round Table India hosted by QRT85 'Lets Go Nuts'. You have choosen : '"+room.room_type+"'"
					message_hotel = text+ " And your tottal rent is Rs."+str(room_rent)+"/-"
				else :
					hotel_obj.hotel_name = hotel_name
					# hotel_obj.room_number = hotel_room_number
					hotel_obj.tottal_rent = room_rent		
					hotel_obj.book_friday = book_friday
					if not hotel_obj.room_type == room:
						room_type_obj = hotel_obj.room_type
						room_type_obj.rooms_available = room_type_obj.rooms_available + 1
						
						room_type_obj.save()
						room.rooms_available = room.rooms_available - 1
						room.save()
						hotel_obj.room_type = room
						room_updates = True
						message_hotel = "You have successfully updated room in Raviz Restaurant for the event, Area 1 Agm of Round Table India hosted by QRT85 'Lets Go Nuts'. You have choosen : '"+room.room_type+"'"
						message_hotel += text+ " And your tottal rent is Rs."+str(room_rent)+"/-"
					hotel_obj.save()
			except:
				hotel_obj = None
			if name:
				user.first_name = name
			if last_name:
				user.last_name = last_name
			if email:
				user.email = email
			if phone:
				user.phone = phone
			user.save()
			if amount_paid:
				reg_user_obj.payment = payment
				last_pay = reg_user_obj.amount_paid
				tottal_paid = int(last_pay) + int(amount_paid)
				reg_user_obj.amount_paid = tottal_paid
				reg_user_obj.save()
				
			set_status(reg_user_obj)
			message = "You are successfully updated your registration for the event, Area 1 Agm of Round Table India hosted by QRT85 'Lets Go Nuts'. Your registration ID is : "+reg_user_obj.qrcode+ " And your tottal payment is Rs."+str(reg_user_obj.amount_paid)+"/-"
			message_status = requests.get('http://alerts.ebensms.com/api/v3/?method=sms&api_key=A2944970535b7c2ce38ac3593e232a4ee&to='+phone+'&sender=QrtReg&message='+message)
			try:
				send_email(email,message,reg_user_obj)
			except:
				pass
			if room_updates:
				message_status = requests.get('http://alerts.ebensms.com/api/v3/?method=sms&api_key=A2944970535b7c2ce38ac3593e232a4ee&to='+phone+'&sender=QrtReg&message='+message_hotel)
			return HttpResponseRedirect('/users/')
		except:
			message = "There is an issue with your registration. Please try again."
			messages.success(self.request, message)
			return HttpResponseRedirect(reverse('register_event'))






