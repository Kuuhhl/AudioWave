import requests
from concurrent.futures import ThreadPoolExecutor
import datetime
import time
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from playsound import playsound
from os import path
import psutil

# API doesn't have valid SSL certificate
# ► Disabled warnings to prevent console getting spammed every call
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def is_process_running(process_name):
    """[Checks if process is running]

    Args:
        process_name ([string]): [Process name to look for]

    Returns:
        [boolean]: [True = running; None = Not running]
    """
    for process in psutil.process_iter():
        if process.name() == process_name:
            return True


def get_limit():
    # Read config-file if there is one
    if path.exists("config"):
        # Return time limit
        with open("config", "r") as f:
            if f.read() == "":
                return None
            return f.read()
    # Loop to keep asking until valid answer is given
    while True:
        # Ask if user wants to set time limit (normalize input to account for upper/lowercase)
        reply = (
            str(input("Do you want to set a time limit to stop announcing? [y|n]: "))
            .lower()
            .strip()
        )
        # Execute if user wants to create time limit
        if reply == "y":
            # Loop to keep asking until valid answer is given
            while True:
                try:
                    # Get input and convert it to integer
                    limit = int(
                        input("What minute do you want to stop announcing at? ")
                    )
                    # Re-ask user if provides negative number
                    if limit < 0:
                        print("Please input a positive number.")
                        continue
                    # Write limit to config-file
                    with open("config", "w") as f:
                        f.write(str(limit))
                    return limit
                # If can't be converted to integer ► it's not valid number
                # Re-ask user
                except ValueError:
                    print("Please input a valid number.")
                    continue
        # Execute if user doesn't want to create time limit
        # Create empty text file/delete text file content
        if reply == "n":
            with open("config", "w") as f:
                f.write("")
            return None
        # If the user selects none of the options y|n, print error message
        print("The answer is invalid.")


def announce(minute, history):
    """[Calculates incoming wave and announces it (uses seperate thread to prevent time-dilation)]

    Args:
        minute ([integer]): [minutes from game-time]
        history ([list]): [holds the last two waves]

    Returns:
        [boolean]: [type of the announced minion wave]
    """
    # Remove first item of list (first wave) and save it's value to beforelastwave
    beforelastwave = history.pop(0)
    # save first value from the new list to lastwave
    lastwave = history[0]
    # Checks minute timer and calculates the new minion wave: according to these rules:

    # Under 15 minutes: ---------------------------------
    # Interval: Caster;Caster;Cannon
    # Between 15 and 25 minutes: ------------------------
    # Interval: Caster;Cannon
    # After 25 minutes: ---------------------------------
    # Interval: Cannon

    # after calculating, plays the corresponding audio-file.
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
    elif minute >= 15 and minute < 25:
        if lastwave == True:
            print("Detected Caster Wave.")
            playsound("audio/casterwave.mp3")
            return False
        elif lastwave == False:
            print("Detected Cannon Wave.")
            playsound("audio/cannonwave.mp3")
            return True
    elif minute >= 25:
        print("Detected Cannon Wave.")
        playsound("audio/cannonwave.mp3")
        return True


def main(limit):
    # Check for API availiability
    try:
        requests.get(
            "https://127.0.0.1:2999/liveclientdata/allgamedata", verify=False
        ).json()["gameData"]
        print("Connected successfully!")
    # raise error if not successful
    except:
        raise KeyError
    # Set default value
    history = [False, True]
    # Initialize second thread
    executor = ThreadPoolExecutor(max_workers=2)
    # main loop to test for minion waves
    while True:
        # Get current game-time from API
        starttime = datetime.timedelta(
            seconds=requests.get(
                "https://127.0.0.1:2999/liveclientdata/allgamedata", verify=False
            ).json()["gameData"]["gameTime"]
        )
        # Loop to execute code without synchronizing time ► syncing every 10 seconds
        # This is done to stop the program from sending too many requests ► more ressource-efficient
        for x in range(10):
            # Add 1 second to current time
            newtime = starttime + datetime.timedelta(seconds=x + 1)
            # Get minutes from time (e.g. 05:14 ► 5)
            minute = int(newtime.seconds / 60)
            # Get seconds from time (e.g. 05:14 ► 14)
            second = int(newtime.seconds % 60)
            # Check if time limit is defined (not 'None'); then test if it is reached
            if limit != None:
                if minute >= int(limit):
                    # Close program if reached
                    exit("Reached limit of " + str(minute) + " minutes. Closing...")
            # Test if Wave spawns
            if (second == 5 or second == 35) and minute > 0:
                # Call announcer function and add the result to history (will influence following announcements)
                history.append(executor.submit(announce, minute, history).result())
            # Wait a second for next iteration
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
# Ask user for time limit / read from file
limit = get_limit()

print("Waiting for game to start...")
# Loop to check for API initialization
while True:
    # Check for Game-process
    if is_process_running("League of Legends.exe"):
        try:
            main(limit)
            break
        # Catch Connection-Error (happens when the Game didn't initialize the API yet)
        except (requests.exceptions.ConnectionError, KeyError):
            continue
    # Execute the loop once every 10 Seconds
    time.sleep(10)
