from machine import UART, Timer
import time
import variabels
import button

class UARTtoPC:
    
    __lockout_command = 0
    
    def __init__(self, uart_num, baudrate, tx_pin, rx_pin, buttons):
        """
        Initializes the UARTtoPC class with UART settings and a timer.
        
        Args:
            uart_num (int): UART number to use.
            baudrate (int): Baudrate for UART communication.
            tx_pin (int): Transmit pin number.
            rx_pin (int): Receive pin number.
        """
        self.uart = UART(uart_num, baudrate=baudrate, tx=tx_pin, rx=rx_pin)
        self.command_timer = Timer(3)
        self.button_handler = button.ButtonHandler(buttons)
    
    def calculate_checksum(self, command):
        """
        Calculates the checksum for a given command.
        
        Args:
            command (str): Command string for which to calculate the checksum.
        
        Returns:
            str: Calculated checksum as a 3-digit string.
        """
        checksum = 0
        for char in command:
            checksum ^= ord(char)
        return f"{checksum:03}"
    
    def pad_payload(self, payload):
        """
        Pads the payload to ensure it is 32 characters long.
        
        Args:
            payload (str): The payload string to pad.
        
        Returns:
            str: Padded payload string.
        
        Raises:
            ValueError: If the payload exceeds 32 characters.
        """
        if len(payload) > 32:
            raise ValueError("Payload must be 32 characters or less.")
        return payload + '@' * (32 - len(payload))  
    
    def send_command(self, command, payload):
        """
        Sends a command with the payload via UART.
        
        Args:
            command (str): Command string (4 characters).
            payload (str): Payload string (up to 32 characters).
        
        Raises:
            ValueError: If the command is not 4 characters long.
        """
        if len(command) != 4:
            raise ValueError("Command must be 4 characters long.")
        padded_payload = self.pad_payload(payload)
        message = f"*{command}{padded_payload}"
        checksum = self.calculate_checksum(command + padded_payload)
        message_with_checksum = f"{message}{checksum}*"
        self.uart.write(message_with_checksum)
    
    def receive_command(self):
        """
        Receives and validates a command from UART.
        
        Returns:
            tuple: Command string and payload string.
        
        Raises:
            ValueError: If the message format is invalid or checksum does not match.
        """
        if self.uart.any():
            message = self.uart.read(41).decode('utf-8')
            if message[0] == '#' and message[-1] == '#':
                command = message[1:5]
                payload = message[5:37]
                received_checksum = message[37:40]
                calculated_checksum = self.calculate_checksum(command + payload)
                if received_checksum == calculated_checksum:
                    return command, payload.rstrip('@')
                else:
                    raise ValueError("Checksum does not match.")
            else:
                raise ValueError("Invalid message format.")
        return None, None
    
    def data_available(self):
        """
        Checks if data is available to read from UART.
        
        Returns:
            bool: True if data is available, False otherwise.
        """
        return self.uart.any()
    
    def decode_string_led(self, input_string):
        """
        Decodes an LED control string.
        
        Args:
            input_string (str): Input string in the format "XYYYZZZAAA..." (19 characters).
        
        Returns:
            tuple: First letter and list of integer values.
        
        Raises:
            ValueError: If the input string length is incorrect.
        """
        if len(input_string) != 19:
            raise ValueError("Input string length is incorrect")

        first_letter = input_string[0]
        blocks = [int(input_string[i:i+3]) for i in range(1, 19, 3)]
        
        return first_letter, blocks

    def encode_sensor_data(self, sensor_data):
        """
        Encodes sensor data into the format "temperature$humidity$tvoc$lux".
        
        Args:
            sensor_data (dict): Dictionary containing sensor readings.
        
        Returns:
            str: Encoded sensor data string.
        """
        temperature = sensor_data.get('temperature')
        humidity = sensor_data.get('humidity')
        tvoc = sensor_data.get('tvoc')
        lux = sensor_data.get('lux')
        
        encoded_string = f"{temperature}${humidity}${tvoc}${lux}"
        return encoded_string
    
    def decode_tone_string(self, input_string):
        """
        Parameters:
        input_string (str): The string to be decoded.
        
        Returns:
        tuple: A tuple containing the integer (first character) and the remaining string.
        
        Raises:
        ValueError: If the input string is not in the correct format or if the first character cannot be converted to an integer.
        """
        if not isinstance(input_string, str):
            raise ValueError("Input must be a string")

        if len(input_string) < 2:
            raise ValueError("Input string is too short")

        first_char = input_string[0]
        remaining_string = input_string[1:]

        try:
            first_char_int = int(first_char)
        except ValueError:
            raise ValueError("First character is not an integer")

        return first_char_int, remaining_string

    
    def __timer_callback(self, t):
        """
        Timer callback function to handle various send commands.
        
        Args:
            t (Timer): Timer instance.
        """
        if variabels.SEARCH_SEND == 1:
            variabels.SEARCH_SEND = 0
            if not variabels.mac_list == []:
                print(variabels.mac_list)
                counter = 0
                for i in variabels.mac_list:
                    command = "MAC" + str(counter)
                    payload = i
                    self.send_command(command, payload)
                    counter = counter + 1
                command = "OKAY"
                payload = ""
                self.send_command(command, payload) 
            else:
                command = "MACN"
                payload = ""
                self.send_command(command, payload)
        if variabels.HRBT_SEND == 1:
            variabels.HRBT_SEND = 0
            command = "NACK"
            payload = ""
            self.send_command(command, payload)
            print("HRBT WAS NOT ACK")
        if variabels.COLR_SEND == 1:
            variabels.COLR_SEND = 0
            command = "NACK"
            payload = ""
            self.send_command(command, payload)
            print("COLOR WAS NOT ACK")
        if variabels.SENS_SEND == 1:
            variabels.SENS_SEND = 0
            command = "NACK"
            payload = ""
            self.send_command(command, payload)
            print("SENS WAS NOT ACK")
        if variabels.TONE_SEND == 1:
            variabels.TONE_SEND = 0
            command = "NACK"
            payload = ""
            self.send_command(command, payload)
            print("TONE WAS NOT ACK")
            
        self.__lockout_command = 0            
        print("TIMER RANOUT LOCKOUT LIFTED")
    
    def handle_pc_command(self, command, payload):
        """
        Handles incoming commands from the PC.
        
        Args:
            command (str): Command string.
            payload (str): Payload string.
        """
        if command and self.__lockout_command == 0:
            if command == "SRCH" and payload == "":
                self.command_timer.init(period=2500, mode=Timer.ONE_SHOT, callback=self.__timer_callback)
                variabels.mac_list.clear()
                self.__lockout_command = 1
                variabels.SEARCH_SEND = 1
                variabels.SEND_ONCE = 0
                return
            if command == "HRBT":
                self.command_timer.init(period=2500, mode=Timer.ONE_SHOT, callback=self.__timer_callback)
                self.__lockout_command = 1
                variabels.NEEDED_MAC_INDEX = payload
                variabels.HRBT_SEND = 1
                variabels.SEND_ONCE = 0
                return
            if command == "COLR":
                self.command_timer.init(period=2500, mode=Timer.ONE_SHOT, callback=self.__timer_callback)
                try:
                    mac_index, led_values = self.decode_string_led(payload)
                    variabels.NEEDED_MAC_INDEX = mac_index
                    variabels.COLOR_PAYLOAD = led_values
                    variabels.COLR_SEND = 1
                    variabels.SEND_ONCE = 0
                    self.__lockout_command = 1
                except:
                    self.handle_pc_command(command, payload)
                    variabels.NEEDED_MAC_INDEX = 0
                    variabels.COLOR_PAYLOAD = []
                    variabels.COLR_SEND = 0
                    variabels.SEND_ONCE = 0
                    self.__lockout_command = 0
                return
            if command == "SENS":
                self.command_timer.init(period=2500, mode=Timer.ONE_SHOT, callback=self.__timer_callback)
                self.__lockout_command = 1
                variabels.NEEDED_MAC_INDEX = payload
                variabels.SENS_SEND = 1
                variabels.SEND_ONCE = 0
                return
            if command == "TONE":
                self.command_timer.init(period=2500, mode=Timer.ONE_SHOT, callback=self.__timer_callback)
                try:
                    mac_index, tone_to_play = self.decode_tone_string(payload)
                    variabels.NEEDED_MAC_INDEX = mac_index
                    variabels.TONE_PAYLOAD = tone_to_play
                    variabels.TONE_SEND = 1
                    variabels.SEND_ONCE = 0
                    self.__lockout_command = 1
                except:
                    variabels.NEEDED_MAC_INDEX = 0
                    variabels.TONE_PAYLOAD = ""
                    variabels.TONE_SEND = 0
                    variabels.SEND_ONCE = 0
                    self.__lockout_command = 0
                return
            if command == "RBUT" and payload == "":
                self.__lockout_command = 1
                command = "BUTS"
                payload = self.button_handler.check_button_states()
                self.send_command(command,payload)
                self.__lockout_command = 0
                
        if command and self.__lockout_command == 1:
            self.send_command("BUSY", "")

    def handle_pc_logic(self):
        """
        Handles the PC logic for various send commands and acknowledgments.
        """
        
        if variabels.EXTEND_TIMER == 1:
            variabels.EXTEND_TIMER = 0
            self.command_timer.deinit()
            self.command_timer.init(period=10000, mode=Timer.ONE_SHOT, callback=self.__timer_callback)
            print("TIME EXTENDED")
            command = "BUSY"
            payload = ""
            self.send_command(command, payload)
        if variabels.COMMAND_ACK == 1:
            if variabels.HRBT_SEND == 1:
                variabels.COMMAND_ACK = 0
                variabels.HRBT_SEND = 0
                variabels.SEND_ONCE = 0
                self.command_timer.deinit()
                self.__lockout_command = 0
                command = "OKAY"
                payload = ""
                self.send_command(command, payload)
                print("HRBT WAS ACK LOCKOUT LIFTED")
            if variabels.COLR_SEND == 1:
                variabels.COMMAND_ACK = 0
                variabels.COLR_SEND = 0
                variabels.SEND_ONCE = 0
                self.command_timer.deinit()
                self.__lockout_command = 0
                command = "OKAY"
                payload = ""
                self.send_command(command, payload)
                print("COLOR WAS ACK LOCKOUT LIFTED")
            if variabels.SENS_SEND == 1:
                variabels.COMMAND_ACK = 0
                variabels.SENS_SEND = 0
                variabels.SEND_ONCE = 0
                self.command_timer.deinit()
                self.__lockout_command = 0
                command = "SENS"
                payload = self.encode_sensor_data(variabels.SENS_PAYLOAD)
                self.send_command(command, payload)
                print("SENS WAS ACK LOCKOUT LIFTED")
            if variabels.TONE_SEND == 1:
                variabels.COMMAND_ACK = 0
                variabels.TONE_SEND = 0
                variabels.SEND_ONCE = 0
                self.command_timer.deinit()
                self.__lockout_command = 0
                command = "OKAY"
                payload = ""
                self.send_command(command, payload)
                print("TONE WAS ACK LOCKOUT LIFTED")
        
