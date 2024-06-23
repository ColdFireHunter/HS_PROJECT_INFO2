from machine import Pin

class ButtonHandler:
    """
    A class to handle multiple button inputs using GPIO pins configured with pull-down resistors.

    Attributes:
    ----------
    buttons : list
        A list of Pin objects corresponding to the GPIO pins connected to the buttons.
    """
    
    def __init__(self, pin_numbers):
        """
        Initializes the ButtonHandler with the specified GPIO pins.

        Parameters:
        ----------
        pin_numbers : list
            A list of integers representing the GPIO pin numbers connected to the buttons.
        """
        # Initialize the list to hold the Pin objects
        self.buttons = []
        # Configure each pin as input with a pull-down resistor
        for pin_number in pin_numbers:
            pin = Pin(pin_number, Pin.IN, Pin.PULL_DOWN)
            self.buttons.append(pin)
    
    def check_button_states(self):
        """
        Checks the states of all buttons and returns a formatted string.

        Returns:
        -------
        str
            A string representing the states of the buttons, with '1' for pressed and '0' for not pressed, separated by '$'.
        """
        # Initialize a list to hold the button states
        states = []
        # Check each button and append '1' or '0' to the states list
        for button in self.buttons:
            state = '1' if button.value() else '0'
            states.append(state)
        # Join the states list into a string separated by '$' and return
        return '$'.join(states)