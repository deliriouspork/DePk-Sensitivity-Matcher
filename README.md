# DePk Sensitivity Matcher
A Python-based tool for matching mouse sensitivity between 3D games on Linux using evdev and uinput. Works on both X11 and Wayland.

Heavily inspired by [Kovaak's Sensitivity Matcher](https://github.com/KovaaK/SensitivityMatcher/).

## Installation
Only *officially* support on Arch as I havn't the means (nor the inclination) to test on other versions. Should work just swimmingly on *most* other distributions.

Due to the waylands security architecture this program **WILL NOT WORK** unless the user running the program is a member of the **input** group.

**WARNING:** Having your user be a member of the input group is generally not advised as it *can* make you more susceptible to keyloggers and other attacks. What I do, and what I'd recommend you do as well, is to run `newgrp input` in your terminal before starting the application. This adds your user to the input group **ONLY** for your current shell. 

### Arch:
```shell
git clone URL
cd cd DePk\ Sensitivity\ Matcher/
python main.py
```
Note: Requires python, python-evdev, and python-pyqt6.

## Usage
Run the tool and enter your sensitivity and game/engine. Open the game you wish to set your sensitivity in and press `ALT+BACKSPACE`. Fiddle with your sensitivity in-game until `ALT+BACKSPACE` performs a perfect (or close to a) 360 degree rotation.

## Todo (depending on if anyone actually uses this garbled together POS python code written by an inexperienced Forestry student in his free time)
* Add a configuration file
* Add error popups when something doesn't go right
* Add more presets
* Make my shit code less shit 

Special Note: Please be careful when running programs you've found online. Just because a project is open source does **NOT** mean that it is garunteed to be safe. I have basically written a key-logger just to match sensitivity in video games. If you are not competent in python and you have not personally removed my code, I'd recommend **NOT** running and installing this.