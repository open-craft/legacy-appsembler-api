"""
Database models for appsembler_api.
"""

from common.djangoapps.student.models import CourseEnrollment
from django.contrib import auth
from django.db import models
from opaque_keys.edx.django.models import CourseKeyField

User = auth.get_user_model()


class CourseRegistrationCode(models.Model):
    """
    This table contains registration codes
    With registration code, a user can register for a course for free

    .. no_pii:
    """

    class Meta:
        app_label = "shoppingcart"

    code = models.CharField(max_length=32, db_index=True, unique=True)
    course_id = CourseKeyField(max_length=255, db_index=True)
    created_by = models.ForeignKey(User, related_name="created_by_user", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.IntegerField(null=True)  # this was originally a foreign key to Order, but we don't use that
    mode_slug = models.CharField(max_length=100, null=True)
    is_valid = models.BooleanField(default=True)

    invoice = models.IntegerField(null=True)  # this was originally a foreign key to Invoice, but we don't use that
    invoice_item = models.IntegerField(
        null=True
    )  # this was originally a foreign key to CourseRegistrationCodeInvoiceItem, but we don't use that


class RegistrationCodeRedemption(models.Model):
    """
    This model contains the registration-code redemption info

    .. no_pii:
    """

    class Meta:
        app_label = "shoppingcart"

    order = models.IntegerField(null=True)  # this was originally a foreign key to Order, but we don't use that
    registration_code = models.ForeignKey(CourseRegistrationCode, db_index=True, on_delete=models.CASCADE)
    redeemed_by = models.ForeignKey(User, db_index=True, on_delete=models.CASCADE)
    redeemed_at = models.DateTimeField(auto_now_add=True, null=True)
    course_enrollment = models.ForeignKey(CourseEnrollment, null=True, on_delete=models.CASCADE)

    @classmethod
    def is_registration_code_redeemed(cls, course_reg_code):
        """
        Checks the existence of the registration code
        in the RegistrationCodeRedemption
        """
        return cls.objects.filter(registration_code__code=course_reg_code).exists()

    @classmethod
    def get_registration_code_redemption(cls, code, course_id):
        """
        Returns the registration code redemption object if found else returns None.
        """
        try:
            code_redemption = cls.objects.get(registration_code__code=code, registration_code__course_id=course_id)
        except cls.DoesNotExist:
            code_redemption = None
        return code_redemption

    @classmethod
    def create_invoice_generated_registration_redemption(cls, course_reg_code, user):  # pylint: disable=invalid-name
        """
        This function creates a RegistrationCodeRedemption entry in case the registration codes were invoice generated
        and thus the order_id is missing.
        """
        code_redemption = RegistrationCodeRedemption(registration_code=course_reg_code, redeemed_by=user)
        code_redemption.save()
        return code_redemption
