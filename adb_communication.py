import subprocess
import time
from typing import List, Tuple, Union

from helper import get_waiting


class Device:
    wireless: bool
    serial: str

    def __init__(self, wireless: bool, serial: str):
        self.wireless = wireless
        self.serial = serial

    def work(self):
        if self.wireless:
            print(f"Working with wireless device! IP: {self.serial}")
        else:
            print(f"Working with USB device! Serial: {self.serial}")

    def shell(self, command: str) -> str:
        return run_adb_command(['-s', self.serial, 'shell', command])

    @property
    def ip(self) -> str:
        try:
            info = self.shell("ip addr show wlan0")
            return info.split('inet ')[1].split('/')[0]
        except IndexError:
            print("Could not find IP address of the device!")
            exit()

    def vibrate(self):
        # This might not work on all devices
        # If it does then, cool! :3
        self.shell("cmd vibrator vibrate 100")


def run_adb_command(inputs: Union[List[str], Tuple[str, ...]]) -> str:
    process = subprocess.Popen(["adb.exe", *inputs], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout.decode('utf-8').strip()


def check_devices() -> Tuple[Device, ...]:
    devices = run_adb_command(['devices'])
    device_listings = devices.split('\n')[1:]
    return tuple(
        Device(
            wireless=len(device_listing.split('.')) == 4,
            serial=device_listing.split('\t')[0]
        )
        for device_listing in device_listings
    )

def wait_for_no_devices(silent: bool = False):
    devices = check_devices()
    i = 0
    while devices:
        if not silent:
            print(f"Please disconnect all devices {get_waiting(i)}", end='\r')
        devices = check_devices()
        i += 1
        time.sleep(.1)

def wait_for_device(prompt: str, confirm: bool = True, require_wireless: bool = False) -> Device:
    devices = check_devices()
    i = 0
    while not devices:
        print(f"{prompt} {get_waiting(i)}", end='\r')
        devices = check_devices()
        i += 1
        time.sleep(.1)

    device = devices[0]

    if confirm:
        if require_wireless and not device.wireless:
            print(f"You've connected {device.serial} via USB. Please disconnect it!")
            wait_for_no_devices(True)
            return wait_for_device(prompt, confirm, require_wireless)
        elif device.wireless:
            print(f"You've connected the device wirelessly! IP: {device.serial}")
            device.vibrate()
            exit()


    return device
