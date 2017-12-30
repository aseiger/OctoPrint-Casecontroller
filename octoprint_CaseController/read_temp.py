import wiringpi

tempSensorID = wiringpi.wiringPiI2CSetup(0x48)


def readTemp():
    temp = 0
    temp = wiringpi.wiringPiI2CReadReg16(tempSensorID, 0x00)
    temphi = ((temp >> 8) & 0xFF) >> 4
    templo = temp & 0xFF
    tempC = float(templo) + float(temphi * 0.0625)
    tempF = ((tempC * 9.0)/5.0) + 32
    return {'tempC': tempC, 'tempF': tempF}

def fanOn():
    wiringpi.wiringPiSetupGpio()
    wiringpi.pinMode(18, 1)
    wiringpi.digitalWrite(18, 1)

def fanOff():
    wiringpi.wiringPiSetupGpio()
    wiringpi.pinMode(18, 1)
    wiringpi.digitalWrite(18, 0)
