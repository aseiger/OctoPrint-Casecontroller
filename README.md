# OctoPrint-Casecontroller

This Plugin is intended to (eventually) be the be-all end-all of Octoprint hardware control plugins. The main function is a case thermal regulator, with the ability to link various temperature sensors to various activities, such as opening/closing valves, running pumps, etc.

## Setup

Install via the bundled [Plugin Manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager)
or manually using this URL:

    https://github.com/aseiger/OctoPrint-Casecontroller/archive/master.zip

There is a significant amount of hardware design that must be completed for this plugin to actually do something. Eventually, I will put together a PCB that has a bunch of IOs.

## Configuration

For now, the configuration is hard-coded because I'm the only one using it. Eventually, there will be a configuration allowing for connecting various logic blocks to IO actions
