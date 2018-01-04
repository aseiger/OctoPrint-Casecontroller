# coding=utf-8
from __future__ import absolute_import

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
        self.supplyVoltage = self.c.readVoltage()
        self.supplyCurrent = self.c.readCurrent()
        self.supplyPower = self.supplyVoltage * self.supplyCurrent
        i_error = self.caseTemp - self._settings.get(["desiredTemp"])
        if(i_error > 0):
            self.valvePosition = i_error * self.valveGain
            self.valvePosition = self.sanitize_flowvals(self.valvePosition)
        else:
            self.valvePosition = 0.0

        self.c.setValve(self.valvePosition)

        # self._logger.info('Voltage: {:.3f}V Current: {:.3f}A Power: {:.3f}W'.format(self.supplyVoltage, self.supplyCurrent, self.supplyPower))

        # self._logger.info(self.caseTemp)
        self._plugin_manager.send_plugin_message(self._identifier,
                                                 dict(
                                                      caseTemp=self.caseTemp,
                                                      desiredCaseTemp=self._settings.get(["desiredTemp"]),
                                                      valvePosition=self.valvePosition,
                                                      supplyVoltage=self.supplyVoltage,
                                                      supplyCurrent=self.supplyCurrent,
                                                      supplyPower=self.supplyPower))

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
            self.c.setStatusLED(0)
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
            ventFanOff=[],
            setDesiredCaseTemp=["temperature"]
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
        elif command == "setDesiredCaseTemp":
            self._settings.set(["desiredTemp"], float(data["temperature"]))
            self._settings.save()

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

__plugin_name__ = "CaseController"

def __plugin_load__():
    plugin = CasecontrollerPlugin()

    global __plugin_implementation__
    __plugin_implementation__ = plugin

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": plugin.get_update_information
    }
