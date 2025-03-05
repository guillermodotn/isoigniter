from PySide6.QtCore import QThread, Signal
import logging
import subprocess


class WinWriterThread(QThread):
    progress = Signal(int)
    finished = Signal(bool, str)

    def __init__(self, iso_path, usb_device):
        super().__init__()
        self.iso_path = iso_path
        self.usb_device = usb_device

    def run(self):
        try:
            self.create_partition_table(self.usb_device)
            self.finished.emit(True, "Write complete.")  # Emit completion signal
        except Exception as e:
            self.finished.emit(False, str(e))  # Emit error message

    def create_partition_table(self, device):
        """Creates a GPT partition table and a FAT32 partition on the given device."""

        try:
            # Create a new GPT partition table
            subprocess.run(["parted", "-s", device, "mklabel", "gpt"], check=True)
            logging.info(f"Created GPT partition table on {device}")

            # Create a new primary partition (FAT32, using 100% of disk)
            subprocess.run(
                ["parted", "-s", device, "mkpart", "primary", "fat32", "1MiB", "100%"],
                check=True,
            )
            logging.info(f"Created primary partition on {device}")

            # Format the partition as FAT32 (assuming it's /dev/sdb1)
            partition = f"{device}1"
            subprocess.run(
                ["mkfs.vfat", "-F32", partition], check=True, stdout=subprocess.DEVNULL
            )
            logging.info(f"Partition table created and formatted on {device}")

        except subprocess.CalledProcessError as e:
            logging.error(f"Error: {e}")
