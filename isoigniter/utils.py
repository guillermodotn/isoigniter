import subprocess


def get_usb_devices():
    result = subprocess.run(
        ["lsblk", "-nd", "-o", "NAME"], capture_output=True, text=True
    )
    devices = result.stdout.strip().split("\n")
    return [f"/dev/{dev}" for dev in devices]
