import time
from machine import I2C

class LTR308ALS:
    # I2C address
    I2C_ADDRESS = 0x53

    # Register addresses
    REG_MAIN_CTRL = 0x00
    REG_ALS_MEAS_RATE = 0x04
    REG_ALS_GAIN = 0x05
    REG_PART_ID = 0x06
    REG_MAIN_STATUS = 0x07
    REG_ALS_DATA_0 = 0x0D
    REG_ALS_DATA_1 = 0x0E
    REG_ALS_DATA_2 = 0x0F

    # Main Control register settings
    ALS_ACTIVE = 0x02

    def __init__(self, i2c, address=I2C_ADDRESS):
        self.i2c = i2c
        self.address = address
        self.init_sensor()

    def init_sensor(self):
        # Activate ALS
        self.i2c.writeto_mem(self.address, self.REG_MAIN_CTRL, bytearray([self.ALS_ACTIVE]))
        time.sleep(0.01)  # Wait for the sensor to initialize

    def read_ambient_light(self):
        # Read the ALS data registers
        data0 = self.i2c.readfrom_mem(self.address, self.REG_ALS_DATA_0, 1)[0]
        data1 = self.i2c.readfrom_mem(self.address, self.REG_ALS_DATA_1, 1)[0]
        data2 = self.i2c.readfrom_mem(self.address, self.REG_ALS_DATA_2, 1)[0]

        # Combine the data bytes into a single value
        als_data = (data2 << 16) | (data1 << 8) | data0

        return als_data

    def set_als_meas_rate(self, resolution, rate):
        # Set the ALS measurement rate and resolution
        meas_rate = (resolution << 4) | rate
        self.i2c.writeto_mem(self.address, self.REG_ALS_MEAS_RATE, bytearray([meas_rate]))

    def set_als_gain(self, gain):
        # Set the ALS gain
        self.i2c.writeto_mem(self.address, self.REG_ALS_GAIN, bytearray([gain]))

    def get_part_id(self):
        # Read the part ID
        part_id = self.i2c.readfrom_mem(self.address, self.REG_PART_ID, 1)[0]
        return part_id

    def new_data_available(self):
        # Read the main status register to check if new data is available
        status = self.i2c.readfrom_mem(self.address, self.REG_MAIN_STATUS, 1)[0]
        # Check the ALS Data Status bit (bit 4)
        return (status & 0x08) != 0

    def read_status(self):
        # Read the status register
        status = self.i2c.readfrom_mem(self.address, self.REG_MAIN_STATUS, 1)[0]
        return status

    def calculate_lux(self, als_data, gain, integration_time_ms):
        # Calculate lux from ALS data, gain, and integration time
        # Constants based on datasheet information
        if gain == 0x00:
            gain_factor = 1.0
        elif gain == 0x01:
            gain_factor = 3.0
        elif gain == 0x02:
            gain_factor = 6.0
        elif gain == 0x03:
            gain_factor = 9.0
        elif gain == 0x04:
            gain_factor = 18.0
        else:
            gain_factor = 1.0  # Default to 1x gain

        if integration_time_ms == 100:
            time_factor = 1.0
        elif integration_time_ms == 50:
            time_factor = 0.5
        elif integration_time_ms == 200:
            time_factor = 2.0
        elif integration_time_ms == 400:
            time_factor = 4.0
        elif integration_time_ms == 150:
            time_factor = 1.5
        elif integration_time_ms == 250:
            time_factor = 2.5
        elif integration_time_ms == 300:
            time_factor = 3.0
        elif integration_time_ms == 350:
            time_factor = 3.5
        else:
            time_factor = 1.0  # Default to 100ms

        lux = (als_data * 0.25) / (gain_factor * time_factor)
        return lux

    def read_lux(self):
        # Read ALS data
        als_data = self.read_ambient_light()

        # Read gain setting
        gain = self.i2c.readfrom_mem(self.address, self.REG_ALS_GAIN, 1)[0]

        # Read measurement rate setting
        meas_rate = self.i2c.readfrom_mem(self.address, self.REG_ALS_MEAS_RATE, 1)[0]
        integration_time_ms = (meas_rate >> 4) & 0x07
        # Map integration time setting to actual milliseconds
        integration_time_mapping = {
            0: 100,
            1: 50,
            2: 200,
            3: 400,
            4: 150,
            5: 250,
            6: 300,
            7: 350
        }
        integration_time_ms = integration_time_mapping.get(integration_time_ms, 100)

        # Calculate lux
        lux = self.calculate_lux(als_data, gain, integration_time_ms)
        return lux
