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

        // every time the controller loop is run, this function is called.
        // it will receive all necessary data for displaying case control data

        self.onDataUpdaterPluginMessage = function(plugin, data) {
          if (plugin != "CaseController") {
            return;
          }

          self.caseTemp(_.sprintf("Case: %.1f&deg;C", data.caseTemp));
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

        // called when the vent fan on button is pressed
        self.ventFanOnBtnCb = function() {
          $.ajax({
            url: API_BASEURL + "plugin/CaseController",
            type: "POST",
            dataType: "json",
            data: JSON.stringify({
              command: "ventFanOn"
            }),
            contentType: "application/json; charset=UTF-8",
            error: function (data, status) {
              var options = {
                title: "Vent Fan On Failed.",
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
        self.ventFanOffBtnCb = function() {
          $.ajax({
            url: API_BASEURL + "plugin/CaseController",
            type: "POST",
            dataType: "json",
            data: JSON.stringify({
              command: "ventFanOff"
            }),
            contentType: "application/json; charset=UTF-8",
            error: function (data, status) {
              var options = {
                title: "Vent Fan Off Failed.",
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
