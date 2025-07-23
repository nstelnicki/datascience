# Import RPi.GPIO if available, otherwise provide a mock version for testing/development
try:
    import RPi.GPIO as GPIO
    RASPBERRY_PI_ENVIRONMENT = True
except ImportError:
    print("RPi.GPIO module not found. Using a mock version for development.")
    RASPBERRY_PI_ENVIRONMENT = False
    # Mock GPIO class and functions
    class MockGPIO:
        BCM = "BCM_MODE"
        IN = "INPUT_MODE"
        PUD_UP = "PULL_UP_DOWN_UP"
        PUD_DOWN = "PULL_UP_DOWN_DOWN"
        HIGH = 1
        LOW = 0
        _pin_states = {} # To store mock pin states
        _warnings = True

        def setmode(self, mode):
            print(f"MockGPIO: Mode set to {mode}")

        def setup(self, pin, mode, pull_up_down=None):
            print(f"MockGPIO: Pin {pin} setup as {mode}", end="")
            if pull_up_down is not None:
                print(f" with pull_up_down={pull_up_down}", end="")
            print()
            if pull_up_down == self.PUD_UP:
                self._pin_states[pin] = self.HIGH # Default to high if pulled up
            elif pull_up_down == self.PUD_DOWN:
                 self._pin_states[pin] = self.LOW # Default to low if pulled down
            else:
                self._pin_states[pin] = self.LOW # Default state if no pull resistor

        def input(self, pin):
            state = self._pin_states.get(pin, self.LOW) # Default to LOW if not set
            # print(f"MockGPIO: Reading from pin {pin}, returning {state}")
            return state

        def cleanup(self):
            print("MockGPIO: Cleanup called.")
            self._pin_states = {}

        def setwarnings(self, state):
            self._warnings = state
            print(f"MockGPIO: Warnings set to {state}")

        # Mock a way to change pin state for testing
        def _set_pin_state(self, pin, state):
            if pin not in self._pin_states:
                 print(f"MockGPIO: Warning - Pin {pin} not setup before setting state. Call setup first.")
            self._pin_states[pin] = state
            print(f"MockGPIO: Test - Pin {pin} state set to {state}")


    GPIO = MockGPIO()

# --- Configuration ---
# GPIO pin for the switch (using BCM numbering)
# IMPORTANT: Choose a pin that is free and safe to use on your Raspberry Pi.
# For this example, we'll use GPIO 17.
SWITCH_PIN = 17
# Define what GPIO signal means "IN" vs "OUT"
# Assuming: Switch connected between SWITCH_PIN and GND.
# - When switch is "IN" (e.g., closed), it pulls the pin LOW.
# - When switch is "OUT" (e.g., open), the pin is HIGH (due to pull-up resistor).
# So, IN_STATE = GPIO.LOW, OUT_STATE = GPIO.HIGH
# We will use a pull-up resistor, so:
# Open switch (OUT) -> Pin is HIGH
# Closed switch (IN) -> Pin is LOW
SWITCH_POSITION_IN_STATE = GPIO.LOW
SWITCH_POSITION_OUT_STATE = GPIO.HIGH


def setup_gpio():
    """Sets up the GPIO pins for the switch."""
    if RASPBERRY_PI_ENVIRONMENT:
        GPIO.setwarnings(False) # Disable warnings for cleaner output if re-running
        GPIO.setmode(GPIO.BCM)  # Use Broadcom pin numbering
        # Setup SWITCH_PIN as input with an internal pull-up resistor.
        # This means if the switch is open, the pin will read HIGH.
        # If the switch is closed (connecting the pin to GND), it will read LOW.
        GPIO.setup(SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        print(f"GPIO pin {SWITCH_PIN} setup as input with pull-up resistor.")
    else:
        GPIO.setmode(GPIO.BCM) # Call mock version
        GPIO.setup(SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Call mock version
        print("Mock GPIO setup complete for SWITCH_PIN.")

def get_switch_state():
    """
    Reads the state of the switch.
    Returns "IN" if the switch is in the 'IN' position (connected to GND, so pin is LOW).
    Returns "OUT" if the switch is in the 'OUT' position (open, so pin is HIGH due to pull-up).
    Returns None if in a non-Pi environment and state isn't mock-set.
    """
    if not RASPBERRY_PI_ENVIRONMENT and SWITCH_PIN not in GPIO._pin_states:
        # Provide a default or indicate that state needs to be mocked for testing
        print("MockGPIO: Switch state not explicitly set for testing. Defaulting to OUT.")
        GPIO._set_pin_state(SWITCH_PIN, SWITCH_POSITION_OUT_STATE) # Default to OUT

    current_state = GPIO.input(SWITCH_PIN)
    if current_state == SWITCH_POSITION_IN_STATE:
        return "IN"
    elif current_state == SWITCH_POSITION_OUT_STATE:
        return "OUT"
    else:
        # This case should ideally not be reached if using pull-up/pull-down correctly
        print(f"Warning: Unexpected GPIO state {current_state} on pin {SWITCH_PIN}")
        return None

def get_barcode_input(prompt_message="Scan barcode: "):
    """
    Gets barcode input from the user (simulating a keyboard-emulating scanner).
    Returns the stripped string or None if input is empty.
    """
    try:
        barcode = input(prompt_message)
        return barcode.strip() if barcode else None
    except EOFError: # Handle cases where input stream is closed (e.g. in testing)
        print("EOFError encountered while trying to read barcode input.")
        return None
    except KeyboardInterrupt:
        print("\nKeyboard interrupt detected during barcode input.")
        raise # Re-raise to allow the main loop to catch it

def cleanup_gpio():
    """Cleans up GPIO settings. Should be called on program exit."""
    if RASPBERRY_PI_ENVIRONMENT:
        GPIO.cleanup()
        print("GPIO cleanup performed.")
    else:
        GPIO.cleanup() # Call mock version

if __name__ == '__main__':
    print("--- Testing Hardware Interface ---")
    setup_gpio()

    if not RASPBERRY_PI_ENVIRONMENT:
        print("\n--- Mocking Switch States (since not on Pi) ---")
        # Test "IN" state
        GPIO._set_pin_state(SWITCH_PIN, SWITCH_POSITION_IN_STATE) # Simulate switch to "IN" (LOW)
        print(f"Switch state (mocked to IN): {get_switch_state()}")

        # Test "OUT" state
        GPIO._set_pin_state(SWITCH_PIN, SWITCH_POSITION_OUT_STATE) # Simulate switch to "OUT" (HIGH)
        print(f"Switch state (mocked to OUT): {get_switch_state()}")
    else:
        print("\n--- Live GPIO Test (connect switch to GPIO 17 and GND) ---")
        print("Please toggle the switch and observe the output for the next 10 seconds.")
        import time
        for i in range(20): # Check state every 0.5s for 10s
            print(f"Current switch state: {get_switch_state()}")
            time.sleep(0.5)

    print("\n--- Testing Barcode Input ---")
    # Note: The following input calls will require manual input if run directly.
    # In a real script, these would likely be triggered based on switch state.
    # For automated testing, you'd need to pipe input to the script.
    print("Test barcode input (Ctrl+D or empty input to skip, Ctrl+C to interrupt):")
    try:
        barcode1 = get_barcode_input("Test Scan 1: ")
        print(f"Barcode 1 received: '{barcode1}'")
        barcode2 = get_barcode_input("Test Scan 2: ")
        print(f"Barcode 2 received: '{barcode2}'")
    except KeyboardInterrupt:
        print("Test input interrupted.")

    cleanup_gpio()
    print("\n--- Hardware Interface Test Complete ---")
