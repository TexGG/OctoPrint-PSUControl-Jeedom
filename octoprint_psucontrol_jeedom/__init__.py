# coding=utf-8
# pyright: reportMissingModuleSource=false, reportMissingImports=false

from __future__ import absolute_import

__author__ = "Tex <tex@grosist.fr>"
__license__ = "GNU Affero General Public License http://www.gnu.org/licenses/agpl.html"
__copyright__ = "Copyright (C) 2022 Tex - Released under terms of the AGPLv3 License"

import octoprint.plugin
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class PSUControl_Jeedom(octoprint.plugin.StartupPlugin,
                         octoprint.plugin.RestartNeedingPlugin,
                         octoprint.plugin.TemplatePlugin,
                         octoprint.plugin.SettingsPlugin):

    def __init__(self):
        self.config = dict()

    def get_settings_defaults(self):
        return dict(
            address = '', # Jeedom base URL whitout trailing /
            api_key = '', # API key
            on_cmd_id = '', # ON command id
            off_cmd_id = '', # OFF command id
            status_cmd_id = '', # Status command id
            verify_certificate = True, # Shoud we check SSL certificate
        )

    def on_settings_initialized(self):
        self.reload_settings()

    def reload_settings(self):
        for k, v in self.get_settings_defaults().items():
            if type(v) == str:
                v = self._settings.get([k])
            elif type(v) == int:
                v = self._settings.get_int([k])
            elif type(v) == float:
                v = self._settings.get_float([k])
            elif type(v) == bool:
                v = self._settings.get_boolean([k])

            self.config[k] = v
            self._logger.debug("{}: {}".format(k, v))

    def on_startup(self, host, port):
        psucontrol_helpers = self._plugin_manager.get_helpers("psucontrol")
        if not psucontrol_helpers or 'register_plugin' not in psucontrol_helpers.keys():
            self._logger.warning("The version of PSUControl that is installed does not support plugin registration.")
            return

        self._logger.debug("Registering plugin with PSUControl")
        psucontrol_helpers['register_plugin'](self)

    def send(self, id_cmd):
        # Jeedom API URL
        url = self.config['address'] + '/core/api/jeeApi.php'
        # 4 parameters : plugin, apikey, type and id
        params = { "plugin" : "virtual", "apikey" : self.config['api_key'], "type" : "cmd", "id" : id_cmd }

        response = None
        verify_certificate = self.config['verify_certificate']
        try:
                # send command
                response = requests.post(url, params=params, verify=verify_certificate)
        except (
                requests.exceptions.InvalidURL,
                requests.exceptions.ConnectionError
        ):
            self._logger.error("Unable to communicate with server. Check settings.")
        except Exception:
            self._logger.exception("Exception while making API call")
        else:
            self._logger.debug("cmd={}, params={}, status_code={}, text={}".format(id_cmd, params, response.status_code, response.text))

            if response.status_code == 401:
                self._logger.warning("Server returned 401 Unauthorized. Check API key.")
                response = None
            elif response.status_code == 404:
                self._logger.warning("Server returned 404 Not Found. Check CMD ID.")
                response = None

        return response

    def change_psu_state(self, state):
        if state: # if state parameter, on/off mode
            if (state == 'on'): # on
                _cmd_id = self.config['on_cmd_id']
            else: # off
                _cmd_id = self.config['off_cmd_id']
        else: # toggle mode
            if self.get_psu_state(): # on
                _cmd_id = self.config['off_cmd_id']
            else: # off
                _cmd_id = self.config['on_cmd_id']

        self.send(_cmd_id)

    def turn_psu_on(self):
        self._logger.debug("Switching PSU On")
        self.change_psu_state('on')

    def turn_psu_off(self):
        self._logger.debug("Switching PSU Off")
        self.change_psu_state('off')

    def get_psu_state(self):
        _cmd_id = self.config['status_cmd_id']

        # get status
        response = self.send(_cmd_id)
        if not response:
            return False

        status = None
        try:
            status = (response.text == "1") # url response text equal "1" when PSU is ON
        except KeyError:
            pass

        if status == None:
            self._logger.error("Unable to determine status. Check settings.")
            status = False

        return status

    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
        self.reload_settings()

    def get_settings_version(self):
        return 1

    def on_settings_migrate(self, target, current=None):
        pass

    def get_template_configs(self):
        return [
            dict(type="settings", custom_bindings=False)
        ]

    def get_update_information(self):
        return dict(
            psucontrol_jeedom=dict(
                displayName="PSU Control - Jeedom",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="texgg",
                repo="OctoPrint-PSUControl-Jeedom",
                current=self._plugin_version,

                # update method: pip w/ dependency links
                pip="https://github.com/TexGG/OctoPrint-PSUControl-Jeedom/archive/{target_version}.zip"
            )
        )

__plugin_name__ = "PSU Control - Jeedom"
__plugin_pythoncompat__ = ">=3,<4"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = PSUControl_Jeedom()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
