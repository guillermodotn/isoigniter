from PySide6.QtCore import QThread, Signal
import os


class UsbWriterThread(QThread):
    progress = Signal(int)
    finished = Signal(bool, str)

    def __init__(self, iso_path, usb_device):
        super().__init__()
        self.iso_path = iso_path
        self.usb_device = usb_device

    def run(self):
        try:
            total_size = os.path.getsize(self.iso_path)
            with open(self.usb_device, "wb") as device:
                with open(self.iso_path, "rb") as iso:
                    bytes_written = 0
                    chunk_size = 4096
                    while True:
                        chunk = iso.read(chunk_size)
                        if not chunk:
                            break
                        device.write(chunk)
                        bytes_written += len(chunk)
                        progress = int((bytes_written / total_size) * 100)
                        self.progress.emit(progress)  # Emit progress
            self.finished.emit(True, "Write complete.")  # Emit completion signal
        except Exception as e:
            self.finished.emit(False, str(e))  # Emit error message
