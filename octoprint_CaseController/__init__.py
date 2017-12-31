# coding=utf-8
from __future__ import absolute_import

### (Don't forget to remove me)
# This is a basic skeleton for your plugin's __init__.py. You probably want to adjust the class name of your plugin
# as well as the plugin mixins it's subclassing from. This is really just a basic skeleton to get you started,
# defining your plugin as a template plugin, settings and asset plugin. Feel free to add or remove mixins
# as necessary.
#
# Take a look at the documentation on what other plugin mixins are available.

import octoprint.plugin
from octoprint.util import RepeatedTimer
from .case_control import CaseController

class CasecontrollerPlugin(octoprint.plugin.StartupPlugin,
                           octoprint.plugin.SettingsPlugin,
                           octoprint.plugin.AssetPlugin,
                           octoprint.plugin.EventHandlerPlugin,
                           octoprint.plugin.TemplatePlugin,
                           octoprint.plugin.SimpleApiPlugin):

    def __init__(self):
        self.c = CaseController()
        self.valvePosition = 0
        self.caseTemp = self.c.readTemp_C()
        self.valveGain = 50

    ##~~ The Main Control Loop
    def mainLoop(self):
        self.caseTemp = self.c.readTemp_C()
        i_error = self.caseTemp - self._settings.get(["desiredTemp"])
        if(i_error > 0):
            self.valvePosition = i_error * self.valveGain
            self.valvePosition = self.sanitize_flowvals(self.valvePosition)

        self.c.setValve(self.valvePosition)

        # self._logger.info(self.caseTemp)
        self._plugin_manager.send_plugin_message(self._identifier,
                                                 dict(
                                                      caseTemp=self.caseTemp,
                                                      valvePosition=self.valvePosition))

    def sanitize_flowvals(self, invar):
       if(invar < 0):
           invar = 0
       elif(invar > 100):
           invar = 100
       # invar = int(invar)
       return invar

    ##~~ EventHandlerPlugin mixin
    def on_event(self, event, payload):
        if(event == "PrintStarted"):
            self.c.setFan(1)
        elif(event == "Shutdown"):
            self.c.setFan(0)

    ##~~ StartupPlugin mixin
    def on_after_startup(self):
        self._logger.info("Starting Case Controller...")
        self.c.setStatusLED(1)
        self.c.setFan(1)

        self.loopTimer = RepeatedTimer(0.25, self.mainLoop)
        self.loopTimer.start()
        return 0

    ##~~ SettingsPlugin mixin

    def get_settings_defaults(self):
        return dict(
            desiredTemp=40
        )

    def get_api_commands(self):
        return dict(
            caseLightOn=[],
            caseLightOff=[],
            ventFanOn=[],
            ventFanOff=[]
        )

    def on_api_command(self, command, data):
        import flask
        if command == "caseLightOn":
            self.c.setCaseLight(1)
        elif command == "caseLightOff":
            self.c.setCaseLight(0)
        elif command == "ventFanOn":
            self.c.setFan(1)
        elif command == "ventFanOff":
            self.c.setFan(0)

    ##~~ AssetPlugin mixin

    def get_assets(self):
        # Define your plugin's asset files to automatically include in the
        # core UI here.
        return dict(
            js=["js/CaseController.js"],
            css=["css/CaseController.css"],
            less=["less/CaseController.less"]
        )

    ##~~ Softwareupdate hook

    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://github.com/foosel/OctoPrint/wiki/Plugin:-Software-Update
        # for details.
        return dict(
            CaseController=dict(
                displayName="Casecontroller Plugin",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="aseiger",
                repo="OctoPrint-Casecontroller",
                current=self._plugin_version,

                # update method: pip
                pip="https://github.com/aseiger/OctoPrint-Casecontroller/archive/{target_version}.zip"
            )
        )


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "CaseController"

def __plugin_load__():
    plugin = CasecontrollerPlugin()

    global __plugin_implementation__
    __plugin_implementation__ = plugin

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": plugin.get_update_information
    }
