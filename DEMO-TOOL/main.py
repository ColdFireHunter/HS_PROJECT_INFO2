import serial
import serial.tools.list_ports
import os

class SerialDeviceManager:
    def __init__(self):
        self.serial_conn = None
        self.mac_addresses = []

    @staticmethod
    def list_serial_ports():
        """List available serial ports with descriptions."""
        ports = serial.tools.list_ports.comports()
        return [(port.device, port.description) for port in ports]

    def select_serial_port(self):
        """Prompt the user to select a serial port by index."""
        ports = self.list_serial_ports()
        if not ports:
            print("No serial ports found.")
            return None
        for idx, (port, desc) in enumerate(ports):
            print(f"{idx}: {port} ({desc})")
        selection = int(input("Select a serial port by index: "))
        self.serial_conn = serial.Serial(ports[selection][0], 115200, timeout=1)

    @staticmethod
    def calculate_checksum(data):
        """Calculate a 3-digit XOR checksum for the given data."""
        checksum = 0
        for char in data:
            checksum ^= ord(char)
        return f"{checksum:03}"

    def format_command(self, command, payload):
        """Format the command with the payload and checksum."""
        payload = (payload + "@" * 32)[:32]
        data = command + payload
        checksum = self.calculate_checksum(data)
        return f"#{data}{checksum}#"

    def decode_response(self, response):
        """Decode the response from the device."""
        if not (response.startswith("*") and response.endswith("*")):
            return None, None, False
        response = response.strip("*")
        command = response[:4]
        payload = response[4:36]
        received_checksum = response[36:39]
        data = command + payload
        calculated_checksum = self.calculate_checksum(data)
        return command, payload, received_checksum == calculated_checksum

    @staticmethod
    def decode_sensor_payload(payload):
        """Decode and print the sensor payload."""
        buffer = payload.strip("@")
        values = buffer.split("$")
        if len(values) == 4:
            try:
                temperature = float(values[0])
                humidity = float(values[1])
                tvoc = float(values[2])
                lux = float(values[3])
                print(f"Temperature: {temperature:.2f} °C")
                print(f"Humidity: {humidity:.2f} %")
                print(f"TVOC: {tvoc:.2f} ppb")
                print(f"LUX: {lux:.2f} lux")
            except ValueError:
                print("Error decoding sensor values.")
        else:
            print("Invalid sensor payload format.")

    @staticmethod
    def decode_button_payload(payload):
        """Decode and print the button states payload."""
        buffer = payload.strip("@")
        values = buffer.split("$")
        if len(values) == 4:
            try:
                state1 = int(values[0])
                state2 = int(values[1])
                state3 = int(values[2])
                state4 = int(values[3])
                print(f"Button States:")
                print(f"STATE1: {state1}")
                print(f"STATE2: {state2}")
                print(f"STATE3: {state3}")
                print(f"STATE4: {state4}")
            except ValueError:
                print("Error decoding button states.")
        else:
            print("Invalid button payload format.")

    def search_for_slaves(self):
        """Send the SRCH command to search for slaves and update the MAC address list."""
        command = "SRCH"
        payload = ""
        formatted_command = self.format_command(command, payload)
        self.serial_conn.write(formatted_command.encode())

        self.mac_addresses = []
        while True:
            if self.serial_conn.in_waiting >= 41:
                response = self.serial_conn.read(41).decode('utf-8', errors='replace')
                command, payload, valid = self.decode_response(response)
                if not valid:
                    print("Invalid checksum received. Ignoring response.")
                    continue
                if command.startswith("MAC"):
                    if command == "MACN":
                        print("No MAC addresses found.")
                        break
                    mac_index = int(command[3])
                    mac_address = payload.strip("@")
                    self.mac_addresses.append(mac_address)
                elif command == "OKAY":
                    break

        if self.mac_addresses:
            print("Found MAC addresses:")
            for idx, mac in enumerate(self.mac_addresses):
                print(f"{idx}: {mac}")

    def wait_for_response(self):
        """Wait for a response from the device."""
        while True:
            if self.serial_conn.in_waiting >= 41:
                response = self.serial_conn.read(41).decode('utf-8', errors='replace')
                command, payload, valid = self.decode_response(response)
                if not valid:
                    print("Invalid checksum received. Ignoring response.")
                    continue
                if command in ["OKAY", "NACK", "SENS", "BUSY", "BUTS"]:
                    return command, payload

    def send_command(self, command, payload):
        """Send a command to the device and handle the response."""
        formatted_command = self.format_command(command, payload)
        self.serial_conn.write(formatted_command.encode())
        while True:
            response, payload = self.wait_for_response()
            if response == "OKAY":
                print("Command acknowledged successfully.")
                break
            elif response in ["SENS", "BUTS"]:
                return payload
            elif response == "NACK":
                print("Command not acknowledged. Please choose an option:")
                print("1: Resend the command")
                print("2: Return to the main menu")
                choice = int(input("Select an option: "))
                if choice == 1:
                    self.serial_conn.write(formatted_command.encode())
                elif choice == 2:
                    break
            elif response == "BUSY":
                print("Device is busy. Please wait!")
                return None
        return None

    def set_led_color(self):
        """Set the LED color for a selected MAC address."""
        print("Available MAC addresses:")
        for idx, mac in enumerate(self.mac_addresses):
            print(f"{idx}: {mac}")
        index = int(input("Select a MAC address index: "))
        colors = [int(input(f"Enter value for {color} (0-255): ")) for color in ["R", "G", "B", "W", "A", "UV"]]
        payload = f"{index:01}" + "".join([f"{color:03}" for color in colors])
        self.send_command("COLR", payload)

    def turn_off_led(self):
        """Turn off the LED for a selected MAC address."""
        print("Available MAC addresses:")
        for idx, mac in enumerate(self.mac_addresses):
            print(f"{idx}: {mac}")
        index = int(input("Select a MAC address index: "))
        payload = f"{index:01}" + "000000000000000000"
        self.send_command("COLR", payload)

    def set_preset_color(self):
        """Set a preset LED color for a selected MAC address."""
        preset_colors = [
            ("RED", (255, 0, 0, 0, 0, 0)),
            ("ORANGE", (255, 165, 0, 0, 0, 0)),
            ("YELLOW", (255, 255, 0, 0, 0, 0)),
            ("GREEN", (0, 255, 0, 0, 0, 0)),
            ("BLUE", (0, 0, 255, 0, 0, 0)),
            ("PURPLE", (128, 0, 128, 0, 0, 0)),
            ("WHITE", (0, 0, 0, 255, 0, 0)),
            ("UV", (0, 0, 0, 0, 0, 255))
        ]
        
        print("Available MAC addresses:")
        for idx, mac in enumerate(self.mac_addresses):
            print(f"{idx}: {mac}")
        index = int(input("Select a MAC address index: "))
        
        print("Available presets:")
        for idx, (preset, _) in enumerate(preset_colors):
            print(f"{idx}: {preset}")
        
        preset_index = int(input("Enter a preset color index: "))
        if 0 <= preset_index < len(preset_colors):
            _, colors = preset_colors[preset_index]
            payload = f"{index:01}" + "".join([f"{color:03}" for color in colors])
            self.send_command("COLR", payload)
        else:
            print("Invalid preset color index.")

    def display_mac_addresses(self):
        """Display the list of MAC addresses."""
        if not self.mac_addresses:
            print("No MAC addresses found.")
        else:
            print("MAC addresses:")
            for idx, mac in enumerate(self.mac_addresses):
                print(f"{idx}: {mac}")

    def get_sensor_values(self):
        """Get sensor values for a selected MAC address."""
        print("Available MAC addresses:")
        for idx, mac in enumerate(self.mac_addresses):
            print(f"{idx}: {mac}")
        index = int(input("Select a MAC address index: "))
        payload = f"{index:01}"
        sensor_payload = self.send_command("SENS", payload)
        if sensor_payload:
            self.decode_sensor_payload(sensor_payload)

    def play_buzzer_sound(self):
        """Play a buzzer sound for a selected MAC address."""
        print("Available MAC addresses:")
        for idx, mac in enumerate(self.mac_addresses):
            print(f"{idx}: {mac}")
        index = int(input("Select a MAC address index: "))
        tone = input("Enter the buzzer sound value (uppercase): ").strip().upper()
        payload = f"{index:01}{tone}"
        formatted_command = self.format_command("TONE", payload)
        self.serial_conn.write(formatted_command.encode())

        while True:
            response, _ = self.wait_for_response()
            if response == "OKAY":
                print("Buzzer command acknowledged successfully.")
                break
            elif response == "NACK":
                print("Command not acknowledged. Please choose an option:")
                print("1: Resend the command")
                print("2: Return to the main menu")
                choice = int(input("Select an option: "))
                if choice == 1:
                    self.serial_conn.write(formatted_command.encode())
                elif choice == 2:
                    break
            elif response == "BUSY":
                print("Device is busy. Please wait and try again.")

    def read_button_states(self):
        """Read the button states from the device."""
        formatted_command = self.format_command("RBUT", "")
        self.serial_conn.write(formatted_command.encode())
        
        while True:
            response, payload = self.wait_for_response()
            if response == "BUTS":
                self.decode_button_payload(payload)
                break
            elif response == "NACK":
                print("Command not acknowledged. Please choose an option:")
                print("1: Resend the command")
                print("2: Return to the main menu")
                choice = int(input("Select an option: "))
                if choice == 1:
                    self.serial_conn.write(formatted_command.encode())
                elif choice == 2:
                    break

    @staticmethod
    def clear_console():
        """Clear the console."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def main_menu(self):
        """Display the main menu and handle user input."""
        while True:
            print("Menu:")
            print("1: Search for slaves")
            if self.mac_addresses:
                print("2: Set LED color")
                print("3: Turn off LED")
                print("4: Set preset color")
                print("5: Get sensor values")
                print("6: Play buzzer sound")
                print("7: Read button states")
                print("8: Show MAC addresses")
                print("9: Exit")
            else:
                print("2: Exit")
            choice = int(input("Select an option: "))

            if choice == 1:
                self.search_for_slaves()
            elif choice == 2:
                if self.mac_addresses:
                    self.set_led_color()
                else:
                    break
            elif choice == 3 and self.mac_addresses:
                self.turn_off_led()
            elif choice == 4 and self.mac_addresses:
                self.set_preset_color()
            elif choice == 5 and self.mac_addresses:
                self.get_sensor_values()
            elif choice == 6 and self.mac_addresses:
                self.play_buzzer_sound()
            elif choice == 7 and self.mac_addresses:
                self.read_button_states()
            elif choice == 8 and self.mac_addresses:
                self.display_mac_addresses()
            elif choice == 9 and self.mac_addresses:
                break
            else:
                print("Invalid option. Please try again.")
            
            if self.mac_addresses and choice != 9:
                clear_choice = input("Do you want to clear the console? (y/n): ").strip().lower()
                if clear_choice == 'y':
                    self.clear_console()

        self.serial_conn.close()

if __name__ == "__main__":
    manager = SerialDeviceManager()
    manager.select_serial_port()
    if manager.serial_conn:
        manager.main_menu()
