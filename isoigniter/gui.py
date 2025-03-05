from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout,
    QFileDialog,
    QLabel,
    QComboBox,
    QProgressBar,
    QMessageBox,
)
from PySide6.QtCore import Signal
from isoigniter.utils import get_usb_devices, has_mbr_signature
from isoigniter.hybrid_iso_writer import (
    UsbWriterThread,
)  # Import hybrid iso writer thread
from isoigniter.win_iso_writer import (
    WinWriterThread,
)  # Import the Windows writer thread


class UsbWriterUI(QWidget):
    start_write = Signal(str, str)  # Signal to trigger writing process

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bootable USB Writer")
        self.setGeometry(100, 100, 400, 200)

        self.iso_label = QLabel("Select ISO:")
        self.iso_button = QPushButton("Browse")
        self.iso_button.clicked.connect(self.select_iso)

        self.device_label = QLabel("Select USB Device:")
        self.device_combo = QComboBox()
        self.update_devices()

        self.write_button = QPushButton("Write to USB")
        self.write_button.clicked.connect(self.start_writing)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        layout = QVBoxLayout()
        layout.addWidget(self.iso_label)
        layout.addWidget(self.iso_button)
        layout.addWidget(self.device_label)
        layout.addWidget(self.device_combo)
        layout.addWidget(self.write_button)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)
        self.iso_path = None
        self.writer_thread = None  # Placeholder for thread

    def select_iso(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select ISO File", "", "ISO Files (*.iso)"
        )
        if file_path:
            self.iso_path = file_path
            self.iso_label.setText(f"ISO: {file_path}")

    def update_devices(self):
        self.device_combo.clear()
        self.device_combo.addItems(get_usb_devices())

    def start_writing(self):
        if not self.iso_path:
            QMessageBox.warning(self, "Error", "Please select an ISO file.")
            return

        usb_device = self.device_combo.currentText()
        if not usb_device:
            QMessageBox.warning(self, "Error", "No USB device selected.")
            return

        is_hybrid = has_mbr_signature(self.iso_path)

        self.write_button.setEnabled(False)
        self.progress_bar.setValue(0)

        # **Start the writer thread**
        if is_hybrid:
            self.writer_thread = UsbWriterThread(self.iso_path, usb_device)
        else:
            self.writer_thread = WinWriterThread(self.iso_path, usb_device)
        self.writer_thread.progress.connect(
            self.progress_bar.setValue
        )  # Update progress bar
        self.writer_thread.finished.connect(self.on_write_complete)  # Handle completion
        self.writer_thread.start()  # Start the writing process

    def on_write_complete(self, success, message):
        self.write_button.setEnabled(True)
        QMessageBox.information(self, "Finished", message)
