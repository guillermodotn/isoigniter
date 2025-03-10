import sys
from PySide6.QtWidgets import QApplication
from isoigniter.gui import UsbWriterUI  # Import your UI class
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = QApplication(sys.argv)  # Create the Qt application
    window = UsbWriterUI()  # Create an instance of your GUI
    window.show()  # Show the window
    sys.exit(app.exec())  # Run the application event loop
