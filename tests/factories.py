"""
Factories for creating instances of models for tests
"""

import factory
from django.contrib import auth

User = auth.get_user_model()


# from https://github.com/open-craft/learning-paths-plugin/blob/main/learning_paths/tests/factories.py
class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: "legacyappsemblerapi_test_user_%d" % n)
    password = factory.PostGenerationMethodCall("set_password", "password")
    is_active = True
    is_superuser = False
    is_staff = False
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")

    class Meta:
        model = User
        skip_postgeneration_save = True
