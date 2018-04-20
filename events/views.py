# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import csv
import traceback
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import FormView, TemplateView, View, UpdateView, DeleteView, ListView
from django.core.urlresolvers import reverse
from django.contrib import messages
from events.templatetags import template_tags
import json
from events.forms import *
from events.models import *
from events.utils import send_email, set_status, hotelDetails
from django.contrib.auth import authenticate, login
import requests
from django.contrib.auth import logout
import re
import datetime

"""
    Home
    """


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
        # type: (object, object, object) -> object
        form = LoginForm()
        return render(request, self.template_name, {'form': form})

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
                    return render(self.request, self.template_name, {'form': form})
            else:
                return render(self.request, self.template_name, {'form': form})


"""
    Register View
    """


class RegisterEvent(TemplateView):
    template_name = 'register.html'

    def get(self, request, *args, **kwargs):
        context = {}
        if not request.user.is_authenticated():
            return HttpResponseRedirect(reverse('login'))

        context['form'] = EventRegisterForm()
        context['room_types'] = RoomType.objects.all()
        context['tables'] = Table.objects.all()  # .order_by('table_order')
        return render(request, self.template_name, context)

    def check_balance(self, amount):

        balance_amount = 0
        if int(amount) < 5000:
            balance_amount = 5000 - int(amount)
            if balance_amount > 0:
                return balance_amount
        return 0

    def get_reg_amt(self, member_type, status):
        if member_type == 'Tabler':
            if status == 'Stag':
                return 5000
            return 6000
        else:
            if status == 'Stag':
                return 4000
            elif status == 'Couple':
                return 5000
            elif status == 'Stag_Informal':
                return 2500
            return 3500

    def post(self, request, *args, **kwargs):
        context = {}
        message_hotel = ''
        message = ''
        room = ''
        try:
            print("\n")
            print(request.POST)
            print("\n")
            name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            email = request.POST.get('email', '')
            phone = request.POST.get('phone', '')
            table = request.POST.get('table_val', '')
            member_type = request.POST.get('member_type')
            status = request.POST.get('status')
            payment = request.POST.get('payment', '')
            amount_paid = int(request.POST.get('amount_paid'))

            hotel_name = request.POST.get('hotel_name', '')
            room_rent = request.POST.get('room_rent', '')
            room_type = request.POST.get('room_type', '')
            # book_friday = request.POST.get('book_friday','')
            checkin = request.POST.get('checkin_date')
            reciept_number = request.POST.get('reciept_number')
            reciept_file = request.FILES.get('reciept_file')
            other_contribution = request.POST.get('other_contribution')
            if not other_contribution:
                other_contribution = 0
            else:
                other_contribution = int(other_contribution)

            if not amount_paid:
                amount_paid = 0
            else:
                amount_paid = int(amount_paid)

            if checkin:
                checkin_date = datetime.datetime.strptime(checkin, "%d/%m/%Y")
            checkout = request.POST.get('checkout_date')
            if checkout:
                checkout_date = datetime.datetime.strptime(checkout, "%d/%m/%Y")

            # if book_friday:
            # 	book_friday = True
            # 	text = " for 3rd Aug 2018 to 5th Aug 2018 (two nights)"
            # else:
            # 	book_friday = False
            # 	text = " for 4th Aug 2018 to 5th Aug 2018 (one nights)"

            event = Event.objects.filter()[0]
            new_table = request.POST.get('other_table')
            if not new_table:
                new_table = request.POST.get('table_val')

            table, created = Table.objects.get_or_create(table_name=new_table,
                                                         event=event)
            if created:
                try:
                    table_order = int(re.search(r'\d+', new_table).group())
                    table.table_order = table_order
                    table.save()
                except:
                    table.save()

            event_user, created = EventUsers.objects.get_or_create(table=table,
                                                                   email=email)

            # event_user, created = EventUsers.objects.get_or_create(email=email)

            if created:
                event_user.table = table
            else:
                if event_user.table != table:
                    message = "User with this MailID '" + str(event_user.email) + "' already exist in table '" + str(
                        event_user.table.table_name) + "'"
                    messages.success(self.request, message)
                    return HttpResponseRedirect(reverse('register_event'))
            event_user.member_type = member_type
            event_user.first_name = name
            event_user.last_name = last_name
            event_user.mobile = phone
            event_user.save()
            try:
                event_reg, created = RegisteredUsers.objects.get_or_create(event_user=event_user,
                                                                           event=event,
                                                                           table=table)

                if created:
                    try:
                        qrcode = RegisteredUsers.objects.latest('qrcode').qrcode
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
                    except Exception as e:
                        print(e, "Exception at line 184")
                        qrcode = 'QRT8001'

                    print("amount_paid : ", amount_paid)
                    balance_amount = self.check_balance(amount_paid)

                    event_reg.qrcode = qrcode

                else:
                    last_pay = event_reg.amount_paid
                    if not last_pay:
                        last_pay = 0
                    tottal_paid = amount_paid

                    balance_amount = self.check_balance(tottal_paid)
                event_reg.payment = payment

                if not other_contribution:
                    other_contribution = 0
                reg_amt = self.get_reg_amt(member_type, status)
                if reg_amt < amount_paid:
                    other_contribution = other_contribution + (amount_paid - reg_amt)
                    amount_paid = reg_amt
                    print(other_contribution, "other_contribution")
                    print(amount_paid, "amount_paid")

                event_reg.contributed_amount = int(other_contribution)
                event_reg.balance_amount = balance_amount
                event_reg.event_status = status

                event_reg.reciept_number = reciept_number
                event_reg.reciept_file = reciept_file
                event_reg.amount_paid = amount_paid
                event_reg.save()
                if amount_paid:
                    PaymentDetails.objects.create(reg_event=event_reg,
                                                  amount=amount_paid
                                                  )
                if room_type:
                    try:
                        room = RoomType.objects.get(id=room_type)
                    except Exception as e:
                        print(e, "Exception at line 213")
                        room = None
                if room:
                    hotel_obj, created = Hotels.objects.get_or_create(registered_users=event_reg)
                    if created:
                        hotel_obj.hotel_name = hotel_name
                        hotel_obj.tottal_rent = int(room_rent)
                        # hotel_obj.book_friday = book_friday
                        hotel_obj.checkin_date = checkin_date
                        hotel_obj.checkout_date = checkout_date
                        hotel_obj.room_type = room
                        hotel_obj.save()
                        room.rooms_available = room.rooms_available - 1
                        room.save()
                        message_hotel = "You have successfully booked room in Hotel Raviz Kollam for the event, Area 1 Agm of Round Table India hosted by QRT85 'Lets Go Nuts'. You have choosen : '" + room.room_type + "'"
                        # message_hotel += text
                        message_hotel += " And your total rent is Rs." + str(room_rent) + "/-"
                    else:
                        hotel_obj.hotel_name = hotel_name
                        hotel_obj.tottal_rent = room_rent
                        hotel_obj.checkin_date = checkin_date
                        hotel_obj.checkout_date = checkout_date
                        if not hotel_obj.room_type == room:
                            room_type_obj = hotel_obj.room_type
                            room_type_obj.rooms_available = room_type_obj.rooms_available + 1

                            room_type_obj.save()
                            room.rooms_available = room.rooms_available - 1
                            room.save()
                            hotel_obj.room_type = room
                            message_hotel = "You have successfully updated room in Hotel Raviz Kollam for the event, Area 1 Agm of Round Table India hosted by QRT85 'Lets Go Nuts'. You have choosen : '" + room.room_type + "'"
                            # message_hotel += text
                            message_hotel += " And your total rent is Rs." + str(room_rent) + "/-"
                        hotel_obj.save()

            except Exception as e:
                print(traceback.format_exc())
                print (e, "@@@EXCEPTION@@@")
                if created and event_reg:
                    event_reg.delete()
                event_reg = None

            if event_reg:
                # set_status(event_reg))
                message = "You are successfully registered for the event, Area 1 Agm of Round Table India hosted by QRT85 'Lets Go Nuts'. Your registration ID is : " + event_reg.qrcode + " And you have paid Rs." + str(
                    event_reg.amount_paid) + "/-"

                message_status = requests.get(
                    'http://alerts.ebensms.com/api/v3/?method=sms&api_key=A2944970535b7c2ce38ac3593e232a4ee&to=' + phone + '&sender=QrtReg&message=' + message)
                try:
                    send_email(email, message, event_reg)
                except Exception as e:
                    print(e, "Exception at send mail")
                    pass

                if message_hotel:
                    message_status = requests.get(
                        "http://unifiedbuzz.com/api/insms/format/json/?mobile=" + phone + "&text=" + message_hotel + "&flash=0&type=1&sender=QrtReg",
                        headers={"X-API-Key": "918e0674e62e01ec16ddba9a0cea447b"})

                return HttpResponseRedirect("/register/success/" + str(event_reg.id))
            else:
                message = " There is an issue with your registration. Please try again"
                messages.success(self.request, message)
                return HttpResponseRedirect(reverse('register_event'))
        except Exception as e:
            print(traceback.format_exc())
            print (e, "@@@EXCEPTION@@@")
            message = "Exception : There is an issue with your registration. Please try again."
            messages.success(self.request, message)
            return HttpResponseRedirect(reverse('register_event'))


class RegSuccessView(TemplateView):
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
            mimetype = 'application/json'
            results = []
            q = request.GET.get('term', '')
            table_name = request.GET.get('table')
            try:
                Table.objects.get(table_name=table_name)
            except Table.DoesNotExist:
                return HttpResponse([], mimetype)

            table = Table.objects.get(table_name=table_name)
            users = EventUsers.objects.filter(table=table)

            users = users.filter(first_name__icontains=q)

            for user in users:
                user_json = {}
                user_json['id'] = user.id
                user_json['label'] = user.first_name + ' ' + user.last_name
                user_json['value'] = user.id
                results.append(user_json)

            data = json.dumps(results)
            return HttpResponse(data, mimetype)


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

"""
    Get user data
    """


class GetUserData(TemplateView):
    def get(self, request):
        data = {}
        django_messages = []
        data['user_exist'] = ''
        user_id = request.GET.get('user_id')
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
        try:
            user = EventUsers.objects.get(id=user_id)
        except EventUsers.DoesNotExist:
            try:
                user = EventUsers.objects.get(user_id.split(' ')[0], user_id.split(' ')[1])
            except EventUsers.DoesNotExist:
                data['success'] = "False"
                data['error_msg'] = "something went WRONG"
                return HttpResponse(json.dumps(data), content_type='application/json')

        try:
            registered_user = RegisteredUsers.objects.get(event_user=user, table=table)
            # data['balance'] = int(registered_user.balance_amount)
            message = "This user is already registered for this event. Please see the details here."
            messages.success(self.request, message)

            data['paid_amount'] = registered_user.amount_paid
            data['payment_type'] = registered_user.payment
            data['user_exist'] = 'true'
            data['status'] = registered_user.event_status
            # return HttpResponseRedirect(reverse('list_users'))

        except (RegisteredUsers.DoesNotExist):
            print("user not exist")
            data['user_exist'] = 'false'
            data['other_table'] = ''
        else:
            try:
                hotel_obj = Hotels.objects.get(registered_users=registered_user)
            except Hotels.DoesNotExist:
                pass
            else:
                data['hotel_name'] = hotel_obj.hotel_name
                data['tottal_rent'] = hotel_obj.tottal_rent
                data['hotel_type'] = hotel_obj.room_type.room_type
                data['book_friday'] = hotel_obj.book_friday
                data['room_type_id'] = hotel_obj.room_type.id
                data['checkin_date'] = hotel_obj.checkin_date.strftime("%d-%m-%Y")
                data['checkout_date'] = hotel_obj.checkout_date.strftime("%d-%m-%Y")
                print("TYPE : " + str(hotel_obj.room_type.room_type))
        data['email'] = user.email
        data['mobile'] = user.mobile
        data['first_name'] = user.first_name
        data['last_name'] = user.last_name
        data['success'] = "True"
        print("Data : ", data)

        return HttpResponse(json.dumps(data), content_type='application/json')


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')


"""
    User List View
    """


class ListUsers(ListView):
    template_name = 'user_list.html'
    queryset = RegisteredUsers.objects.filter(is_active=True)

    def get_queryset(self):
        self.queryset = super(ListUsers, self).get_queryset()
        if self.request.GET.get('is_active') == 'False':
            self.queryset = RegisteredUsers.objects.filter(is_active=False)
        elif self.request.GET.get('hotel') == 'True':
            hotels = Hotels.objects.filter(registered_users__is_active=True).values_list('registered_users__id', flat=True)
            hotel_booked_users = self.queryset.filter(id__in=hotels)
            self.queryset = hotel_booked_users
        elif self.request.GET.get('stag') == 'True':
            self.queryset = self.queryset.filter(event_status='Stag')
        elif self.request.GET.get('couple') == 'True':
            self.queryset = self.queryset.filter(event_status='Couple')
        elif self.request.GET.get('complete') == 'True':
            all_users = RegisteredUsers.objects.filter(is_active=True)
            full_paid_relevant_users = []
            for user in all_users:
                completely_paid = template_tags.payment_status(user.id)
                if completely_paid == 'Complete':
                    full_paid_relevant_users.append(user.id)
            self.queryset = self.queryset.filter(id__in=full_paid_relevant_users)
        elif self.request.GET.get('partial') == 'True':
            all_users = RegisteredUsers.objects.filter(is_active=True)
            partial_paid_relevant_users = []
            for users in all_users:
                partially_paid = template_tags.payment_status(users.id)
                if partially_paid == 'Partial':
                    partial_paid_relevant_users.append(users.id)
            self.queryset = self.queryset.filter(id__in=partial_paid_relevant_users)
        elif self.request.GET.get('date') == 'aug3':
            hotels = Hotels.objects.filter(registered_users__is_active=True, checkin_date__lte='2018-08-03', checkout_date__gte='2018-08-03').values_list('registered_users__id', flat=True)
            self.queryset = self.queryset.filter(id__in=hotels)
        elif self.request.GET.get('date') == 'aug4':
            hotels = Hotels.objects.filter(registered_users__is_active=True, checkin_date__lte='2018-08-04', checkout_date__gte='2018-08-04').values_list('registered_users__id', flat=True)
            self.queryset = self.queryset.filter(id__in=hotels)
        else:
            self.queryset = self.queryset.filter(is_active=True)
        return self.queryset

    def get_context_data(self, **kwargs):
        context = super(ListUsers, self).get_context_data(**kwargs)
        registered_users = self.queryset
        hotels = []
        for user in registered_users:
            try:
                hotels.append(user.hotel.all().first())
            except:
                hotels.append('Not Booked')
        context['hotels'] = hotels
        context['is_active'] = self.request.GET.get('is_active')
        context['users'] = registered_users
        context['tables'] = Table.objects.all()
        context['total_paid_registration'] = self.queryset.aggregate(Sum('amount_paid')).values()[0] or 0.00
        context['total_contributions'] = self.queryset.aggregate(Sum('contributed_amount')).values()[0] or 0.00

        context['total_registration_due'] = sum(item.due_amount for item in self.queryset)
        context['total_hotel_due'] = sum(item.hotel_due for item in self.queryset)
        context['total_due'] = context['total_registration_due'] + context['total_hotel_due']
        context['total_paid_hotel'] = Hotels.objects.filter(registered_users__is_active=True).aggregate(Sum('tottal_rent')).values()[0] or 0.00
        context['total_amount_paid'] = context['total_paid_registration'] + context['total_paid_hotel'] + context[
            'total_contributions'] or 0.00
        return context


"""
   Coupon View
    """


class InvoiceView(TemplateView):
    template_name = 'coupon.html'

    # def get_context_data(self, **kwargs):
    #     context = super(InvoiceView, self).get_context_data(**kwargs)
    #     context['event_user'] = RegisteredUsers.objects.all()
    #     return context

    def get(self, request, *args, **kwargs):
        context = {}
        pk = kwargs.pop('pk')
        event_reg = RegisteredUsers.objects.get(id=pk)

        if event_reg.amount_paid < 5000:
            context['partial'] = 'Partial'

        context['hotel'] = hotelDetails(event_reg)
        context['event_register'] = event_reg
        context['payment_details'] = PaymentDetails.objects.filter(reg_event=event_reg)
        return render(request, self.template_name, context)


"""
    User Update View
    """


class UserRegisterUpdate(TemplateView):
    template_name = 'register.html'
    form = EventRegisterForm

    def get(self, request, *args, **kwargs):
        context = {}
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

    def post(self, request, *args, **kwargs):
        try:

            # room_updates = False
            message_hotel = ''
            name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            email = request.POST.get('email', '')
            phone = request.POST.get('phone', '')
            # table = request.POST.get('table_val', '')
            update_id = request.POST.get('update_id', '')

            payment = request.POST.get('payment', '')
            amount_paid = request.POST.get('amount_paid', '')
            room_type = request.POST.get('room_type', '')
            hotel_name = request.POST.get('hotel_name', '')
            room_rent = request.POST.get('room_rent', '')
            # book_friday = request.POST.get('book_friday', '')

            checkin = request.POST.get('checkin_date')
            print("Date In : ", checkin)
            if checkin:
                checkin_date = datetime.datetime.strptime(checkin, "%d/%m/%Y")

            checkout = request.POST.get('checkout_date')
            print("Date Out : ", checkout)
            if checkout:
                checkout_date = datetime.datetime.strptime(checkout, "%d/%m/%Y")
            text = str(checkin_date) + " to " + str(checkout_date)
            # if book_frida y:
            #     book_friday = True
            #     text = " for 3rd Aug 2018 to 5th Aug 2018 (two nights)"
            # else:
            #     text = " for 4th Aug 2018 to 5th Aug 2018 (one night)"
            #     book_friday = False

            reg_user_obj = RegisteredUsers.objects.get(id=update_id)

            user = EventUsers.objects.get(id=reg_user_obj.event_user.id)

            if amount_paid:
                PaymentDetails.objects.create(reg_event=reg_user_obj,
                                              amount=amount_paid)
            try:
                room = RoomType.objects.get(id=room_type)
                hotel_obj, created = Hotels.objects.get_or_create(registered_users=reg_user_obj)
                if created:
                    hotel_obj.hotel_name = hotel_name
                    hotel_obj.tottal_rent = int(room_rent)
                    # hotel_obj.book_friday = book_friday
                    hotel_obj.checkin_date = checkin_date
                    hotel_obj.checkout_date = checkout_date
                    hotel_obj.room_type = room
                    hotel_obj.save()
                    room.rooms_available = room.rooms_available - 1
                    room.save()
                    message_hotel = "You have successfully booked room in Hotel Raviz Kollam for the event, Area 1 Agm of Round Table India hosted by QRT85 'Lets Go Nuts'. You have choosen : '" + room.room_type + "'"
                    message_hotel += text
                    message_hotel += " And your total rent is Rs." + str(room_rent) + "/-"
                else:
                    hotel_obj.hotel_name = hotel_name
                    hotel_obj.checkin_date = checkin_date
                    hotel_obj.checkout_date = checkout_date
                    hotel_obj.tottal_rent = room_rent

                    if not hotel_obj.checkout_date == checkout_date or hotel_obj.checkout_date == checkout_date:
                        message_hotel = "You have successfully updated room in Hotel Raviz Kollam for the event, Area 1 Agm of Round Table India hosted by QRT85 'Lets Go Nuts'. You have choosen : '" + room.room_type + "'"
                        message_hotel += text
                        message_hotel += " And your total rent is Rs." + str(room_rent) + "/-"

                    if not hotel_obj.room_type == room:
                        room_type_obj = hotel_obj.room_type
                        room_type_obj.rooms_available = room_type_obj.rooms_available + 1

                        room_type_obj.save()
                        room.rooms_available = room.rooms_available - 1
                        room.save()
                        hotel_obj.room_type = room
                        message_hotel = "You have successfully updated room in Hotel Raviz Kollam for the event, Area 1 Agm of Round Table India hosted by QRT85 'Lets Go Nuts'. You have choosen : '" + room.room_type + "'"
                        message_hotel += text
                        message_hotel += " And your total rent is Rs." + str(room_rent) + "/-"
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

            message = "You are successfully updated your registration for the event, Area 1 Agm of Round Table India hosted by QRT85 'Lets Go Nuts'. Your registration ID is : " + reg_user_obj.qrcode + " And your total payment is Rs." + str(
                reg_user_obj.amount_paid) + "/-"

            message_status = requests.get(
                "http://unifiedbuzz.com/api/insms/format/json/?mobile=" + phone + "&text=" + message + "&flash=0&type=1&sender=QrtReg",
                headers={"X-API-Key": "918e0674e62e01ec16ddba9a0cea447b"})

            # message_status = requests.get(
            #     'http://alerts.ebensms.com/api/v3/?method=sms&api_key=A2944970535b7c2ce38ac3593e232a4ee&to=' + phone + '&sender=QrtReg&message=' + message)
            # message_status = requests.get(
            #     "http://unifiedbuzz.com/api/insms/format/json/?mobile="+ phone +"&api_key="+'11111'+"&text="+message+"&flash=0&type=1&sender=QrtReg")

            try:
                send_email(email, message, reg_user_obj)
            except:
                pass
            if message_hotel:
                message_status = requests.get(
                    "http://unifiedbuzz.com/api/insms/format/json/?mobile=" + phone + "&text=" + message + "&flash=0&type=1&sender=QrtReg",
                    headers={"X-API-Key": "918e0674e62e01ec16ddba9a0cea447b"})

            return HttpResponseRedirect('/users/')
        except:
            message = "There is an issue with your registration. Please try again."
            messages.success(self.request, message)
            return HttpResponseRedirect(reverse('register_event'))


class UpdateHotelView(UpdateView):
    template_name = "update_hotel.html"
    form_class = HotelForm
    success_url = '/users/'
    queryset = RegisteredUsers.objects.all()

    def get_initial(self):
        initial = super(UpdateHotelView, self).get_initial()
        try:
            self.hotel_obj = Hotels.objects.get(registered_users=self.object)
        except Hotels.DoesNotExist:
            self.hotel_obj = ''
        else:
            initial['tottal_rent'] = self.hotel_obj.registered_users.hotel_due
        return initial

    def get_context_data(self, **kwargs):
        context = super(UpdateHotelView, self).get_context_data(**kwargs)
        context['form'] = HotelForm()
        context['room_types'] = RoomType.objects.all()
        context['hotel_obj'] = self.hotel_obj
        return context

    def form_valid(self, form):
        registered_user_obj = RegisteredUsers.objects.get(id=self.kwargs.pop('pk'))
        checkin = form.cleaned_data['checkin_date']
        checkout = form.cleaned_data['checkout_date']
        checkin_date = datetime.datetime.strptime(checkin, "%d/%m/%Y")
        checkout_date = datetime.datetime.strptime(checkout, "%d/%m/%Y")
        hotel_obj, created = Hotels.objects.get_or_create(registered_users=registered_user_obj)
        hotel_obj.hotel_name = form.cleaned_data['hotel_name']
        hotel_obj.mode_of_payment = form.cleaned_data['mode_of_payment']
        if hotel_obj.registered_users.hotel_due > 0:
            current_rent = hotel_obj.tottal_rent
            hotel_obj.tottal_rent = form.cleaned_data['tottal_rent'] + current_rent
        else:
            hotel_obj.tottal_rent = form.cleaned_data['tottal_rent']
        hotel_obj.room_type = form.cleaned_data['room_type']
        hotel_obj.checkin_date = checkin_date
        hotel_obj.checkout_date = checkout_date
        hotel_obj.receipt_number = form.cleaned_data['receipt_number']
        hotel_obj.receipt_file = form.cleaned_data['receipt_file']
        hotel_obj.save()
        if created:
            hotel_obj.room_type.rooms_available -= 1
            hotel_obj.room_type.save()

        if created:
            message_hotel = "You have successfully booked room in Hotel Raviz Kollam for the event, Area 1 Agm of Round Table India hosted by QRT85 'Lets Go Nuts'. You have choosen : '" + str(
                hotel_obj.room_type) + "' "
            message_hotel += " And your total rent is Rs." + str(hotel_obj.tottal_rent) + "/-"
        else:
            message_hotel = "You have successfully updated room in Hotel Raviz Kollam for the event, Area 1 Agm of Round Table India hosted by QRT85 'Lets Go Nuts'. You have choosen : '" + str(
                hotel_obj.room_type) + "' "
            message_hotel += " And your total rent is Rs." + str(hotel_obj.tottal_rent) + "/-"

        return HttpResponseRedirect(self.get_success_url())


class UpdateContributionPaymentView(UpdateView):
    template_name = 'update_reg_payment.html'
    form_class = UpdatePaymentForm
    success_url = '/users'
    queryset = RegisteredUsers.objects.all()

    def get_initial(self):
        initial = super(UpdateContributionPaymentView, self).get_initial()
        initial['contributed_amount'] = 0
        return initial

    def form_valid(self, form):
        obj = self.get_object()
        current_contribution = obj.contributed_amount
        # balance = obj.balance_amount
        if not current_contribution:
            current_contribution = 0

        obj = form.save(commit=False)

        updated_contribution = form.cleaned_data.get('contributed_amount')

        if not updated_contribution:
            updated_contribution = 0
        #
        # if balance > updated_amount:
        #     balance = balance - updated_amount
        #     updated_amount = current + updated_amount
        #     contributed_amount = 0
        # else:
        #     updated_amount = current + balance
        #     balance = 0
        #     contributed_amount = updated_amount - balance

        obj.contributed_amount = int(current_contribution) + int(updated_contribution)
        obj.save()
        return super(UpdateContributionPaymentView, self).form_valid(form)

    def form_invalid(self, form):
        return super(UpdateContributionPaymentView, self).form_invalid()


class UpgradeStatusView(UpdateView):
    template_name = 'upgrade_status.html'
    form_class = UpgradeStatusForm
    success_url = '/users'
    queryset = RegisteredUsers.objects.all()

    def get_initial(self):
        initial = super(UpgradeStatusView, self).get_initial()
        return initial

    def form_valid(self, form):
        # import pdb;pdb.set_trace()
        obj = self.get_object()
        current = obj.amount_paid
        obj = form.save(commit=False)
        if self.request.POST.get('status'):
            obj.event_status = self.request.POST.get('status')
        obj.amount_paid = current + form.cleaned_data.get('amount_to_upgrade')
        obj.save()

        # message = "You are successfully updated your status of registration to " + obj.event_status + "for the event, Area 1 Agm of Round Table India hosted by QRT85 'Lets Go Nuts'. Your registration ID is : " + obj.qrcode + " And your  total payment is Rs." + str(
        #     obj.amount_paid) + "/-"
        # # send_email(obj.event_user.email, message, obj)
        # message_status = requests.get(
        #     "http://unifiedbuzz.com/api/insms/format/json/?mobile=" + obj.event_user.mobile + "&text=" + message + "&flash=0&type=1&sender=QrtReg",
        #     headers={"X-API-Key": "918e0674e62e01ec16ddba9a0cea447b"})
        return super(UpgradeStatusView, self).form_valid(form)

    def form_invalid(self, form):
        return super(UpgradeStatusView, self).form_invalid(form)


class DashBoardView(ListView):
    template_name = "dashboard.html"

    def get_queryset(self):
        self.queryset = RegisteredUsers.objects.filter(is_active=True)
        return self.queryset

    def get_context_data(self, **kwargs):
        context = super(DashBoardView, self).get_context_data(**kwargs)
        context['registered_user'] = self.queryset
        context['stag_user'] = self.queryset.filter(event_status='Stag')
        context['couple_user'] = self.queryset.filter(event_status='Couple')
        context['hotels_booked'] = Hotels.objects.filter(registered_users__is_active=True)
        context['total_contributions'] = self.queryset.aggregate(Sum('contributed_amount')).values()[0] or 0.00

        context['booked_room_types'] = RoomType.objects.all()
        context['room_count'] = RoomType.objects.aggregate(Sum('rooms_available')).values()[0] or 0
        context['total_rooms'] = Hotels.objects.filter(registered_users__is_active=True).count() + context['room_count']
        context['total_rooms_booked'] =  context['total_rooms'] - context['room_count']

        context['total_paid_registration'] = self.queryset.aggregate(Sum('amount_paid')).values()[
                                                 0] or 0.00
        context['total_paid_hotel'] = Hotels.objects.all().aggregate(Sum('tottal_rent')).values()[0] or 0.00
        context['total_amount_paid'] = context['total_paid_registration'] + context['total_paid_hotel'] \
                                       + context['total_contributions'] or 0.00
        return context


class DownloadCSVView(TemplateView):
    template_name = 'user_list.html'

    def get(self, request, *args, **kwargs):
        get_user_registered = RegisteredUsers.objects.all()
        total_paid_registration = RegisteredUsers.objects.all().aggregate(Sum('amount_paid')).values()[
                                      0] or 0.00
        total_contributions = RegisteredUsers.objects.all().aggregate(Sum('contributed_amount')).values()[0] or 0.00
        total_registration_due = sum(item.due_amount for item in RegisteredUsers.objects.all())
        total_hotel_due = sum(item.hotel_due for item in RegisteredUsers.objects.all())
        total_due = total_registration_due + total_hotel_due
        total_paid_hotel = Hotels.objects.all().aggregate(Sum('tottal_rent')).values()[0] or 0.00
        total_amount_paid = total_paid_registration + total_paid_hotel + total_contributions or 0.00
        if get_user_registered:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="registered_users.csv"'
            writer = csv.writer(response)
            writer.writerow(['Name', 'Table', 'Registration Code', 'Phone', 'Email', 'Reg Type', 'Partial/Completely',
                             'Registration Amount ', 'Amount Due', 'Room', 'Hotel Name', 'Room Type', 'Check-In',
                             'Check-Out', 'No of Nights', 'Hotel Amount Paid', 'Hotel Dues', '', 'Contribution',
                             'Total Payment', 'Total Due'])
            for users in get_user_registered:
                try:
                    payment_status = template_tags.payment_status(users.id)
                    try:
                        user_hotel = users.hotel.all()[0]
                        hotel_days = template_tags.no_of_night(users.id)

                    except IndexError:
                        user_hotel = None
                        hotel_days = '-'
                    if user_hotel:
                        room_type = user_hotel.room_type.room_type
                        hotel_name = user_hotel.hotel_name
                        check_in_date = user_hotel.checkin_date
                        check_out_date = user_hotel.checkout_date
                        hotel_rent = user_hotel.tottal_rent

                    else:
                        room_type = '-'
                        hotel_name = '-'
                        check_in_date = '-'
                        check_out_date = '-'
                        hotel_rent = '-'
                    writer.writerow(
                        [users.event_user.first_name + '' + users.event_user.last_name, users.table.table_name,
                         users.qrcode, users.event_user.mobile,
                         users.event_user.email, users.event_status, payment_status, users.amount_paid,
                         users.due_amount, '',
                         hotel_name, room_type, check_in_date, check_out_date, hotel_days, hotel_rent, users.hotel_due,
                         '', users.contributed_amount, users.total_paid,
                         users.total_due])
                except Exception as e:
                    print e
            writer.writerow(
                ['', '', '',
                 '',
                 '', '', '', total_paid_registration,
                 total_registration_due, '',
                 '', '', '', '', '', total_paid_hotel, total_hotel_due, '',
                 total_contributions, total_amount_paid,
                 total_due])
            return response
        return super(DownloadCSVView, self).get(request, *args, **kwargs)


class DuePaymentView(UpdateView):
    template_name = 'update_due.html'
    form_class = UpdateDuePaymentForm
    success_url = '/users'
    queryset = RegisteredUsers.objects.all()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        init_val = self.object.amount_paid
        amount = int(request.POST.get('amount_paid'))
        self.object.amount_paid = init_val + amount
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_initial(self):
        initial = super(DuePaymentView, self).get_initial()
        initial['amount_paid'] = self.object.due_amount
        return initial


class AddContributionListPage(TemplateView):
    template_name = 'add_contirbution_list.html'

    def get_context_data(self, **kwargs):
        context = super(AddContributionListPage, self).get_context_data(**kwargs)
        context['registered_users'] = RegisteredUsers.objects.filter(is_active=True)
        return context


class DeleteHotelView(DeleteView):
    model = Hotels
    success_url = '/users'

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.room_type.rooms_available += 1
        self.object.room_type.save()
        self.object.delete()
        return HttpResponseRedirect(success_url)


class DeleteRegisteredUsers(DeleteView):
    model = RegisteredUsers
    template_name = 'registered_users_confirm_delete.html'
    success_url = '/users'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save()
        return HttpResponseRedirect(self.success_url)


class AddToRegistrationView(View):

    def get(self, request, *args, **kwargs):
        user_id = RegisteredUsers.objects.get(id=self.kwargs['pk'])
        user_id.is_active = True
        user_id.save()
        return HttpResponseRedirect('/users')


class EditRegistrationView(UpdateView):
    template_name = 'update_profile.html'
    form_class = UpdateProfileForm
    queryset = EventUsers.objects.all()
    success_url = '/users/'

    def get_context_data(self, *args, **kwargs):
        context = super(EditRegistrationView, self).get_context_data(**kwargs)
        pk = self.object
        event_registered_user =RegisteredUsers.objects.get(event_user=self.object)
        try:
            hotel_obj = Hotels.objects.get(registered_users=event_registered_user)
        except:
            hotel_obj = None
        context['event_registered_user'] = event_registered_user
        context['room_types'] = RoomType.objects.all()
        context['hotel_obj'] = hotel_obj
        return context

    def form_valid(self, form):
        registered_user_obj = RegisteredUsers.objects.get(event_user=self.object)
        if self.request.POST.get('checkin_date'):
            checkin = datetime.datetime.strptime(self.request.POST.get('checkin_date'), "%d/%m/%Y")
        else:
            checkin = ""
        if self.request.POST.get('checkout_date'):
            checkout = datetime.datetime.strptime(self.request.POST.get('checkout_date'), "%d/%m/%Y")
        else:
            checkout = ""
        hotel_obj, created = Hotels.objects.get_or_create(registered_users=registered_user_obj)
        hotel_obj.hotel_name = self.request.POST['hotel_name']
        hotel_obj.mode_of_payment = self.request.POST['payment']
        if hotel_obj.registered_users.hotel_due > 0:
            current_rent = hotel_obj.tottal_rent
            hotel_obj.tottal_rent = int(self.request.POST['tottal_rent']) + current_rent
        else:
            hotel_obj.tottal_rent = self.request.POST['tottal_rent']
        self.update_hotel(hotel_obj, self.request.POST,checkin,checkout)
        self.update_registred_user(registered_user_obj)
        form.save()
        if created:
            hotel_obj.room_type.rooms_available -= 1
            hotel_obj.room_type.save()
        if created:
            message_hotel = "You have successfully booked room in Hotel Raviz Kollam for the event, Area 1 Agm of Round Table India hosted by QRT85 'Lets Go Nuts'. You have choosen : '" + str(
                hotel_obj.room_type) + "' "
            message_hotel += " And your total rent is Rs." + str(hotel_obj.tottal_rent) + "/-"
        else:
            message_hotel = "You have successfully updated room in Hotel Raviz Kollam for the event, Area 1 Agm of Round Table India hosted by QRT85 'Lets Go Nuts'. You have choosen : '" + str(
                hotel_obj.room_type) + "' "
            message_hotel += " And your total rent is Rs." + str(hotel_obj.tottal_rent) + "/-"

        return HttpResponseRedirect(self.get_success_url())

    def update_hotel(self, hotel_obj, form, checkin, checkout):
        room_id = self.request.POST['room_type_sel'].split(":")[0]
        if room_id and room_id != '0':
            hotel_obj.room_type = RoomType.objects.get(id=room_id)
        if checkin :
            hotel_obj.checkin_date = checkin
        if checkout:
            hotel_obj.checkout_date = checkout
        hotel_obj.receipt_number = self.request.POST.get('receipt_number')
        hotel_obj.receipt_file = self.request.POST.get('receipt_file')
        hotel_obj.save()
        return True

    def update_registred_user(self,registered_user_obj):
        if registered_user_obj.event_status != self.request.POST.get('status'):
            if registered_user_obj.event_status== 'Stag':
                registered_user_obj.amount_paid = 1000
                if registered_user_obj.amount_paid> int(self.request.POST.get('amount_paid')):
                    registered_user_obj.contributed_amount =registered_user_obj.contributed_amount+(int(self.request.POST.get('amount_paid'))-1000)
            else:
                registered_user_obj.contributed_amount = registered_user_obj.contributed_amount +1000
                registered_user_obj.amount_paid = 5000
        registered_user_obj.event_status = self.request.POST.get('status')
        registered_user_obj.reciept_number = self.request.POST.get('reciept_number')
        if self.request.FILES.get('reciept_file'):
            registered_user_obj.reciept_file = self.request.FILES.get('reciept_file')
        registered_user_obj.save()