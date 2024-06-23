import random
import time
import variabels

class CMDHandler:
    def __init__(self, espcom):
        self.com = espcom
    
    def xor_checksum(self,data):
        checksum = 0
        for byte in data:
            checksum ^= byte
        return checksum
    
    def custom_ljust(self, s, width, fillchar='@'):
        if len(s) >= width:
            return s
        return s + (fillchar * (width - len(s)))

    def decode_message(self,message):
        if message[0] != '#' or message[-1] != '#':
            raise ValueError("Message should start and end with '#'")

        source = message[1:18]
        command = message[18:22]
        payload = message[22:54].rstrip('@')
        received_checksum = int(message[54:56], 16)
        
        data_to_check = message[1:54]
        calculated_checksum = self.xor_checksum(data_to_check.encode('utf-8'))
        
        if received_checksum != calculated_checksum:
            raise ValueError("Checksum does not match")

        return source, command, payload

    def encode_message(self,source, command, payload):
        if len(source) != 17 or len(command) != 4:
            raise ValueError("Source must be 17 characters and command must be 4 characters")
        if len(payload) > 32:
            raise ValueError("Payload must not exceed 32 characters")

        padded_payload = self.custom_ljust(payload, 32, '@')
        data_to_check = source + command + padded_payload
        checksum = self.xor_checksum(data_to_check.encode('utf-8'))
        
        checksum_hex = '{:02x}'.format(checksum)
        message = f"*{source}{command}{padded_payload}{checksum_hex}*"
        
        return message
    
    def decode_sensor_data(self, payload):
        # Split the payload string into individual sensor values
        data_parts = payload.split('$')

        # Parse sensor values
        sensor_data = {
            'temperature': float(data_parts[0]),
            'humidity': float(data_parts[1]),
            'tvoc': int(data_parts[2])
        }

        # Check if lux value is present
        if len(data_parts) > 3:
            sensor_data['lux'] = float(data_parts[3])

        return sensor_data
    
    def encode_to_hex_string(self, values):
        if len(values) != 6:
            raise ValueError("Exactly six values are required")
        for value in values:
            if not (0 <= value <= 255):
                 raise ValueError("Values must be between 0 and 255")
    
        hex_string = "0x" + "".join(f"{value:02X}" for value in values)
        return hex_string
    
    def handle_command(self, source, command, payload):
        if command:
            if command == "RESP":
                print("RESPOSNE FROM SEARCH")
                print(payload)
                if payload not in variabels.mac_list:
                    variabels.mac_list.append(payload)
            if command == "HRBT":
                print ("HEARTBEAT RECIVIED")
                variabels.COMMAND_ACK = 1
            if command == "OKAY":
                print ("COMMAND ACK")
                variabels.COMMAND_ACK = 1
            if command == "NACK":
                print ("COMMAND NACK")
                variabels.COMMAND_ACK = 0
            if command == "BUSY":
                print ("LAMP BUSY")
                variabels.EXTEND_TIMER = 1
            if command == "SENS":
                print("SENS COMMAND")
                try:
                    variabels.SENS_PAYLOAD = self.decode_sensor_data(payload)   
                    variabels.COMMAND_ACK = 1
                except:
                    variabels.SENS_PAYLOAD = []
                    variabels.COMMAND_ACK = 0
                    
                
                
                
        
    
    

            
                
                
                
        
        
