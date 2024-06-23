from machine import Pin, PWM

class LEDController:
    def __init__(self):
        # Initialize PWM for each LED with a default duty cycle
        self.ledR = PWM(Pin(7), freq=16000, duty_u16=32768)
        self.ledG = PWM(Pin(15), freq=16000, duty_u16=32768)
        self.ledB = PWM(Pin(16), freq=16000, duty_u16=32768)
        self.ledW = PWM(Pin(17), freq=16000, duty_u16=32768)
        self.ledA = PWM(Pin(8), freq=16000, duty_u16=32768)
        self.ledUV = PWM(Pin(18), freq=16000, duty_u16=32768)
        
        # Store all LED PWM objects in a list for easy management
        self.leds = [self.ledR, self.ledG, self.ledB, self.ledW, self.ledA, self.ledUV]
        
        # Turn off all LEDs initially
        self.turn_off()
        
        # Initialize a debug LED
        self.led = Pin(6, Pin.OUT)
        self.debug_off()  # Ensure the debug LED is off initially

    def validate_hex_code(self, hex_code):
        """Validate the hex code format."""
        if not isinstance(hex_code, str):
            raise ValueError("Hex code must be a string.")
        if not hex_code.startswith('0x') and not hex_code.startswith('0X'):
            raise ValueError("Hex code must start with '0x' or '0X'.")
        hex_str = hex_code[2:]
        if len(hex_str) != 12:
            raise ValueError("Invalid hex code length. Expected 12 characters.")
        try:
            int(hex_str, 16)
        except ValueError:
            raise ValueError("Hex code contains invalid characters.")

    def hex_to_duty(self, hex_code):
        """Convert hex code to PWM duty values."""
        self.validate_hex_code(hex_code)
        hex_str = hex_code[2:]
        duties = [int(hex_str[i:i+2], 16) for i in range(0, 12, 2)]
        mapped_duties = [int(d * 1023 / 255) for d in duties]  # Map to PWM range
        return mapped_duties

    def set_leds(self, hex_code):
        """Set the LEDs to the brightness values specified by the hex code."""
        duties = self.hex_to_duty(hex_code)
        for led, duty in zip(self.leds, duties):
            led.duty(duty)

    def turn_off(self):
        """Turn off all LEDs."""
        for led in self.leds:
            led.duty(0)
            
    def debug_on(self):
        """Turn the debug LED on."""
        self.led.on()

    def debug_off(self):
        """Turn the debug LED off."""
        self.led.off()

    def debug_toggle(self):
        """Toggle the debug LED state."""
        if self.led.value() == 1:
            self.debug_off()
        else:
            self.debug_on()
