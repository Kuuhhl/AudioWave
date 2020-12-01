import requests
import threading
from concurrent.futures import ThreadPoolExecutor
import datetime
import time
from requests.packages.urllib3.exceptions import (
    InsecureRequestWarning,
    NewConnectionError,
    MaxRetryError,
)
from playsound import playsound


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def announce(minute, history):  # True = Cannon; False = Caster
    beforelastwave = history.pop(0)
    lastwave = history[0]
    if minute < 20:
        if lastwave == True:
            print("Caster Wave!")
            playsound("casterwave.mp3")
            return False
        elif lastwave == False and beforelastwave == False:
            print("Cannon Wave!")
            playsound("cannonwave.mp3")
            return True
        elif lastwave == False and beforelastwave == True:
            print("Caster Wave!")
            playsound("casterwave.mp3")
            return False
    elif minute > 20 and minute < 35:
        if lastwave == True:
            print("Caster Wave!")
            playsound("casterwave.mp3")
            return False
        elif lastwave == False:
            print("Cannon Wave!")
            playsound("cannonwave.mp3")
            return True
    elif minute > 20:
        print("Cannon Wave!")
        playsound("cannonwave.mp3")
        return True


def main():
    history = [False, True]
    executor = ThreadPoolExecutor(max_workers=2)
    while True:
        starttime = datetime.timedelta(
            seconds=requests.get(
                "https://127.0.0.1:2999/liveclientdata/allgamedata", verify=False
            ).json()["gameData"]["gameTime"]
        )
        for x in range(10):
            x += 1
            newtime = starttime + datetime.timedelta(seconds=x)
            minute = int(newtime.seconds / 60)
            second = int(newtime.seconds % 60)
            if (second == 5 or second == 35) and minute > 0:
                history.append(executor.submit(announce, minute, history).result())
            time.sleep(1)


while True:
    try:
        main()
        break
    except (requests.exceptions.ConnectionError, KeyError):
        print("Not connected yet...")
        time.sleep(1)
        continue