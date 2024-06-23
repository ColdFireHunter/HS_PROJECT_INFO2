import random
import time

class CMDHandler:
    
    __added_source = ""
    
    def __init__(self, espcom, ledhandler, sensorcontrol, buzz):
        self.com = espcom
        self.led = ledhandler
        self.sensor = sensorcontrol
        self.buzzer = buzz
    
    def xor_checksum(self, data):
        """Calculate XOR checksum for a given data string."""
        checksum = 0
        for byte in data:
            checksum ^= byte
        return checksum
    
    def custom_ljust(self, s, width, fillchar='@'):
        """Left-justify a string with a specified fill character."""
        if len(s) >= width:
            return s
        return s + (fillchar * (width - len(s)))

    def decode_message(self, message):
        """Decode an incoming message and verify its checksum."""
        if message[0] != '*' or message[-1] != '*':
            raise ValueError("Message should start and end with '*'")

        source = message[1:18]
        command = message[18:22]
        payload = message[22:54].rstrip('@')
        received_checksum = int(message[54:56], 16)
        
        data_to_check = message[1:54]
        calculated_checksum = self.xor_checksum(data_to_check.encode('utf-8'))
        
        if received_checksum != calculated_checksum:
            raise ValueError("Checksum does not match")

        return source, command, payload

    def encode_message(self, destination, command, payload):
        """Encode a message with a checksum for sending."""
        if len(destination) != 17 or len(command) != 4:
            raise ValueError("Source must be 17 characters and command must be 4 characters")
        if len(payload) > 32:
            raise ValueError("Payload must not exceed 32 characters")

        padded_payload = self.custom_ljust(payload, 32, '@')
        data_to_check = destination + command + padded_payload
        checksum = self.xor_checksum(data_to_check.encode('utf-8'))
        
        checksum_hex = '{:02x}'.format(checksum)
        message = f"#{destination}{command}{padded_payload}{checksum_hex}#"
        
        return message
    
    def decode_sensor_data(self, payload):
        """Decode sensor data payload into a dictionary."""
        data_parts = payload.split('$')

        sensor_data = {
            'temperature': float(data_parts[0]),
            'humidity': float(data_parts[1]),
            'tvoc': int(data_parts[2])
        }

        if len(data_parts) > 3:
            sensor_data['lux'] = float(data_parts[3])

        return sensor_data
    
    def encode_to_hex_string(self, values):
        """Encode a list of values into a hex string."""
        if len(values) != 6:
            raise ValueError("Exactly six values are required")
        for value in values:
            if not (0 <= value <= 255):
                raise ValueError("Values must be between 0 and 255")
        
        hex_string = "0x" + "".join(f"{value:02X}" for value in values)
        return hex_string
    
    def handle_command(self, source, command, payload):
        """Handle incoming commands and execute corresponding actions."""
        if command:
            if command == "SRCH":
                # Handle search command
                buffer = self.encode_message(source, "RESP", self.com.get_mac())
                self.__added_source = self.com.get_mac()
                random_sleep_time = random.uniform(0.05, 0.5)  # Random delay between 50ms and 500ms
                time.sleep(random_sleep_time)
                self.com.send_message(buffer)
            elif command == "HRBT":
                # Handle heartbeat command
                if self.__added_source == source:
                    buffer = self.encode_message(self.__added_source, "HRBT", "")
                    self.com.send_message(buffer)
                    self.led.debug_toggle()
            elif command == "COLR":
                # Handle color change command
                if self.__added_source == source:
                    try:
                        self.led.set_leds(payload)
                        buffer = self.encode_message(self.__added_source, "OKAY", "")
                        self.com.send_message(buffer)
                    except:
                        buffer = self.encode_message(self.__added_source, "NACK", "")
                        self.com.send_message(buffer)
            elif command == "SENS":
                # Handle sensor data request command
                if self.__added_source == source:
                    payload_buffer = self.sensor.get_sensor_data()
                    buffer = self.encode_message(self.__added_source, "SENS", payload_buffer)
                    self.com.send_message(buffer)
            elif command == "TONE":
                # Handle tone command
                if self.__added_source == source:
                    if self.buzzer.is_song_available(payload):
                        buffer = self.encode_message(self.__added_source, "BUSY", "")
                        self.com.send_message(buffer)
                        self.buzzer.play_song(payload)
                        buffer = self.encode_message(self.__added_source, "OKAY", "")
                        self.com.send_message(buffer)
                    else:
                        buffer = self.encode_message(self.__added_source, "NACK", "")
                        self.com.send_message(buffer)
            else:
                buffer = self.encode_message(self.__added_source, "NACK", "")
                self.com.send_message(buffer)                
