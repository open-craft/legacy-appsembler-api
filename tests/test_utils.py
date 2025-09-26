"""
Tests for the `legacy-appsembler-api` utils module.
"""

import re

import pytest
from django.conf import settings
from django.http import Http404

from shoppingcart.utils import (
    auto_generate_username,
    generate_random_string,
    get_reg_code_validity,
    random_code_generator,
    save_registration_code,
)

from .factories import UserFactory


def test_random_string():
    assert len(generate_random_string(34)) == 34


def test_random_code_generator():
    expected_length = settings.REGISTRATION_CODE_LENGTH
    assert expected_length == 13
    assert len(random_code_generator()) == expected_length


@pytest.mark.django_db
def test_save_registration_code():
    course_mode = "audit"
    course_id = "course-v1:OpenedX+DemoX+DemoCourse"
    user = UserFactory()
    course_registration_code = save_registration_code(user, course_id, course_mode)

    assert len(course_registration_code.code) == settings.REGISTRATION_CODE_LENGTH
    assert course_registration_code.mode_slug == course_mode
    assert str(course_registration_code.course_id) == course_id
    assert course_registration_code.order is None
    assert course_registration_code.invoice is None
    assert course_registration_code.invoice_item is None


@pytest.mark.django_db
def test_reg_code_validity_new_valid():
    course_mode = "audit"
    course_id = "course-v1:OpenedX+DemoX+DemoCourse"
    user = UserFactory()
    course_registration_code = save_registration_code(user, course_id, course_mode)

    reg_code_is_valid, reg_code_already_redeemed, course_registration_code_ = get_reg_code_validity(
        course_registration_code.code
    )

    assert reg_code_is_valid
    assert not reg_code_already_redeemed
    assert course_registration_code.pk == course_registration_code_.pk


@pytest.mark.django_db
def test_reg_code_validity_non_existant():
    with pytest.raises(Http404):
        get_reg_code_validity("thiscodedoesnotexist!")


@pytest.mark.django_db
def test_auto_generate_username():

    # it should raise an error with an invalid email
    with pytest.raises(ValueError):
        auto_generate_username("not-an-email")

    # test the base case of generating a username when there are no clashes
    username = auto_generate_username("legacy_appsemblerapi+1test@example.com")
    assert username == "legacyappsemblerapi1test"

    # create a user with this username so we get a clash next time
    user = UserFactory()
    user.username = username
    user.save()

    # try again - this should clash and add the NNN postfix to the username
    another_username = auto_generate_username("legacy_appsemblerapi+1test@example.com")
    assert re.match(r"^legacyappsemblerapi1test\d\d\d$", another_username)
