import subprocess


def get_usb_devices():
    result = subprocess.run(
        ["lsblk", "-nd", "-o", "NAME"], capture_output=True, text=True
    )
    devices = result.stdout.strip().split("\n")
    return [f"/dev/{dev}" for dev in devices]


def has_mbr_signature(iso_path):
    with open(iso_path, "rb") as f:
        mbr = f.read(512)  # Read first 512 bytes (MBR sector)
    return mbr[510:512] == b"\x55\xaa"  # Check boot signature

