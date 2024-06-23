import ahtx0
import ltr308
from ags10 import AGS10
from machine import I2C, Pin

class SENSOR_CONTROL:
    def __init__(self):
        # Initialize I2C bus with specified pins and frequency
        self.sensor_i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=100000)

        # Initialize AHT20 sensor for temperature and humidity
        self.aht20_sensor = ahtx0.AHT20(self.sensor_i2c)
        # Initialize AGS10 sensor for air quality (TVOC)
        self.ags10_sensor = AGS10(self.sensor_i2c)
        # Initialize LTR308 sensor for ambient light
        self.ltr_sensor = ltr308.LTR308ALS(self.sensor_i2c)

        # Configure LTR308 sensor settings
        self.ltr_sensor.set_als_meas_rate(0x02, 0x02)  # Set ALS measurement rate
        self.ltr_sensor.set_als_gain(0x01)  # Set ALS gain

    def get_sensor_data(self):
        """Read data from all sensors and generate a payload string"""
        # Read temperature from AHT20 sensor
        temperature = self.aht20_sensor.temperature
        # Read humidity from AHT20 sensor
        humidity = self.aht20_sensor.relative_humidity

        # Read TVOC from AGS10 sensor
        tvoc = self.ags10_sensor.total_volatile_organic_compounds_ppb

        # Read lux (ambient light) from LTR308 sensor if new data is available
        if self.ltr_sensor.new_data_available():
            lux = self.ltr_sensor.read_lux()
        else:
            lux = None

        # Generate payload string with sensor data
        payload = f"{temperature:.2f}${humidity:.2f}${tvoc}"
        if lux is not None:
            payload += f"${lux}"

        return payload  # Return the payload string
