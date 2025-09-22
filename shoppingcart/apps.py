"""
appsembler_api Django application initialization.
"""

from django.apps import AppConfig
from openedx.core.djangoapps.plugins.constants import PluginURLs, ProjectType


class AppsemblerApiConfig(AppConfig):
    """
    Configuration for the appsembler_api Django application.
    """

    name = 'shoppingcart'
    plugin_app = {
        PluginURLs.CONFIG: {
            ProjectType.LMS: {
                PluginURLs.NAMESPACE: 'appsembler_api',
                PluginURLs.REGEX: '^appsembler_api/v0/',
                PluginURLs.RELATIVE_PATH: 'urls',
            }
        },
    }
