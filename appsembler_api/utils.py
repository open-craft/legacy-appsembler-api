"""
utility functions for API classes.
"""

from random import randint

from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from common.djangoapps.student.models import email_exists_or_retired, username_exists_or_retired
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from openedx.core.djangoapps.user_authn.views.password_reset import PasswordResetFormNoActive

def account_exists(email, username):
    # source: https://github.com/appsembler/edx-platform/blob/appsembler/psu-temp-tahoe-juniper/openedx/core/djangoapps/appsembler/api/v1/api.py#L35-L55
    """Check if an account exists for either the email or the username

    Both email and username are required as parameters, but either or both can
    be None

    Do we need to check secondary email? If so then check if the email exists:
    ```
    from student.models import AccountRecovery
    AccountRecovery.objects.filter(secondary_email=email).exists()
    ```
    """
    if email and email_exists_or_retired(email):
        email_exists = True
    else:
        email_exists = False
    if username and username_exists_or_retired(username):
        username_exists = True
    else:
        username_exists = False
    return email_exists or username_exists


def auto_generate_username(email):
    """
    This functions generates a valid username based on the email, also checks if
    the username exists and adds a random 3 digit int at the end to warranty
    uniqueness.
    """
    try:
        validate_email(email)
    except ValidationError:
        raise ValueError("Email is a invalid format")

    username = ''.join(e for e in email.split('@')[0] if e.isalnum())

    while account_exists(username=username, email=None):
        username = ''.join(e for e in email.split('@')[0] if e.isalnum()) + str(randint(100, 999))

    return username


def send_activation_email(request):
    form = PasswordResetFormNoActive(request.data)
    if form.is_valid():
        form.save(
            use_https=request.is_secure(),
            from_email=configuration_helpers.get_value(
                'email_from_address', settings.DEFAULT_FROM_EMAIL),
            request=request,
            subject_template_name='appsembler_api/set_password_subject.txt',
            email_template_name='appsembler_api/set_password_email.html')
        return True
    else:
        return False
