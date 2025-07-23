# Raspberry Pi Inventory Management System

This Python program allows a Raspberry Pi to manage a simple inventory list by reading the state of a physical switch and processing barcode scans.

- If a switch is set to "IN", scanned barcodes are **added** to an SQLite database.
- If the switch is set to "OUT", scanned barcodes are **removed** from the database.

## Features

-   **Switch-based operation mode:** Clearly defined "IN" (add) and "OUT" (remove) modes.
-   **Barcode scanning:** Accepts input from USB barcode scanners that emulate keyboard input.
-   **SQLite Database:** Stores barcode data persistently.
-   **GPIO Interaction:** Uses Raspberry Pi GPIO pins to read switch status.
-   **Mockable Hardware:** Includes a mock GPIO interface for development and testing in non-Pi environments.

## Requirements

### Hardware
-   Raspberry Pi (any model with GPIO pins)
-   MicroSD card with Raspberry Pi OS
-   Power supply for Raspberry Pi
-   USB Barcode Scanner (that acts as a keyboard/HID device)
-   A physical switch (e.g., a toggle switch, SPDT)
-   Jumper wires
-   (Optional but Recommended) Breadboard
-   (Optional but Recommended) A pull-up or pull-down resistor (e.g., 10kΩ) if not using the internal pull-up. This project is configured to use the internal pull-up resistor.

### Software
-   Python 3 (should be pre-installed on Raspberry Pi OS)
-   `RPi.GPIO` Python library:
    -   Install on Raspberry Pi OS using: `sudo apt-get update && sudo apt-get install python3-rpi.gpio`

## Setup and Wiring

1.  **Software Installation:**
    *   Ensure Python 3 is available.
    *   Install the `RPi.GPIO` library using the command above.
    *   Clone this repository or download the files (`inventory_manager.py`, `database_handler.py`, `hardware_handler.py`, `requirements.txt`) to your Raspberry Pi.

2.  **Hardware Wiring (Switch):**
    *   The script is configured to use **GPIO 17 (Pin 11 on the 40-pin header)** for the switch input.
    *   It uses the Raspberry Pi's internal **pull-up resistor**.
    *   **"OUT" state (default/open):** The switch should be open, meaning GPIO 17 is not connected to Ground. The internal pull-up resistor will keep the pin HIGH.
    *   **"IN" state (closed):** The switch should connect GPIO 17 to a Ground (GND) pin on the Raspberry Pi. This will pull the pin LOW.

    **Example Wiring (for a simple 2-pin toggle switch):**
    *   One terminal of the switch: Connect to **GPIO 17**.
    *   Other terminal of the switch: Connect to a **GND** pin on the Raspberry Pi.

    *Warning: Always be careful when working with GPIO pins to avoid short circuits. Double-check your connections before powering on.*

3.  **Barcode Scanner:**
    *   Connect your USB barcode scanner to one of the USB ports on the Raspberry Pi.
    *   It is assumed the scanner behaves like a keyboard (HID device). When a barcode is scanned, its value should be typed out, followed by an Enter keystroke. Most USB scanners work this way by default.

## Running the Script

1.  Navigate to the directory where you saved the files:
    ```bash
    cd path/to/your/script_directory
    ```
2.  Run the main script:
    ```bash
    python3 inventory_manager.py
    ```
3.  The program will start, initialize the GPIO and database, and then wait for switch changes or barcode scans.
    *   Set your physical switch to the "IN" or "OUT" position.
    *   Scan barcodes. The program will provide feedback in the console.
4.  To stop the program, press `Ctrl+C`. This will trigger a cleanup routine for the GPIO pins.

## How it Works

-   **`inventory_manager.py`:** The main application script that orchestrates the logic, reads the switch, and calls appropriate database and hardware functions.
-   **`database_handler.py`:** Manages all interactions with the `inventory.db` SQLite database, including creating the table, adding barcodes, and removing barcodes.
-   **`hardware_handler.py`:** Handles direct interaction with hardware:
    -   Reading the GPIO pin connected to the switch.
    -   Getting input from the barcode scanner (simulated as standard keyboard input).
    -   Includes a mock GPIO setup for running the code on non-Pi systems for development (though hardware interactions won't occur).
-   **`requirements.txt`:** Lists Python package dependencies (primarily for documentation in this case, as `RPi.GPIO` is system-installed).

## Development and Testing

-   The `hardware_handler.py` script includes a mock `GPIO` class. If `RPi.GPIO` cannot be imported (e.g., you're on a Windows/macOS/Linux PC), the script will use this mock version. This allows you to run `inventory_manager.py` and test the application flow, database interactions, and barcode input logic without a Raspberry Pi.
-   When running with the mock interface, the switch state will not change based on physical hardware. You can see examples in `hardware_handler.py`'s `if __name__ == '__main__':` block on how to simulate pin state changes for testing if needed, or modify `inventory_manager.py` to call `hardware_handler.GPIO._set_pin_state()` for testing purposes.

## Troubleshooting

-   **No switch state change:** Double-check your wiring for the switch on GPIO 17 and GND. Ensure the switch is functioning correctly.
-   **Barcode not read:**
    -   Verify your scanner is powered on and connected.
    -   Test if the scanner works as a keyboard in a text editor on the Raspberry Pi. It should type the barcode numbers and press Enter.
    -   Ensure the terminal window running the script has focus when you scan.
-   **Permission errors for GPIO:** You might need to run the script with `sudo python3 inventory_manager.py` if you encounter permission issues with GPIO access, though typically being part of the `gpio` group is sufficient.
-   **Database errors:** The script prints error messages from SQLite. The database file `inventory.db` will be created in the same directory as the script.
