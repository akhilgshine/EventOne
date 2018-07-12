from django import forms
from django.forms import ModelForm
from django.forms.fields import *
from django.forms.widgets import *
from django.utils.translation import ugettext_lazy as _

from events.models import *

# class RegisterForm(forms.Form):

class LoginForm(forms.Form):
    username = forms.CharField(max_length=255, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    error_messages = {
        'invalid_login': _('The username credential is unknown.'),
        'invalid_pass': _('Invalid password or PIN'),
        'inactive': _('This account is inactive'),
    }

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password'].widget.attrs['class'] = 'form-control'


class EventRegisterForm(forms.Form):
    table = forms.CharField(widget=forms.HiddenInput(), initial=123)
    first_name = forms.CharField(max_length=255, required=True)
    last_name = forms.CharField(max_length=255, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=255, required=True)
    payment = forms.CharField(max_length=255, required=True)
    amount_paid = forms.FloatField(required=True)
    contributed_amount = forms.IntegerField(initial=0)
    t_shirt_size = forms.ChoiceField(choices=T_SHIRT_CHOICES)

    # payment = ChoiceField(label='',
    # 	initial='bank',
    # 	widget=RadioSelect(renderer=TabRadioRenderer),
    # 	choices=(('cash','Cash'),('paytm','PayTm'),('credit/debit','Credit/Debit')))


class HotelForm(forms.ModelForm):
    checkin_date = forms.CharField(required=True)
    checkout_date = forms.CharField(required=True)
    room_number  = forms.CharField(required=False)

    class Meta:
        model = BookedHotel
        fields = ('room_type', 'hotel', 'tottal_rent', 'mode_of_payment', 'receipt_number', 'receipt_file', 'room_number')

    def __init__(self, *args, **kwargs):
        super(HotelForm, self).__init__(*args, **kwargs)
        self.fields['room_type'].widget.attrs['class'] = 'form-control'
        self.fields['hotel'].widget.attrs['placeholder'] = 'Hotel Name'
        self.fields['hotel'].widget.attrs['class'] = 'form-control'
        self.fields['hotel'].widget.attrs['readonly'] = 'readonly'
        # self.fields["hotel"].initial = Hotel.objects.all()[0].id

        self.fields['tottal_rent'].widget.attrs['class'] = 'form-control'
        self.fields['tottal_rent'].widget.attrs['placeholder'] = 'Rent'
        self.fields['room_number'].widget.attrs['class'] = 'form-control'
        self.fields['room_number'].widget.attrs['placeholder'] = 'Room Number'
        # self.fields['tottal_rent'].widget.attrs['readonly'] = 'readonly'

        self.fields['checkin_date'].widget.attrs['class'] = 'datepicker form-control'
        self.fields['checkout_date'].widget.attrs['class'] = 'datepicker form-control'


class UpdatePaymentForm(forms.ModelForm):
    class Meta:
        model = RegisteredUsers
        fields = ('contributed_amount', 'payment', 'reciept_number', 'reciept_file')

    def __init__(self, *args, **kwargs):
        super(UpdatePaymentForm, self).__init__(*args, **kwargs)
        self.fields['contributed_amount'].widget.attrs['class'] = 'form-control'


class UpgradeStatusForm(forms.ModelForm):
    amount_to_upgrade = forms.IntegerField(required=True)

    class Meta:
        model = RegisteredUsers
        fields = ('amount_paid', 'event_status', 'payment', 'reciept_number', 'reciept_file')

    def __init__(self, *args, **kwargs):
        super(UpgradeStatusForm, self).__init__(*args, **kwargs)
        self.fields['amount_paid'].widget.attrs['class'] = 'form-control'
        self.fields['amount_to_upgrade'].widget.attrs['class'] = 'form-control'
        self.fields['amount_to_upgrade'].widget.attrs['readonly'] = 'readonly'


class UpdateDuePaymentForm(forms.ModelForm):
    event_status = forms.ChoiceField(choices=STATUS_CHOICES, widget=RadioSelect())

    class Meta:
        model = RegisteredUsers
        fields = ('amount_paid', 'payment', 'reciept_number', 'reciept_file', 'event_status')

    def __init__(self, *args, **kwargs):
        super(UpdateDuePaymentForm, self).__init__(*args, **kwargs)
        self.fields['amount_paid'].widget.attrs['class'] = 'form-control'
        self.fields['event_status'].widget.attrs['class'] = 'd-inline'
        # self.fields['amount_paid'].widget.attrs['readonly'] = 'readonly'
        try:
            if self.instance and self.instance.event_user.member_type == 'Tabler':
                self.fields['event_status'].choices = [(u'Couple', u'Couple(2 Days)'), (u'Stag', u'Stag(2 Days)')]
        except EventUsers.DoesNotExist:
            pass


class UpdateProfileForm(forms.ModelForm):
    t_shirt_size = forms.ChoiceField(choices=T_SHIRT_CHOICES, required=False)
    member_type = forms.ChoiceField(choices=MEMBER_CHOICES)
    table = forms.ModelChoiceField(queryset=Table.objects.all())
    hotel = forms.ModelChoiceField(queryset=Hotel.objects.all(), required=False)

    class Meta:
        model = EventUsers
        fields = ('first_name', 'last_name', 'mobile', 'email', 't_shirt_size', 'member_type', 'table', 'hotel')

    def __init__(self, *args, **kwargs):
        super(UpdateProfileForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['class'] = 'form-control'
        self.fields['last_name'].widget.attrs['class'] = 'form-control'
        self.fields['mobile'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['member_type'].widget.attrs['class'] = 'form-control'
        self.fields['table'].widget.attrs['class'] = 'form-control'


class UpdateHotelDuePaymentForm(forms.ModelForm):
    class Meta:
        model = BookedHotel
        fields = ('tottal_rent', 'mode_of_payment', 'receipt_number', 'receipt_file')

    def __init__(self, *args, **kwargs):
        super(UpdateHotelDuePaymentForm, self).__init__(*args, **kwargs)
        self.fields['tottal_rent'].widget.attrs['class'] = 'form-control'
        self.fields['tottal_rent'].widget.attrs['readonly'] = 'readonly'


class ProxyHotelForm(forms.ModelForm):
    class Meta:
        model = ProxyHotelBooking
        fields = ('table', 'hotel', 'room_type', 'hotel_rent', 'check_in_date', 'check_out_date',)

    def __init__(self, *args, **kwargs):
        super(ProxyHotelForm, self).__init__(*args, **kwargs)
        self.fields['table'].widget.attrs['class'] = 'form-control'
        self.fields['room_type'].widget.attrs['class'] = 'form-control'
        self.fields['hotel'].widget.attrs['placeholder'] = 'Hotel Name'
        self.fields['hotel'].widget.attrs['class'] = 'form-control'
        self.fields["hotel"].initial = Hotel.objects.all()[0].id

        self.fields['hotel_rent'].widget.attrs['class'] = 'form-control'
        self.fields['hotel_rent'].widget.attrs['placeholder'] = 'Rent'

        self.fields['check_in_date'].widget.attrs['class'] = 'datepicker form-control'
        self.fields['check_out_date'].widget.attrs['class'] = 'datepicker form-control'


class UpdateTShirtForm(forms.ModelForm):
    class Meta:
        model = RegisteredUsers
        fields = ['t_shirt_size', ]

    def __init__(self, *args, **kwargs):
        super(UpdateTShirtForm, self).__init__(*args, **kwargs)
        self.fields['t_shirt_size'].widget.attrs['class'] = 'form-control'
