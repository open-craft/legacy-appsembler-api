"""
These settings are here to use during tests, because django requires them.

In a real-world use case, apps in this project are installed into other
Django applications, so these settings will not be used.
"""

from lms.envs.tutor.development import *  # pylint: disable=wildcard-import

REGISTRATION_CODE_LENGTH = 13

ROOT_URLCONF = "shoppingcart.urls"

INSTALLED_APPS.remove("debug_toolbar")  # pylint: disable=undefined-variable
MIDDLEWARE.remove("debug_toolbar.middleware.DebugToolbarMiddleware")  # pylint: disable=undefined-variable
