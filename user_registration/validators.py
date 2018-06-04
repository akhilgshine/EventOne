import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_phone(value):
    if not value.isdigit():
        raise ValidationError(
            _('%(value)s is not a number'),
            params={'value': value},
        )
    clean_phone_number = re.sub('[^0-9]+', '', value)
    formatted_phone_number = re.sub("(\d)(?=(\d{3})+(?!\d))", r"\1", "%d" % int(clean_phone_number[:-1])) + \
                             clean_phone_number[-1]
    return formatted_phone_number

