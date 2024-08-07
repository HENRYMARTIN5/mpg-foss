# AutoFOSS

100% automated FOSS data collection and analysis tool.

## Installation

This tool shares its dependencies and Python environment with the parent monorepo. Just follow the instructions in [that README](../README.md)

## Extra Device Config

Make sure the scale is at factory defaults, except for:
User -> COM1 -> Mode -> Continuous

Make sure the power supply has the following settings:

1. 24.0V, 2.0A, Range: 35V/3A (Static generator)
2. 12.0V, 1.8A, Range: 35V/3A - OCP off (Pump)
3. 12.0V, 0.830A, Range: 35V/3A - OCP off, OVP off (Valve)

Zero/tare the scale before beginning.

## Data Format and Viewing

AutoFOSS collects data in a similar manner to that created by the official Gator Operator Software, with a few changes. Here's the CSV format:

Timestamp: The time the data was collected
Elapsed: The time since the start of the script
Current Weight: The weight of the resevoir/bucket at the time of data collection
Sensor 1-8: The wavelength values of the sensors (in nanometers) at the time of data collection

You can view the data in your favorite spreadsheet program, or use the included `autofossviz.py` to open an interactive window to view the data. You can also add a custom visualizer for your data by adding your own class that inherits from plotters.plotter.Plotter and adding it to the `ALL_PLOTTERS` dict in `plotters/__init__.py` - see `weight_over_time.py` for an example.

## Adding a Device

In order to add a new component to your AutoFOSS setup (e.g. a second pump to increase drain speed), you will need to:

1. Create a new Python file in the `autofoss` directory that contains a class that inherits from `AutofossComponent` in `component.py`. This class should implement:
    - `__init__(self, other_components: dict, **kwargs)`: To create the component and store references to other components - initialization of your device and connection should be done here
    - `start(self)`: Start the device's operation, whatever that may be (non-blocking, so spin up a thread if necessary)
    - `stop(self)`: Stop the device's operation
    - `reset(self)`: Reset the device and disconnect. Any changes made by reset() should be undone in start().
2. Add your class (in the correct order) to the `components` dict in `autofoss.py` in the `main` function. For instance, if you have a new pump with a class `AutofossDrainpump`: `components['drainpump'] = AutofossDrainpump(components, ...)`.
3. Start and stop your class in the appropriate locations in `autofoss.py` - for instance, you might start your pump after starting the Gator (which also opens the valve) and stop it before stopping the Gator.
4. Add any necessary command-line arguments to `autofoss.py` to control your new device, and pass them to the initialization of your class (where you added it to the `components` dict).

## Usage

```plaintext
usage: autofoss.py [-h] [-s SCALE_PORT] [-p POWER_PORT] [-S] [-g] [--weight-timeout WEIGHT_TIMEOUT] [-b BUCKET_WEIGHT] [--pump-extra-runtime PUMP_EXTRA_RUNTIME] [-f] [-r] [-o OUT_DIR]

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
```

## Pre-Usage Checklist

1. Take the Gator out of its case and place it near the end of the fiber from the tank.
2. Take off the cap from the fiber. Leave the cap on the Gator screwed in.
3. Grab two lint-free wipes, fold them over on top of each other, and moisten them with isopropyl alcohol. Clean the end of the fiber until it appears clear under the fiber microscope.
4. Unscrew the Gator connector cap, and connect the now-clean fiber to the Gator and screw it in. Make sure to line up the notch correctly.
5. Connect the Gator to the computer via a USB-B to USB-A cable.
6. Connect the power supply to the Gator and press the power button in. Make sure that all 8 FBG status lights on the front are illuminated.
7. Connect the scale to power and verify the settings as described in the Extra Device Config section.
8. Connect the scale to the computer via an RS-232 to USB cable.
9. Place a small piece of foam or another prop on one side of the bucket to tilt it slightly in one direction. This will help the water drain out of the bucket more easily when refilling.
10. Make sure the bucket on the scale is empty, except for the tubing and whatever weight is necessary to keep it in place. Press the zero/tare button on the scale to zero it out.
11. Make sure the tubing is connected in the following way:
    - Bucket -> Pump -> Top of Tank
    - Bottom of Tank -> Valve -> Bucket
    - Vent on Tank -> Running to a bucket at a higher elevation than the tank
12. Make sure the tubing is secure and won't come loose during operation.
13. Connect the power supply to the computer over USB.
14. Ensure all devices are connected to the power supply.
15. Turn on the power supply, and verify the voltags are set as described in the Extra Device Config section.
16. Turn on the high-voltage amplifier (there's a switch on the back right).
17. Run the script!
