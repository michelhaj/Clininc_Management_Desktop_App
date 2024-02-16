import os
import sys
import random
import time


def getMachine_addr():
    os_type = sys.platform.lower()
    if "win" in os_type:
        command = "wmic bios get serialnumber"
    elif "linux" in os_type:
        command = "hal-get-property --udi /org/freedesktop/Hal/devices/computer --key system.hardware.uuid"
    elif "darwin" in os_type:
        command = "ioreg -l | grep IOPlatformSerialNumber"
    return os.popen(command).read().replace("\n", "").replace("  ", "").replace(" ", "")


# output machine serial code: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXX
print(getMachine_addr())


import random


def verify(key):
    global score
    score = 0
    check_digit = key[2]
    check_digit_count = 0
    chunks = key.split("-")
    for chunk in chunks:
        if len(chunk) != 4:
            return False
        for char in chunk:
            if char == check_digit:
                check_digit_count += 1
            score += ord(char)
    if score > 1700 and score < 1800 and check_digit_count == 3:
        return True
    else:
        return False


def generate():
    global key
    key = ""
    section = ""
    check_digit = 0
    alphabet = "abcdefghijklmnopqrstuvwxyz1234567890"
    while len(key) < 25:
        char = random.choice(alphabet)
        key += char
        section += char
        if len(section) == 4:
            key += "-"
            section = ""
    key = key[:-1]
    return key


flag = True
b = generate()
while flag:
    if verify(b):
        print(b)
        print(score)
        flag = False
    else:
        b = generate()
