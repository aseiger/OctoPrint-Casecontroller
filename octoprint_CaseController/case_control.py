import pigpio
from time import sleep

FULL_OPEN = 37600
FULL_CLOSE = 36150
FAN_PIN = 18
SERVO_PIN = 19
CASE_LIGHT_PIN = 24
STATUS_LED_PIN = 23

ADS1115_CONVERSIONDELAY = 130
ADS1015_REG_POINTER_MASK = 0x03
ADS1015_REG_POINTER_CONVERT = 0x00
ADS1015_REG_POINTER_CONFIG = 0x01
ADS1015_REG_POINTER_LOWTHRESH = 0x02
ADS1015_REG_POINTER_HITHRESH = 0x03

ADS1015_REG_CONFIG_OS_MASK      = 0x8000
ADS1015_REG_CONFIG_OS_SINGLE    = 0x8000  # Write: Set to start a single-conversion
ADS1015_REG_CONFIG_OS_BUSY      = 0x0000  # Read: Bit =  0 when conversion is in progress
ADS1015_REG_CONFIG_OS_NOTBUSY   = 0x8000  # Read: Bit =  1 when device is not performing a conversion

ADS1015_REG_CONFIG_MUX_MASK     = 0x7000
ADS1015_REG_CONFIG_MUX_DIFF_0_1 = 0x0000  # Differential P =  AIN0, N =  AIN1 = default
ADS1015_REG_CONFIG_MUX_DIFF_0_3 = 0x1000  # Differential P =  AIN0, N =  AIN3
ADS1015_REG_CONFIG_MUX_DIFF_1_3 = 0x2000  # Differential P =  AIN1, N =  AIN3
ADS1015_REG_CONFIG_MUX_DIFF_2_3 = 0x3000  # Differential P =  AIN2, N =  AIN3
ADS1015_REG_CONFIG_MUX_SINGLE_0 = 0x4000  # Single-ended AIN0
ADS1015_REG_CONFIG_MUX_SINGLE_1 = 0x5000  # Single-ended AIN1
ADS1015_REG_CONFIG_MUX_SINGLE_2 = 0x6000  # Single-ended AIN2
ADS1015_REG_CONFIG_MUX_SINGLE_3 = 0x7000  # Single-ended AIN3

ADS1015_REG_CONFIG_PGA_MASK     = 0x0E00
ADS1015_REG_CONFIG_PGA_6_144V   = 0x0000  # +/-6.144V range =  Gain 2/3
ADS1015_REG_CONFIG_PGA_4_096V   = 0x0200  # +/-4.096V range =  Gain 1
ADS1015_REG_CONFIG_PGA_2_048V   = 0x0400  # +/-2.048V range =  Gain 2 = default
ADS1015_REG_CONFIG_PGA_1_024V   = 0x0600  # +/-1.024V range =  Gain 4
ADS1015_REG_CONFIG_PGA_0_512V   = 0x0800  # +/-0.512V range =  Gain 8
ADS1015_REG_CONFIG_PGA_0_256V   = 0x0A00  # +/-0.256V range =  Gain 16

ADS1015_REG_CONFIG_MODE_MASK    = 0x0100
ADS1015_REG_CONFIG_MODE_CONTIN  = 0x0000  # Continuous conversion mode
ADS1015_REG_CONFIG_MODE_SINGLE  = 0x0100  # Power-down single-shot mode (default

ADS1015_REG_CONFIG_DR_MASK      = 0x00E0
ADS1015_REG_CONFIG_DR_8SPS    = 0x0000  # 128 samples per second
ADS1015_REG_CONFIG_DR_16SPS    = 0x0020  # 250 samples per second
ADS1015_REG_CONFIG_DR_32SPS    = 0x0040  # 490 samples per second
ADS1015_REG_CONFIG_DR_64SPS    = 0x0060  # 920 samples per second
ADS1015_REG_CONFIG_DR_128SPS   = 0x0080  # 1600 samples per second = default
ADS1015_REG_CONFIG_DR_250SPS   = 0x00A0  # 2400 samples per second
ADS1015_REG_CONFIG_DR_475SPS   = 0x00C0  # 3300 samples per second
ADS1015_REG_CONFIG_DR_860SPS   = 0x00E0  # 3300 samples per second

ADS1015_REG_CONFIG_CMODE_MASK   = 0x0010
ADS1015_REG_CONFIG_CMODE_TRAD   = 0x0000  # Traditional comparator with hysteresis = default
ADS1015_REG_CONFIG_CMODE_WINDOW = 0x0010  # Window comparator

ADS1015_REG_CONFIG_CPOL_MASK    = 0x0008
ADS1015_REG_CONFIG_CPOL_ACTVLOW = 0x0000  # ALERT/RDY pin is low when active = default
ADS1015_REG_CONFIG_CPOL_ACTVHI  = 0x0008  # ALERT/RDY pin is high when active

ADS1015_REG_CONFIG_CLAT_MASK    = 0x0004  # Determines if ALERT/RDY pin latches once asserted
ADS1015_REG_CONFIG_CLAT_NONLAT  = 0x0000  # Non-latching comparator = default
ADS1015_REG_CONFIG_CLAT_LATCH   = 0x0004  # Latching comparator

ADS1015_REG_CONFIG_CQUE_MASK    = 0x0003
ADS1015_REG_CONFIG_CQUE_1CONV   = 0x0000  # Assert ALERT/RDY after one conversions
ADS1015_REG_CONFIG_CQUE_2CONV   = 0x0001  # Assert ALERT/RDY after two conversions
ADS1015_REG_CONFIG_CQUE_4CONV   = 0x0002  # Assert ALERT/RDY after four conversions
ADS1015_REG_CONFIG_CQUE_NONE    = 0x0003  # Disable the comparator and put ALERT/RDY in high state = default

class CaseController():
    def __init__(self):
        self.pi = pigpio.pi()

        ##~~ initialze the servo
        self.full_close = FULL_CLOSE
        self.full_open = FULL_OPEN
        self.pi.set_mode(SERVO_PIN, pigpio.OUTPUT)
        self.pi.set_PWM_frequency(SERVO_PIN, 33)
        self.pi.set_PWM_range(SERVO_PIN, 40000)
        self.pi.set_PWM_dutycycle(SERVO_PIN, self.full_close)

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

        ##~~ initialize the power sensor
        self.current_offset_v = 0.65
        self.voltage = self.readVoltage()
        self.current = self.readCurrent()

    def readTemp_C(self):
        temp_sensor_h = self.pi.i2c_open(1, 0x48)
        temp = self.pi.i2c_read_word_data(temp_sensor_h, 0x00)
        self.pi.i2c_close(temp_sensor_h)
        temphi = ((temp >> 8) & 0xFF) >> 4
        templo = temp & 0xFF
        tempC = float(templo) + float(temphi * 0.0625)
        self.case_temperature = tempC
        return(tempC)

    def byteSwapWord(self, wordIn):
        return(((wordIn & 0xFF) << 8) + ((wordIn & 0xFF00) >> 8))

    def readVoltage(self):
        config = ADS1015_REG_CONFIG_CQUE_NONE
        config |= ADS1015_REG_CONFIG_CLAT_NONLAT
        config |= ADS1015_REG_CONFIG_CPOL_ACTVLOW
        config |= ADS1015_REG_CONFIG_CMODE_TRAD
        config |= ADS1015_REG_CONFIG_MODE_SINGLE

        config |= ADS1015_REG_CONFIG_PGA_6_144V
        config |= ADS1015_REG_CONFIG_MUX_SINGLE_1
        config |= ADS1015_REG_CONFIG_DR_128SPS
        config |= ADS1015_REG_CONFIG_OS_SINGLE
        adc_sensor_h = self.pi.i2c_open(1, 0x49)
        # write the configuration to start the conversion
        self.pi.i2c_write_word_data(adc_sensor_h, ADS1015_REG_POINTER_CONFIG, self.byteSwapWord(config))
        # wait for the conversion to finish by monitoring the MSB
        regval = self.byteSwapWord(self.pi.i2c_read_word_data(adc_sensor_h, ADS1015_REG_POINTER_CONFIG))
        while((regval & 0x8000) != 0x8000):
            regval = self.byteSwapWord(self.pi.i2c_read_word_data(adc_sensor_h, ADS1015_REG_POINTER_CONFIG))
            # print('%04x' % (regval & 0x8000))
            sleep(0.001)
        #read the conversion
        raw_value = self.pi.i2c_read_word_data(adc_sensor_h, ADS1015_REG_POINTER_CONVERT)
        self.pi.i2c_close(adc_sensor_h)
        raw_value = self.byteSwapWord(raw_value)
        raw_volts = ((raw_value * 12.288) / 65536)
        true_volts = raw_volts / 0.32
        return(true_volts)

    def readCurrent(self):
        config = ADS1015_REG_CONFIG_CQUE_NONE
        config |= ADS1015_REG_CONFIG_CLAT_NONLAT
        config |= ADS1015_REG_CONFIG_CPOL_ACTVLOW
        config |= ADS1015_REG_CONFIG_CMODE_TRAD
        config |= ADS1015_REG_CONFIG_MODE_SINGLE

        config |= ADS1015_REG_CONFIG_PGA_6_144V
        config |= ADS1015_REG_CONFIG_MUX_SINGLE_0
        config |= ADS1015_REG_CONFIG_DR_128SPS
        config |= ADS1015_REG_CONFIG_OS_SINGLE
        adc_sensor_h = self.pi.i2c_open(1, 0x49)
        # write the configuration to start the conversion
        self.pi.i2c_write_word_data(adc_sensor_h, ADS1015_REG_POINTER_CONFIG, self.byteSwapWord(config))
        # wait for the conversion to finish by monitoring the MSB
        regval = self.byteSwapWord(self.pi.i2c_read_word_data(adc_sensor_h, ADS1015_REG_POINTER_CONFIG))
        while((regval & 0x8000) != 0x8000):
            regval = self.byteSwapWord(self.pi.i2c_read_word_data(adc_sensor_h, ADS1015_REG_POINTER_CONFIG))
            # print('%04x' % (regval & 0x8000))
            sleep(0.001)
        #read the conversion
        raw_value = self.pi.i2c_read_word_data(adc_sensor_h, ADS1015_REG_POINTER_CONVERT)
        self.pi.i2c_close(adc_sensor_h)
        raw_value = self.byteSwapWord(raw_value)
        raw_volts = ((raw_value * 12.288) / 65536)
        adjusted_volts = raw_volts - self.current_offset_v;
        current = adjusted_volts / 0.04
        if(current < 0.04):
            return(0.0)
        else:
            return(current)

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
        valve_range = self.full_close - self.full_open
        percentage = (100.0 - float(flowRate))/100.0
        value = float(valve_range)*percentage + self.full_open
        self.pi.set_PWM_dutycycle(SERVO_PIN, int(value))

if(__name__ == '__main__'):
    c = CaseController()
    c.setCaseLight(1)
    while(1):
        print('Voltage: {:.3f} Current: {:.3f} Temp: {:.3f}'.format(c.readVoltage(), c.readCurrent(), c.readTemp_C()))
