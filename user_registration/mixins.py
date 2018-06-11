from django.http import HttpResponseRedirect
from django.urls import reverse_lazy


class RegisteredObjectMixin(object):
    def get(self, request, *args, **kwargs):
        if self.request.user.registered_obj and self.request.user.registered_obj.is_payment_completed:
            return HttpResponseRedirect(reverse_lazy('user_profile'))
        else:
            return super(RegisteredObjectMixin, self).get(request, *args, **kwargs)
