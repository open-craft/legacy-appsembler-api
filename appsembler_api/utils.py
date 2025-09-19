"""
utility functions for API classes.
"""

import logging
import random
import string

from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError
from django.http import Http404
from common.djangoapps.student.models import email_exists_or_retired, username_exists_or_retired
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from openedx.core.djangoapps.user_authn.views.password_reset import PasswordResetFormNoActive

from .models import CourseRegistrationCode, RegistrationCodeRedemption

AUDIT_LOG = logging.getLogger("audit")


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
        username = ''.join(e for e in email.split('@')[0] if e.isalnum()) + str(random.randint(100, 999))

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


def get_reg_code_validity(registration_code, request):
    """
    This function checks if the registration code is valid, and then checks if it was already redeemed.
    """
    reg_code_already_redeemed = False
    course_registration = None
    try:
        course_registration = CourseRegistrationCode.objects.get(code=registration_code)
    except CourseRegistrationCode.DoesNotExist:
        reg_code_is_valid = False
    else:
        if course_registration.is_valid:
            reg_code_is_valid = True
        else:
            reg_code_is_valid = False
        reg_code_already_redeemed = RegistrationCodeRedemption.is_registration_code_redeemed(registration_code)
    if not reg_code_is_valid:
        AUDIT_LOG.info(u"Redemption of a invalid RegistrationCode %s", registration_code)
        raise Http404()

    return reg_code_is_valid, reg_code_already_redeemed, course_registration


def generate_random_string(length):
    """
    Create a string of random characters of specified length
    """
    chars = [
        char for char in string.ascii_uppercase + string.digits + string.ascii_lowercase
        if char not in 'aAeEiIoOuU1l'
    ]
    return ''.join((random.choice(chars) for i in range(length)))


def random_code_generator():
    """
    generate a random alphanumeric code of length defined in
    REGISTRATION_CODE_LENGTH settings
    """
    code_length = getattr(settings, 'REGISTRATION_CODE_LENGTH', 8)
    return generate_random_string(code_length)


def save_registration_code(user, course_id, mode_slug, invoice=None, order=None, invoice_item=None):
    """
    recursive function that generate a new code every time and saves in the Course Registration Table
    if validation check passes

    Args:
        user (User): The user creating the course registration codes.
        course_id (str): The string representation of the course ID.
        mode_slug (str): The Course Mode Slug associated with any enrollment made by these codes.
        invoice (Invoice): (Optional) The associated invoice for this code.
        order (Order): (Optional) The associated order for this code.
        invoice_item (CourseRegistrationCodeInvoiceItem) : (Optional) The associated CourseRegistrationCodeInvoiceItem

    Returns:
        The newly created CourseRegistrationCode.

    """
    code = random_code_generator()

    course_registration = CourseRegistrationCode(
        code=code,
        course_id=str(course_id),
        created_by=user,
        invoice=invoice,
        order=order,
        mode_slug=mode_slug,
        invoice_item=invoice_item
    )
    try:
        with transaction.atomic():
            course_registration.save()
        return course_registration
    except IntegrityError:
        return save_registration_code(
            user, course_id, mode_slug, invoice=invoice, order=order, invoice_item=invoice_item
        )


class RedemptionCodeError(Exception):
    """An error occurs while processing redemption codes. """
    pass
