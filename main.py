import requests
from concurrent.futures import ThreadPoolExecutor
import datetime
import time
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from playsound import playsound
from os import path

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def get_limit():
    if path.exists("config"):
        with open("config", "r") as f:
            return str(f.read())
    while "The answer is invalid.":
        reply = (
            str(input("Do you want to set a time limit to stop announcing? [y|n]: "))
            .lower()
            .strip()
        )
        if reply[0] == "y":
            while "Input not a number.":
                try:
                    limit = int(
                        input("What minute do you want to stop announcing at? ")
                    )
                    with open("config", "w") as f:
                        f.write(str(limit))
                    return limit
                except ValueError:
                    print("Please input a valid number.")
                    continue
        if reply[0] == "n":
            with open("config", "w") as f:
                f.write("False")
            return "False"
        print("The answer is invalid.")


def announce(minute, history):
    beforelastwave = history.pop(0)
    lastwave = history[0]
    if minute < 15:
        if lastwave == True:
            print("Detected Caster Wave.")
            playsound("audio/casterwave.mp3")
            return False
        elif lastwave == False and beforelastwave == False:
            print("Detected Cannon Wave.")
            playsound("audio/cannonwave.mp3")
            return True
        elif lastwave == False and beforelastwave == True:
            print("Detected Caster Wave.")
            playsound("audio/casterwave.mp3")
            return False
    elif minute > 15 and minute < 25:
        if lastwave == True:
            print("Detected Caster Wave.")
            playsound("audio/casterwave.mp3")
            return False
        elif lastwave == False:
            print("Detected Cannon Wave.")
            playsound("audio/cannonwave.mp3")
            return True
    elif minute > 25:
        print("Detected Cannon Wave.")
        playsound("audio/cannonwave.mp3")
        return True


def main(limit):
    print("Waiting for game...")
    history = [False, True]
    executor = ThreadPoolExecutor(max_workers=2)
    try:
        requests.get(
            "https://127.0.0.1:2999/liveclientdata/allgamedata", verify=False
        ).json()["gameData"]
        print("Connected successfully!")
    except:
        raise KeyError
    while True:
        starttime = datetime.timedelta(
            seconds=requests.get(
                "https://127.0.0.1:2999/liveclientdata/allgamedata", verify=False
            ).json()["gameData"]["gameTime"]
        )
        for x in range(10):  # syncing every 10 seconds
            x += 1
            newtime = starttime + datetime.timedelta(seconds=x)
            minute = int(newtime.seconds / 60)
            second = int(newtime.seconds % 60)
            try:
                if minute >= int(limit):
                    exit("Reached limit of " + str(minute) + " minutes. Closing...")
            except ValueError:
                pass
            if (second == 5 or second == 35) and minute > 0:
                history.append(executor.submit(announce, minute, history).result())
            time.sleep(1)


print(
    """
    ___             ___     _       __               
   /   | __  ______/ (_)___| |     / /___ __   _____ 
  / /| |/ / / / __  / / __ \ | /| / / __ `/ | / / _ \\
 / ___ / /_/ / /_/ / / /_/ / |/ |/ / /_/ /| |/ /  __/
/_/  |_\__,_/\__,_/_/\____/|__/|__/\__,_/ |___/\___/ 
"""
)

while True:
    try:
        main(get_limit())
        break
    except (requests.exceptions.ConnectionError, KeyError):
        time.sleep(5)
        continue