/*
 * View model for OctoPrint-Casecontroller
 *
 * Author: Alexander Seiger
 * License: AGPLv3
 */
$(function() {
    function CasecontrollerViewModel(parameters) {
        var self = this;

        self.navigation = parameters[0];

        // assign the injected parameters, e.g.:
        // self.loginStateViewModel = parameters[0];
        // self.settingsViewModel = parameters[1];

        // TODO: Implement your plugin's view model here.

        self.caseTemp = ko.observable();
        self.caseTempStr = ko.observable();
        self.desiredCaseTemp = ko.observable();
        self.desiredCaseTempEdit = ko.observable();
        self.valvePosition = ko.observable();
        self.fanSpeed = ko.observable();
        self.supplyVoltage = ko.observable();
        self.supplyCurrent = ko.observable();
        self.supplyPower = ko.observable();
        self.caseLightState = ko.observable();
        self.machinePowerState = ko.observable();

        self.powerStr = ko.observable();

        self.valveFanStr = ko.observable();

        // every time the controller loop is run, this function is called.
        // it will receive all necessary data for displaying case control data

        self.onDataUpdaterPluginMessage = function(plugin, data) {
          if (plugin != "CaseController") {
            return;
          }

          //update all of the loop data info. There's lots of it...
          self.caseTemp(data.caseTemp);
          self.desiredCaseTemp(data.desiredCaseTemp);
          self.valvePosition(data.valvePosition);
          self.fanSpeed(data.fanSpeed);
          self.supplyVoltage(data.supplyVoltage);
          self.supplyCurrent(data.supplyCurrent);
          self.supplyPower(data.supplyPower);
          self.caseLightState(data.caseLightState);
          self.machinePowerState(data.machinePowerState);

          self.valveFanStr(_.sprintf("Fan: %.1f%% | Valve: %.1f%%", self.fanSpeed(), self.valvePosition()));

          self.caseTempStr(_.sprintf("Case: %.1f&deg;C | %.1f&deg;C", self.caseTemp(), self.desiredCaseTemp()));

          self.powerStr(_.sprintf("%.3fV %.3fA %.3fW", self.supplyVoltage(), self.supplyCurrent(), self.supplyPower()))
        }

        // called when the case light on button is pressed
        self.caseLightOnBtnCb = function() {
          $.ajax({
            url: API_BASEURL + "plugin/CaseController",
            type: "POST",
            dataType: "json",
            data: JSON.stringify({
              command: "caseLightOn"
            }),
            contentType: "application/json; charset=UTF-8",
            error: function (data, status) {
              var options = {
                title: "Case Light On Failed.",
                text: data.responseText,
                hide: true,
                buttons: {
                  sticker: false,
                  closer: true
                },
                type: "error"
              };

              new PNotify(options);
            }
          });
        }

        //called when the case light off button is pressed
        self.caseLightOffBtnCb = function() {
          $.ajax({
            url: API_BASEURL + "plugin/CaseController",
            type: "POST",
            dataType: "json",
            data: JSON.stringify({
              command: "caseLightOff"
            }),
            contentType: "application/json; charset=UTF-8",
            error: function (data, status) {
              var options = {
                title: "Case Light Off Failed.",
                text: data.responseText,
                hide: true,
                buttons: {
                  sticker: false,
                  closer: true
                },
                type: "error"
              };

              new PNotify(options);
            }
          });
        }

        // called when the machine on button is pressed
        self.machineOnBtnCb = function() {
          $.ajax({
            url: API_BASEURL + "plugin/CaseController",
            type: "POST",
            dataType: "json",
            data: JSON.stringify({
              command: "machineOn"
            }),
            contentType: "application/json; charset=UTF-8",
            error: function (data, status) {
              var options = {
                title: "Machine On Failed.",
                text: data.responseText,
                hide: true,
                buttons: {
                  sticker: false,
                  closer: true
                },
                type: "error"
              };

              new PNotify(options);
            }
          });
        }

        //called when the machine off button is pressed
        self.machineOffBtnCb = function() {
          $.ajax({
            url: API_BASEURL + "plugin/CaseController",
            type: "POST",
            dataType: "json",
            data: JSON.stringify({
              command: "machineOff"
            }),
            contentType: "application/json; charset=UTF-8",
            error: function (data, status) {
              var options = {
                title: "Machine Off Failed.",
                text: data.responseText,
                hide: true,
                buttons: {
                  sticker: false,
                  closer: true
                },
                type: "error"
              };

              new PNotify(options);
            }
          });
        }

        //called when the vent fan off button is pressed
        self.setDesiredCaseTempBtnCb = function() {
          //sanitize the input kagigger
          newValue = parseFloat(self.desiredCaseTempEdit());
          if(isNaN (newValue))
          {
            return;
          }

          $.ajax({
            url: API_BASEURL + "plugin/CaseController",
            type: "POST",
            dataType: "json",
            data: JSON.stringify({
              command: "setDesiredCaseTemp",
              temperature: newValue
            }),
            contentType: "application/json; charset=UTF-8",
            error: function (data, status) {
              var options = {
                title: "Set Desired Case Temp Failed.",
                text: data.responseText,
                hide: true,
                buttons: {
                  sticker: false,
                  closer: true
                },
                type: "error"
              };

              new PNotify(options);
            }
          });
        }
    }

    /* view model class, parameters for constructor, container to bind to
     * Please see http://docs.octoprint.org/en/master/plugins/viewmodels.html#registering-custom-viewmodels for more details
     * and a full list of the available options.
     */
    OCTOPRINT_VIEWMODELS.push({
        construct: CasecontrollerViewModel,
        // ViewModels your plugin depends on, e.g. loginStateViewModel, settingsViewModel, ...
        dependencies: ['navigationViewModel'],
        // Elements to bind to, e.g. #settings_plugin_CaseController, #tab_plugin_CaseController, ...
        elements: ['#navbar_plugin_CaseController', '#tab_plugin_CaseController']
    });
});
