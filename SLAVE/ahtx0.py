import utime
from micropython import const

class AHT10:
    """Interface library for AHT10/AHT20 temperature+humidity sensors"""

    AHTX0_I2CADDR_DEFAULT = const(0x38)  # Default I2C address
    AHTX0_CMD_INITIALIZE = 0xE1  # Initialization command
    AHTX0_CMD_TRIGGER = const(0xAC)  # Trigger reading command
    AHTX0_CMD_SOFTRESET = const(0xBA)  # Soft reset command
    AHTX0_STATUS_BUSY = const(0x80)  # Status bit for busy
    AHTX0_STATUS_CALIBRATED = const(0x08)  # Status bit for calibrated

    def __init__(self, i2c, address=AHTX0_I2CADDR_DEFAULT):
        """Initialize the sensor with I2C interface and address"""
        utime.sleep_ms(20)  # 20ms delay to wake up the sensor
        self._i2c = i2c
        self._address = address
        self._buf = bytearray(6)
        self.reset()  # Perform a soft reset
        if not self.initialize():  # Initialize the sensor
            raise RuntimeError("Could not initialize")
        self._temp = None
        self._humidity = None

    def reset(self):
        """Perform a soft-reset of the AHT sensor"""
        self._buf[0] = self.AHTX0_CMD_SOFTRESET
        self._i2c.writeto(self._address, self._buf[0:1])
        utime.sleep_ms(20)  # 20ms delay to wake up after reset

    def initialize(self):
        """Ask the sensor to self-initialize. Returns True on success, False otherwise"""
        self._buf[0] = self.AHTX0_CMD_INITIALIZE
        self._buf[1] = 0x08
        self._buf[2] = 0x00
        self._i2c.writeto(self._address, self._buf[0:3])
        self._wait_for_idle()  # Wait for the sensor to be ready
        if not self.status & self.AHTX0_STATUS_CALIBRATED:
            return False
        return True

    @property
    def status(self):
        """Return the status byte from the sensor, see datasheet for details"""
        self._read_to_buffer()
        return self._buf[0]

    @property
    def relative_humidity(self):
        """Return the measured relative humidity in percent."""
        self._perform_measurement()  # Trigger a measurement
        self._humidity = (
            (self._buf[1] << 12) | (self._buf[2] << 4) | (self._buf[3] >> 4)
        )
        self._humidity = (self._humidity * 100) / 0x100000  # Convert to percentage
        return self._humidity

    @property
    def temperature(self):
        """Return the measured temperature in degrees Celsius."""
        self._perform_measurement()  # Trigger a measurement
        self._temp = ((self._buf[3] & 0xF) << 16) | (self._buf[4] << 8) | self._buf[5]
        self._temp = ((self._temp * 200.0) / 0x100000) - 50  # Convert to Celsius
        return self._temp

    def _read_to_buffer(self):
        """Read sensor data into the buffer"""
        self._i2c.readfrom_into(self._address, self._buf)

    def _trigger_measurement(self):
        """Internal function for triggering the sensor to read temperature and humidity"""
        self._buf[0] = self.AHTX0_CMD_TRIGGER
        self._buf[1] = 0x33
        self._buf[2] = 0x00
        self._i2c.writeto(self._address, self._buf[0:3])

    def _wait_for_idle(self):
        """Wait until the sensor can receive a new command"""
        while self.status & self.AHTX0_STATUS_BUSY:
            utime.sleep_ms(5)  # Check every 5ms

    def _perform_measurement(self):
        """Trigger measurement and read result into buffer"""
        self._trigger_measurement()
        self._wait_for_idle()  # Wait until the sensor is idle
        self._read_to_buffer()


class AHT20(AHT10):
    """Subclass for AHT20 sensor, inherits from AHT10 but with a different initialize command"""
    AHTX0_CMD_INITIALIZE = 0xBE  # Calibration command specific to AHT20
