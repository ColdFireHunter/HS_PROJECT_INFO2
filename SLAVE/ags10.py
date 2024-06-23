import time

""" AGS10 module """

class AGS10:
    AGS10_I2CADDR_DEFAULT = 0x1A  # Default I2C address for the AGS10 sensor

    def __init__(self, i2c, address=AGS10_I2CADDR_DEFAULT):
        self._i2c = i2c
        self._address = address
        self._dbuf = bytearray(5)  # Buffer for storing sensor data
        self._rbuf = bytearray(5)  # Buffer for storing resistance data
        self._dbuf_read_time = 0  # Timestamp of the last data buffer read
        self._rbuf_read_time = 0  # Timestamp of the last resistance buffer read
        self._init_time = time.time()  # Initialization time
        self._validate = False  # CRC validation flag

    @property
    def status(self):
        # Reads and returns the status byte from the sensor
        self._read_to_dbuf()
        return self._dbuf[0]

    @property
    def is_ready(self):
        # Checks if the sensor is ready by evaluating the status byte
        return not (self.status & 0x01)

    @property
    def total_volatile_organic_compounds_ppb(self):
        # Reads and returns the total volatile organic compounds in ppb
        self._read_to_dbuf()
        if self._validate and self._calc_crc8(self._dbuf[0:4]) != self._dbuf[4]:
            raise AssertionError('CRC mismatch')
        return int.from_bytes(self._dbuf[1:4], 'big')

    @property
    def resistance_kohm(self):
        # Reads and returns the resistance in kOhms
        self._read_to_rbuf()
        if self._validate and self._calc_crc8(self._rbuf[0:4]) != self._rbuf[4]:
            raise AssertionError('CRC mismatch')
        return int.from_bytes(self._rbuf[0:4], 'big') * 0.1

    @property
    def version(self):
        # Reads and returns the version of the sensor
        buf = bytearray(5)
        self._i2c.readfrom_mem_into(self._address, 0x11, buf)
        return buf[3]

    @property
    def check_crc(self):
        # Property to get CRC validation flag
        return self._validate

    @check_crc.setter
    def check_crc(self, value):
        # Property to set CRC validation flag
        self._validate = value

    def zero_point_calibrate(self, kohm):
        # Calibrates the sensor to the zero point with a given resistance value in kOhms
        data_bytes = int.to_bytes(int(kohm / 0.1), 2, 'big')
        buf = [0, 0x0C, data_bytes[0], data_bytes[1]]
        crc = self._calc_crc8(buf)
        buf = [0, 0x0C, data_bytes[0], data_bytes[1], crc]
        self._i2c.writeto_mem(self._address, 0x01, bytearray(buf))

    def zero_point_factory_reset(self):
        # Resets the zero point calibration to factory settings
        buf = [0, 0x0C, 0xFF, 0xFF, 0x81]
        self._i2c.writeto_mem(self._address, 0x01, bytearray(buf))

    def update_address(self, new_addr):
        # Updates the I2C address of the sensor
        new_addr_inv = ~new_addr
        buf = [new_addr, new_addr_inv, new_addr, new_addr_inv]
        crc = self._calc_crc8(buf)
        buf = [new_addr, new_addr_inv, new_addr, new_addr_inv, crc]
        self._i2c.writeto_mem(self._address, 0x21, bytearray(buf))

    def _read_to_dbuf(self):
        # Reads data into the data buffer if the minimum time delay has passed
        if time.time() - self._dbuf_read_time < 2:
            # Minimum 1.5s delay is required between successive data acquisitions
            return
        # Read sensor data to buffer
        self._i2c.readfrom_into(self._address, self._dbuf, True)
        self._dbuf_read_time = time.time()

    def _read_to_rbuf(self):
        # Reads resistance data into the resistance buffer if the minimum time delay has passed
        if time.time() - self._rbuf_read_time < 2:
            # Minimum 1.5s delay is required between successive resistance reads
            return
        # Read sensor data to buffer
        self._i2c.readfrom_mem_into(self._address, 0x20, self._rbuf)
        self._rbuf_read_time = time.time()

    def _calc_crc8(self, data):
        # Calculates the CRC-8 checksum for a given data buffer
        crc = 0xFF
        for byte in data:
            crc ^= byte
            for i in range(8):
                crc = ((crc << 1) ^ 0x31) if crc & 0x80 else crc << 1
        return crc & 0xFF
