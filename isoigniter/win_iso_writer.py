from PySide6.QtCore import QThread, Signal
import logging
import subprocess
from importlib.resources import files
import re

class WinWriterThread(QThread):
    progress = Signal(int)
    finished = Signal(bool, str)

    def __init__(self, iso_path, usb_device):
        super().__init__()
        self.iso_path = iso_path
        self.usb_device = usb_device
        self.uefi_ntfs_img_path = files('isoigniter').joinpath("resources/uefi-ntfs.img")

    def run(self):
        try:
            self.create_partition_table(self.usb_device)
            self.copy_files_to_usb()
            self.finished.emit(True, "Write complete.")  # Emit completion signal
        except Exception as e:
            self.finished.emit(False, str(e))  # Emit error message

    def create_partition_table(self, device):
        """Creates a GPT partition table and partions on the device."""

        try:
            # Get the size of the device
            result = subprocess.run(["lsblk", "-b", "-n", "-d", "-o", "SIZE", device], check=True, stdout=subprocess.PIPE, text=True)
            logging.info(f"Device size: {result.stdout.strip()} bytes")
            win_data_partition_size = int(result.stdout.strip()) // 1024**2 - 10  # 10MB less than the total size
            logging.info(f"Win data partition size: {win_data_partition_size} MiB")

            # Create a new GPT partition table
            subprocess.run(["parted", "-s", device, "mklabel", "gpt"], check=True)
            logging.info(f"Created GPT partition table on {device}")

            # Create a new primary partition (FAT32, using 100% of disk)
            subprocess.run(
                ["parted", "-s", device, "mkpart", "primary", "fat32", f"{win_data_partition_size}MiB", "100%"],
                check=True,
            )
            logging.info(f"Created primary partition (boot) on {device}")

            # Create a new primary partition (FAT32, using 100% of disk)
            subprocess.run(
                ["parted", "-s", device, "mkpart", "primary", "ntfs", "0%", "100%"],
                check=True,
            )
            logging.info(f"Created primary partition (Win data) on {device}")

            # Format the partition as NTFS (assuming it's /dev/sda1)
            partition = f"{device}1"
            subprocess.run(
                ["mkfs.ntfs", "-f", partition], check=True, stdout=subprocess.DEVNULL
            )
            logging.info(f"Partition {partition} formatted as NTFS")

            # Format the partition as FAT32 (assuming it's /dev/sda2)
            partition = f"{device}2"
            subprocess.run(
                ["mkfs.vfat", "-F32", partition], check=True, stdout=subprocess.DEVNULL
            )
            logging.info(f"Partition {partition} formatted as FAT32")

        except subprocess.CalledProcessError as e:
            logging.error(f"Error: {e}")

    def copy_files_to_usb(self):
        """Copies the files from the ISO to the USB device & writes the UEFI NTFS image to 2nd partition."""

        try:
            partition = f"{self.usb_device}2"
            with open(partition, "wb") as device:
                with open(self.uefi_ntfs_img_path, "rb") as img:
                    device.write(img.read())
            logging.info(f"UEFI NTFS image written to {partition}")
        except Exception as e:
            logging.error(f"Error: {e}")