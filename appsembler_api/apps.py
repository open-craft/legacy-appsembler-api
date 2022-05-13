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
                PluginURLs.NAMESPACE: u'',
                PluginURLs.REGEX: r'^courses/{}/discussion/forum/'.format(COURSE_ID_PATTERN),
                PluginURLs.RELATIVE_PATH: u'urls',
            }
        },
    }
