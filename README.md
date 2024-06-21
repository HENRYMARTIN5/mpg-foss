# MPG-FOSS Monorepo

Contains code for various utilities related to Modal Propellant Gauging via a Fiber Optic Sensing System.

## Installation

### Prerequisites

- Python 3.8 (use pyenv if you're on a system with a different version of Python installed, it should automatically switch to 3.8 when you cd into the repo)
- Pip
- A venv (reccommended, but not strictly necessary)
- Windows, Arch Linux, Ubuntu 20.04 LTS, Debian Stable, or Raspberry Pi OS (you can ignore warnings if you know what you're doing on another distro)

### Actually Installing

1. Clone the repo: `git clone https://github.com/HENRYMARTIN5/mpg-foss.git`
2. cd into the repo: `cd mpg-foss`
3. Create a venv: `python -m venv env`, then activate it: `source env/bin/activate` on *nix or `env\Scripts\activate` on Windows
4. Open the launcher: `python launcher.py`
5. Install the dependencies from the menu. If you're on a Raspberry Pi, you can ignore the warnings about distro compatibility.
6. Profit?

## Utilities

> [!WARNING]
> Frankly, the launcher is terrible - you should just run each of these from the command-line. The launcher is only there for people who don't know how to use a command-line interface, which *shouldn't* be you if you're working on this project.

> [!NOTE]
> Other older tools are still available in `old/`, but are generally not supported and may not work.

### AutoFOSS

The 100% automated FOSS data collection and analysis tool.

To run: `python autofoss/autofoss.py`

Help:

```plaintext
usage: autofoss.py [-h] [-s SCALE_PORT] [-p POWER_PORT] [-S] [-g] [--weight-timeout WEIGHT_TIMEOUT] [-b BUCKET_WEIGHT] [--pump-extra-runtime PUMP_EXTRA_RUNTIME] [-f] [-r] [-o OUT_DIR]

AutoFOSS - 100% automated FOSS data collection

optional arguments:
  -h, --help            show this help message and exit
  -s SCALE_PORT, --scale-port SCALE_PORT
                        COM port for the scale
  -p POWER_PORT, --power-port POWER_PORT
                        COM port for the power supply
  -S, --no-log-scale    Don't log scale data to console
  -g, --log-gator       Log Gator data to console (warning: absolutely murders performance!)
  --weight-timeout WEIGHT_TIMEOUT
                        Time in seconds before considering the tank drained
  -b BUCKET_WEIGHT, --bucket-weight BUCKET_WEIGHT
                        Weight of the bucket when empty (with a bit of wiggle room) in lbs
  --pump-extra-runtime PUMP_EXTRA_RUNTIME
                        How long to run the pump for (in seconds) additionally after the refill threshold is reached
  -f, --refill-first    Immediately jump to refilling the tank at the start of the script's cycle
  -r, --refill          Just refill the tank and exit
  -o OUT_DIR, --out-dir OUT_DIR
                        Output directory for CSV files

Make sure the scale is at factory defaults, except for:
User -> COM1 -> Mode -> Continuous

Procedure for use:
1. Ensure the Gator, power supply, and scale are connected and turned on.
2. Run this script.
3. This script will automatically start everything neccesary to record data, and will refill the tank as needed. You shouldn't need to do anything.
4. You can stop the script at the next cycle gracefully by pressing CTRL+C. If you want to stop the script immediately, press CTRL+C a second time.
```
