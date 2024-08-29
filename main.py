import os
import sys
import time

import colorama
import psutil
import adb_communication as adb
from tqdm import tqdm
from colorama import Fore, Style, Back

from helper import exit_program

colorama.init()

# Settings
# CHANGE THESE AS PER USAGE
ADB_EXE = 'adb.exe'
USE_IN_UNITY_ADB = True
UNITY_AUTO_CONFIRM = True
AUTO_CONFIRM = True
# Settings

# Global variables
PROGRESS_PREFIX = f'{Back.LIGHTBLACK_EX}{Fore.LIGHTGREEN_EX}'
PROGRESS_SUFFIX = f'{Fore.RESET}{Back.RESET}'
ADB_PATH = f'{Style.DIM}{Fore.LIGHTYELLOW_EX}{{0}}{Fore.LIGHTWHITE_EX}{Style.NORMAL}'
Y_OR_NO = ' [y/n] '
PIDS = psutil.pids()
BAR_FORMAT = f'{PROGRESS_PREFIX}{{l_bar}}{{bar}}| {{n_fmt}}/{{total_fmt}}{PROGRESS_SUFFIX}'
PROGRESS = tqdm(
    total=len(PIDS),
    desc='Searching for ADB process',
    file=sys.stdout,
    bar_format=BAR_FORMAT
)
adb_path = None
confirmed = False


# Functions
def yes_or_no_raw(question) -> bool:
    while True:
        reply = str(input(question)).lower().strip()
        if not reply:
            continue
        if reply[0] == 'y':
            return True
        if reply[0] == 'n':
            return False


def yes_or_no(question) -> bool:
    return yes_or_no_raw(question + Y_OR_NO)


def clear_progress():
    progress_length = len(str(PROGRESS))
    print(f'\r{" " * progress_length}', end='\r')


# Sorry, but Yes or no `progress` is the name of the function :3
def yes_or_no_p(question) -> bool:
    length = len(question)
    clear_progress()
    answer = yes_or_no(f'\r{PROGRESS_PREFIX}{question}{PROGRESS_SUFFIX}')
    print(end='\033[F')
    return answer


def check_unity() -> bool:
    global confirmed
    try:
        version = adb_path.split('\\Editor\\', maxsplit=2)[1]
        PROGRESS.write(
            f"{Style.BRIGHT}Found your {Back.LIGHTBLACK_EX}Unity{Back.RESET} version {Fore.BLUE}{version}{Fore.RESET}{Style.NORMAL}")
        confirmed = UNITY_AUTO_CONFIRM
    except ValueError:
        return False
    else:
        return True


# Find ADB
for pid in PIDS:
    PROGRESS.update(1)
    adb_path = None
    try:
        process = psutil.Process(pid)
    except psutil.NoSuchProcess:
        continue
    if process.name() == ADB_EXE:
        adb_path = process.exe()
        if USE_IN_UNITY_ADB:
            if not check_unity():
                continue
            if UNITY_AUTO_CONFIRM:
                confirmed = True
            else:
                PROGRESS.write(ADB_PATH.format(adb_path))
                confirmed = yes_or_no_p("Do you want to use this ADB path in Unity?")
        elif AUTO_CONFIRM:
            confirmed = True
        else:
            PROGRESS.write(ADB_PATH.format(adb_path))
            confirmed = yes_or_no_p("Do you want to use this ADB path?")
        if confirmed:
            break
else:
    PROGRESS.write("ADB not found")
    PROGRESS.close()
    exit_program()
if not confirmed:
    PROGRESS.write("No ADB path confirmed")
    PROGRESS.close()
    exit_program()
else:
    PROGRESS.set_description(f"ADB path confirmed! ")
    PROGRESS.update(PROGRESS.total - PROGRESS.n)
    PROGRESS.close()

print("\nUsing ADB in:", ADB_PATH.format(adb_path))

os.chdir(os.path.dirname(adb_path))

device = adb.wait_for_device("Please connect your device through USB")
device.work()
connection_ip = device.ip

print(adb.run_adb_command(('tcpip', '5555')))
time.sleep(5)  # Accounting for delay when using adb

adb.wait_for_no_devices()
time.sleep(2)  # Accounting for delay when using adb

adb.run_adb_command(('connect', connection_ip))
device = adb.wait_for_device("Device should connect wirelessly", require_wireless=True)
