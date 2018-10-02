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
        self.fanGain = 25
        self.fanOff_value = 0
        self.fanMin_value = 10
        self.fanMax_value = 100
        self.fanSpeed = 0
        self.caseLightTimeout = RepeatedTimer(1, self.caseLightOff_Timeout)
        self.isLightTimeoutActive = 0
        self.fastCaseLightTimeout = RepeatedTimer(1, self.caseLightOff_FastTimeout)
        self.isfastLightTimeoutActive = 0
        self.lastZHeight = -1.0;

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

            # fan should only increase in speed after valve is all open
            self.fanSpeed = (i_error - (100/self.valveGain)) * self.fanGain
            if(self.fanSpeed <= 0):
                self.fanSpeed = 0.0;

            # based on if printing or not, adjust the min fan speed to ensure negative pressure
            if(self._printer.is_printing()):
                self.fanSpeed = self.sanitize_flowvals(self.fanSpeed + self.fanMin_value)
            else:
                self.fanSpeed = self.sanitize_flowvals(self.fanSpeed)
        else:
            self.valvePosition = 0.0

            # based on if printing or not, adjust the min fan speed to ensure negative pressure
            if(self._printer.is_printing()):
                self.fanSpeed = self.fanMin_value
            else:
                self.fanSpeed = 0

        self.c.setValve(self.valvePosition)
        self.c.setFan(self.fanSpeed)

        if(self.c.read_button()):
            if(self.c.case_light_state == 0):
                self.caseLightOn_Timeout()
            else:
                self.caseLightOff_Timeout()

        self._plugin_manager.send_plugin_message(self._identifier,
                                                 dict(
                                                      msgType="LoopData",
                                                      caseTemp=self.caseTemp,
                                                      desiredCaseTemp=self._settings.get(["desiredTemp"]),
                                                      valvePosition=self.valvePosition,
                                                      fanSpeed=self.fanSpeed,
                                                      supplyVoltage=self.supplyVoltage,
                                                      supplyCurrent=self.supplyCurrent,
                                                      supplyPower=self.supplyPower,
                                                      caseLightState=self.c.case_light_state,
                                                      machinePowerState=self.c.mpwr_state))

    def sanitize_flowvals(self, invar):
       if(invar < 0):
           invar = 0
       elif(invar > 100):
           invar = 100
       # invar = int(invar)
       return invar

    def caseLightOn_Timeout(self):
        #only allow manual light control if the fast light is inactive
        if(self.isfastLightTimeoutActive == 0):
            self.isLightTimeoutActive = 1
            self.c.setCaseLight(1)
            self.caseLightTimeout = RepeatedTimer(self._settings.get(["caseLightTimeout"]), self.caseLightOff_Timeout)
            self.caseLightTimeout.start()

    def caseLightOff_Timeout(self):
        #don't shut the light off on a fast light
        if(self.isfastLightTimeoutActive == 0):
            self.c.setCaseLight(0)

        self.caseLightTimeout.cancel()
        self.isLightTimeoutActive = 0

    def caseLightOff_FastTimeout(self):
        #don't shut the light out on a manual light
        if(self.isLightTimeoutActive == 0):
            self.c.setCaseLight(0)

        self.fastCaseLightTimeout.cancel()
        self.isfastLightTimeoutActive = 0

    def caseLightOn_FastTimeout(self):
        #only allow fast light control if manual control is inactive
        if(self.isLightTimeoutActive == 0):
            self.isfastLightTimeoutActive = 1
            self.c.setCaseLight(1)
            self.fastCaseLightTimeout = RepeatedTimer(self._settings.get(["caseLightFastTimeout"]), self.caseLightOff_FastTimeout)
            self.fastCaseLightTimeout.start()

    ##~~ EventHandlerPlugin mixin
    def on_event(self, event, payload):
        if(event == "Shutdown"):
            self.c.setStatusLED(0)
            self.c.setFan(0)
        elif(event == "CaptureStart"):
            self.caseLightOn_FastTimeout()
            self._logger.info("CaptureStart")
        elif(event == "PrintDone"):
            self.caseLightOn_FastTimeout()
            self._logger.info("PrintDone")
        elif(event == "CaptureDone"):
            self.caseLightOff_FastTimeout()
            self._logger.info("CaptureDone")
        elif(event == "CaptureFailed"):
            self.caseLightOff_FastTimeout()
            self._logger.info("CaptureFailed")
        elif(event == 'Home'):
            self.lastZHeight = -1.0;

    def caseLightBeforeZ(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):
        if(gcode and ((gcode =="G1") or (gcode == "G0"))):
            zIndex = cmd.find('Z')
            if(zIndex > 0):
                outString = "";
                while((cmd[zIndex] != ' ') and (cmd[zIndex] != '\n')):
                    zIndex = zIndex + 1
                    if(zIndex >= len(cmd)):
                        break
                    outString = outString + cmd[zIndex]

                # if printer is printing, set the new Z
                queuedZHeight = float(outString)
                if(self._printer.is_printing and (queuedZHeight != self.lastZHeight)):
                    self.lastZHeight = queuedZHeight
                    self.caseLightOn_FastTimeout()

                self._logger.info("Received {}".format(outString))
        return

    ##~~ StartupPlugin mixin
    def on_after_startup(self):
        self._logger.info("Starting Case Controller...")
        self.c.setStatusLED(1)
        self.c.setFan(self.fanMin_value)
        self.loopTimer = RepeatedTimer(0.25, self.mainLoop)
        self.loopTimer.start()
        return 0

    ##~~ SettingsPlugin mixin

    def get_settings_defaults(self):
        return dict(
            desiredTemp=40,
            caseLightTimeout=600,
            caseLightFastTimeout=5
        )

    def get_api_commands(self):
        return dict(
            caseLightOn=[],
            caseLightOff=[],
            machineOn=[],
            machineOff=[],
            setDesiredCaseTemp=["temperature"]
        )

    def on_api_command(self, command, data):
        import flask
        if command == "caseLightOn":
            self.caseLightOn_Timeout()
        elif command == "caseLightOff":
            self.caseLightOff_Timeout()
        elif command == "machineOn":
            if(self._printer.is_printing() == 0):
                self.c.setMPWR(1)
        elif command == "machineOff":
            if(self._printer.is_printing() == 0):
                self.c.setMPWR(0)
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
        "octoprint.plugin.softwareupdate.check_config": plugin.get_update_information,
        "octoprint.comm.protocol.gcode.queuing": plugin.caseLightBeforeZ
    }
