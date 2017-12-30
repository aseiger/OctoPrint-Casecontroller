#!/usr/bin/python

import wiringpi
wiringpi.wiringPiSetupPhys();
wiringpi.pinMode(16, 1);
wiringpi.digitalWrite(16, 1);

