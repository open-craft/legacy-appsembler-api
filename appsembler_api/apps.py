"""
appsembler_api Django application initialization.
"""

from django.apps import AppConfig

from openedx.core.djangoapps.plugins.constants import PluginSettings, PluginURLs, ProjectType, SettingsType


class AppsemblerApiConfig(AppConfig):
    """
    Configuration for the appsembler_api Django application.
    """

    name = 'appsembler_api'
    plugin_app = {
        PluginURLs.CONFIG: {
            ProjectType.LMS: {
                PluginURLs.NAMESPACE: u'appsembler_api',
                PluginURLs.REGEX: '^appsembler_api/v0/',
                PluginURLs.RELATIVE_PATH: u'urls',
            }
        },
    }
