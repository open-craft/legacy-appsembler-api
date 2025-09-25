"""
Tests for the `legacy-appsembler-api` views module.
"""

import pytest
from django.urls import reverse


@pytest.mark.django_db(transaction=True)
def test_create_user_account(superuser_client):

    response = superuser_client.post(
        reverse("create_user_account_api"),
        {
            "username": "appsemblerapitestcreate",
            "password": "mypassword",
            "email": "appsemblerapitestcreate@example.com",
            "name": "my name",
            "send_activation_email": "False",
        },
        format="json",
    )

    assert response.status_code == 200
    assert "user_id " in response.data
