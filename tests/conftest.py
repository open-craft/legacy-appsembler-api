"""
Shared fixtures and such for tests
"""

import pytest
from rest_framework.test import APIClient

from .factories import UserFactory


@pytest.fixture(scope="session")
def django_db_setup():
    """
    Avoid creating/setting up the test database

    Otherwise the tests crash with:
        django.db.utils.OperationalError: (1044, "Access denied for user 'openedx'@'%' to database 'test_openedx'")
    """


@pytest.fixture()
def superuser():
    user = UserFactory()
    user.is_superuser = True
    user.is_staff = True
    user.save()
    return user


@pytest.fixture()
def superuser_client(superuser):  # pylint: disable=redefined-outer-name
    client = APIClient()
    client.force_authenticate(user=superuser)
    return client
