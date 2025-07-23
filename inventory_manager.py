import time
import database_handler
import hardware_handler

def main():
    print("Inventory Management System - Starting")

    # Initialize GPIO
    hardware_handler.setup_gpio()

    # Initialize Database
    database_handler.init_db()

    last_switch_state = None
    current_switch_state = None

    try:
        print("System ready. Waiting for switch changes or barcode scans.")
        if not hardware_handler.RASPBERRY_PI_ENVIRONMENT:
            print("INFO: Running in a mock environment. You may need to manually mock switch states if not done by default in hardware_handler.")
            # Example of how one might toggle the mock switch for testing if needed:
            # hardware_handler.GPIO._set_pin_state(hardware_handler.SWITCH_PIN, hardware_handler.GPIO.LOW) # Mock "IN"
            # hardware_handler.GPIO._set_pin_state(hardware_handler.SWITCH_PIN, hardware_handler.GPIO.HIGH) # Mock "OUT"


        while True:
            current_switch_state = hardware_handler.get_switch_state()

            if current_switch_state != last_switch_state:
                if current_switch_state == "IN":
                    print("\nSwitch is now IN. Ready to ADD barcodes.")
                elif current_switch_state == "OUT":
                    print("\nSwitch is now OUT. Ready to REMOVE barcodes.")
                else: # Should not happen with good wiring
                    print(f"\nSwitch is in an UNKNOWN state ({current_switch_state}). Please check wiring.")
                last_switch_state = current_switch_state

            if current_switch_state == "IN":
                # Non-blocking check for input could be complex here.
                # For simplicity, we'll prompt when the switch is IN.
                # A more advanced version might use threading or async input.
                print("Mode: IN (Add). Waiting for barcode scan...")
                barcode = hardware_handler.get_barcode_input("Scan barcode to ADD: ")
                if barcode:
                    if database_handler.add_barcode(barcode):
                        print(f"SUCCESS: Barcode '{barcode}' ADDED to database.")
                    else:
                        # Error/info message already printed by add_barcode
                        print(f"FAILED: Could not add barcode '{barcode}'. It might already exist or be invalid.")
                elif barcode is not None: # Empty string entered, not EOF
                     print("No barcode entered.")
                else: # EOF or other issue from get_barcode_input
                    print("No valid barcode input received.")

                # Add a small delay to prevent spamming input prompts if switch is noisy
                # or if scanner sends multiple "enters"
                time.sleep(0.5)

            elif current_switch_state == "OUT":
                print("Mode: OUT (Remove). Waiting for barcode scan...")
                barcode = hardware_handler.get_barcode_input("Scan barcode to REMOVE: ")
                if barcode:
                    if database_handler.remove_barcode(barcode):
                        print(f"SUCCESS: Barcode '{barcode}' REMOVED from database.")
                    else:
                        # Error/info message already printed by remove_barcode
                        print(f"INFO: Barcode '{barcode}' could not be removed (may not exist or invalid).")
                elif barcode is not None: # Empty string entered
                    print("No barcode entered.")
                else: # EOF or other issue
                    print("No valid barcode input received.")

                time.sleep(0.5)

            else: # Switch state is None or unexpected
                # This might happen briefly during startup if RPi.GPIO is slow
                # or if get_switch_state() returns None in mock mode without explicit setting.
                if hardware_handler.RASPBERRY_PI_ENVIRONMENT:
                    print("Waiting for valid switch state...")
                else: # Mock environment hint
                    print("Mock Env: Switch state is None. Ensure `hardware_handler.GPIO._set_pin_state()` is called if testing state changes.")
                time.sleep(1) # Wait a bit before re-checking

    except KeyboardInterrupt:
        print("\nExiting program due to KeyboardInterrupt.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("Performing cleanup...")
        hardware_handler.cleanup_gpio()
        print("Inventory Management System - Stopped")

if __name__ == '__main__':
    main()
