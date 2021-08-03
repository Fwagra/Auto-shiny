# Auto-Shiny

Little project automating the egg hatching, thus finding shinies, in the Nintendo Switch game Pokémon Sword & shield. It can be ran from command line or a web interface.

[Video demo on Youtube](https://www.youtube.com/watch?v=aUCLPIf0x_8)

It's based on the [SwitchInputEmulator](https://github.com/wchill/SwitchInputEmulator) project.

## Prerequisites

- A flashed Arduino UNO R3/Micro or Teensy
- A USB-to-UART converter. You can buy one [here](https://www.amazon.com/HiLetgo-FT232RL-Converter-Adapter-Breakout/dp/B00IJXZQ7C) or [here](https://www.amazon.fr/gp/product/B07R17BMTL/ref=ppx_yo_dt_b_asin_title_o02_s00?ie=UTF8&psc=1)
- A linux-based system
- Python, pip3, pyserial
- Apache2 and PHP (web interface only)

## Setup

- Flash the Arduino using the [SwitchInputEmulator guide](https://github.com/wchill/SwitchInputEmulator).
- Connect the Arduino and the converter using this [wiring guide](img/wiring.png).
- Connect the Arduino to the computer and the converter to the Switch's dock using USB cables.
- Install Python3 : `sudo apt-get install python3`
- Install pip3 : `sudo apt-get install python3-pip`
- Install pyserial : `sudo -H pip3 install pyserial`
- Find the port of the Arduino on your system (usually `/dev/ttyUSB0` or `/dev/ttyUSB1`)
- Clone this repository (in `/var/www/html` if you want to use the web interface)

### For the web interface

- Install Apache2 : `sudo apt-get install apache2`
- Install PHP : `sudo apt-get install php7.3`
- ⚠️ Apache must be in the sudoers file, so take care your computer is not reachable from the outside.
- Open the sudoers file with `sudo nano /etc/sudoers` and add this line  `www-data ALL=(ALL) NOPASSWD: ALL`. 

## Usage 

### Game prerequisites

- Your text display must be set to **fast**
- The "Team/Box" setting must be set to **manual choice**
- To hatch eggs, you must go to the **Bridge Field** Nursery and have 5 pokémons in your team.
- The first one must have a _Flame Body_ or _Magma Armor_ ability
- You must not be on your bike
- Your menu's cursor must be on the *map icon*
- To release pokémons, you must select the top left slot of a box

### Command line

In the project folder, run the following command replacing the port with your : 
```
python3 shiny.py --port=/dev/ttyUSB0
```
It will display a prompt waiting for your command.

**Pick and hatch**

Follow the _game prerequisites_ and entrust your pokémons to the Nursery. Walk until you get an egg. Then place your character right in front of the Nursery helper, without the bike, then dock your switch and run the script.

Type the  `pnh` command, then the number of eggs you wanna hatch. Look for the pokemon your breeding in [this file](pokemon.json) to know the needed  number of cycles.


**Release** 

In the storage, select the first slot of the box you want to release. Then dock your Switch and run the script.

Type the `release` command, then the number of pokémons you want to release.

### Web Interface

Clone the repository in the document root folder (ex: `/var/www/html`). Go to http://localhost/Auto-shiny on your browser and fill the fields. 

You must follow the same prerequisites as the command line version.