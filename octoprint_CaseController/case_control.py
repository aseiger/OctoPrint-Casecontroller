import pigpio

FULL_OPEN = 37600
FULL_CLOSE = 36000
FAN_PIN = 18
SERVO_PIN = 19
CASE_LIGHT_PIN = 24
STATUS_LED_PIN = 23

class CaseController():
    def __init__(self):
        self.pi = pigpio.pi()

        ##~~ initialze the servo
        self.pi.set_mode(SERVO_PIN, pigpio.OUTPUT)
        self.pi.set_PWM_frequency(SERVO_PIN, 33)
        self.pi.set_PWM_range(SERVO_PIN, 40000)
        self.pi.set_PWM_dutycycle(SERVO_PIN, FULL_CLOSE)

        self.valve_position = 0

        ##~~ initialize the fan
        self.pi.set_mode(FAN_PIN, pigpio.OUTPUT)
        self.pi.write(FAN_PIN, 0)

        self.fan_state = 0

        ##~~ initialze the case light
        self.pi.set_mode(CASE_LIGHT_PIN, pigpio.OUTPUT)
        self.pi.write(CASE_LIGHT_PIN, 0)

        self.case_light_state = 0

        ##~~ initialize status LED
        self.pi.set_mode(STATUS_LED_PIN, pigpio.OUTPUT)
        self.pi.write(STATUS_LED_PIN, 0)

        self.status_led_state = 0

        ##~~ initialize the temperature tempSensor
        self.case_temperature = self.readTemp_C()

    def readTemp_C(self):
        temp_sensor_h = self.pi.i2c_open(1, 0x48)
        temp = self.pi.i2c_read_word_data(temp_sensor_h, 0x00)
        self.pi.i2c_close(temp_sensor_h)
        temphi = ((temp >> 8) & 0xFF) >> 4
        templo = temp & 0xFF
        tempC = float(templo) + float(temphi * 0.0625)
        self.case_temperature = tempC
        return(tempC)

    def setCaseLight(self, state):
        self.pi.write(CASE_LIGHT_PIN, state)
        self.case_light_state = state

    def setStatusLED(self, state):
        self.pi.write(STATUS_LED_PIN, state)
        self.status_led_state = state

    def setFan(self, state):
        self.pi.write(FAN_PIN, state)
        self.fan_state = state

    def setValve(self, flowRate):
        valve_range = FULL_CLOSE - FULL_OPEN
        percentage = (100.0 - float(flowRate))/100.0
        value = float(valve_range)*percentage + FULL_OPEN
        self.pi.set_PWM_dutycycle(SERVO_PIN, int(value))

if(__name__ == '__main__'):
    caseController = CaseController()
