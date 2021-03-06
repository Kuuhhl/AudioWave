# AudioWave for League of Legends
This tool allows you to be notified audibly every time a minion wave spawns. It plays an announcement on every time minions spawn according to the type of minion wave spawning (e.g."Cannonwave").
## Installation (not needed for `.exe` binaries)
* Install `Python 3.8`
* Install dependencies:
```
pip install requests
pip install playsound
```
## Usage
* Run `main.py` or the binary `.exe` before entering the game.
* If it's your first time running the program, you will have the option to specify a time limit to close the program automatically on a given time.
* Enjoy!

### Disclaimer
Please make sure to restart the app after every game until I implement a solution.

## How does it work?
* The program reads the ingame time from the live ingame API by Riot.
* A timer is started that is synced regularly to prevent too much time dilation.
* Every time a wave should spawn, the program predicts the next wave by analyzing the last two waves.
* The predicted wave is announced.

## I don't like the audio. Can I change it?
To change the audio-file:
* navigate to the `/audio` in the script's folder 
* replace the `.mp3` files with your own. Make sure not to change the file names though.
## How do I change the time limit?
To change the time limit:
* Navigate to the script's folder
* Delete `config` file.

## TODO
* Implement a feature to use this without restarting after games.
* Implement a feature to start this when game already started.
