import sqlite3
import os

DATABASE_NAME = 'inventory.db'

def init_db():
    """Initializes the database and creates the barcodes table if it doesn't exist."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS barcodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode_value TEXT UNIQUE NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print(f"Database '{DATABASE_NAME}' initialized and 'barcodes' table ensured.")

def add_barcode(barcode_value):
    """Adds a barcode to the database. Returns True if successful, False otherwise."""
    if not barcode_value:
        print("Error: Barcode value cannot be empty.")
        return False
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO barcodes (barcode_value) VALUES (?)", (barcode_value,))
        conn.commit()
        print(f"Barcode '{barcode_value}' added successfully.")
        return True
    except sqlite3.IntegrityError:
        print(f"Error: Barcode '{barcode_value}' already exists in the database.")
        return False
    except Exception as e:
        print(f"Error adding barcode '{barcode_value}': {e}")
        return False
    finally:
        conn.close()

def remove_barcode(barcode_value):
    """Removes a barcode from the database. Returns True if successful, False otherwise."""
    if not barcode_value:
        print("Error: Barcode value cannot be empty.")
        return False
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM barcodes WHERE barcode_value = ?", (barcode_value,))
        result = cursor.fetchone()
        if result:
            cursor.execute("DELETE FROM barcodes WHERE barcode_value = ?", (barcode_value,))
            conn.commit()
            if cursor.rowcount > 0:
                print(f"Barcode '{barcode_value}' removed successfully.")
                return True
            else:
                # Should not happen if previous check passed, but as a safeguard
                print(f"Error: Barcode '{barcode_value}' could not be removed (unexpectedly).")
                return False
        else:
            print(f"Info: Barcode '{barcode_value}' not found in the database.")
            return False # Or True, depending on desired behavior for "not found"
    except Exception as e:
        print(f"Error removing barcode '{barcode_value}': {e}")
        return False
    finally:
        conn.close()

def check_barcode_exists(barcode_value):
    """Checks if a barcode exists in the database. Returns True if exists, False otherwise."""
    if not barcode_value:
        return False
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM barcodes WHERE barcode_value = ?", (barcode_value,))
        exists = cursor.fetchone() is not None
        return exists
    except Exception as e:
        print(f"Error checking barcode '{barcode_value}': {e}")
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    # Basic test and initialization
    if os.path.exists(DATABASE_NAME):
        os.remove(DATABASE_NAME) # Clean up for testing
        print(f"Removed existing database '{DATABASE_NAME}' for fresh test.")

    init_db()

    print("\n--- Testing add_barcode ---")
    add_barcode("12345")
    add_barcode("67890")
    add_barcode("12345") # Duplicate
    add_barcode("")     # Empty

    print("\n--- Testing check_barcode_exists ---")
    print(f"Barcode '12345' exists? {check_barcode_exists('12345')}")
    print(f"Barcode '00000' exists? {check_barcode_exists('00000')}")

    print("\n--- Testing remove_barcode ---")
    remove_barcode("12345")
    remove_barcode("00000") # Not existing
    remove_barcode("")      # Empty

    print("\n--- Final check ---")
    print(f"Barcode '12345' exists? {check_barcode_exists('12345')}")
    print(f"Barcode '67890' exists? {check_barcode_exists('67890')}")

    # Clean up the test database
    # os.remove(DATABASE_NAME)
    # print(f"Cleaned up test database '{DATABASE_NAME}'.")
    print(f"Test database '{DATABASE_NAME}' is available for inspection.")
