# region Docstring
"""
Script to automatically take full recordings of drains. Logs data from the Gator and scale to a CSV file and automatically enables noise generation and the valve with the MX100TP.

Make sure the scale is at factory defaults, except for:
User -> COM1 -> Mode -> Continuous

Procedure:
1. Ensure the Gator, power supply, and scale are connected and turned on.
2. Run this script.
3. This script will automatically start everything neccesary to record data, and will refill the tank as needed. You shouldn't need to do anything.
4. You can stop the script at the next cycle gracefully by pressing CTRL+C. If you want to stop the script immediately, press CTRL+C a second time.
"""

# region Gator API installatino
try:
    from gator_api.gator_api import GatorApi
except ImportError:
    import os
    print("Gator API not found. Attempting to install...")
    if os.path.exists("gator_api-1.0.0-py3-none-any.whl"):
        os.system("pip install gator_api-1.0.0-py3-none-any.whl")
    elif os.path.exists("../gator_api-1.0.0-py3-none-any.whl"):
        os.system("pip install ../gator_api-1.0.0-py3-none-any.whl")
    else:
        print("Error: Gator API not found. The latest version of the Gator API can be found in the Python API folder of the MPG-FOSS Google Drive. \
As this API is strictly proprietary, it cannot be included in this repository. Please download the whl file and place it at the root of the mpg-foss repo, \
and it will be automatically installed the next time you run this script.")
        exit(1)

# region API init
import scale
import gator
import power
import refill
from csv_util import write_csv
import argparse
import traceback
from component import ComponentManager

# region Refill
def do_refill(components: ComponentManager):
    print('Refilling tank...')
    components.get('power').off(3)
    components.get('refill').start()
    res = components.get('refill').wait_for_refill()
    if not res:
        print("Refill failed! Pausing for human intervention. Press ENTER to continue.")
        input()
    print('Tank refilled.')
    try:
        print('Resetting components...')
        try:
            components.get('power').stop()
        except ValueError:
            pass
        components.get('gator').reset()
        components.get('scale').reset()
    except Exception as e:
        print("Error resetting components:", e)
        traceback.print_exc()
        components.get('scale').stop()
        components.get('power').stop()

def do_nodrain(args) -> int:
    print("Initializing components...")
    components = ComponentManager()
    components.add('power', \
                    power.AutofossPowersupply(components, address=args.power_port), \
                    priority=3)
    components.add('scale', \
                    scale.AutofossScale(components, log_scale=not args.no_log_scale, default_port=args.scale_port, weight_timeout=args.weight_timeout, full_weight=args.full_tank_weight), \
                    priority=2)
    components.add('gator', \
                    gator.AutofossGator(components, auto_end=True, log_gator=args.log_gator, nodrain=True), \
                    priority=1)
    components.start_all()
    components.get('scale').wait_for_thread()
    print("Shutting down...")
    components.stop_all()
    print('Everything is off. Writing samples to CSV...')
    file_name = write_csv(components.get('gator').samples, out_folder=args.out_dir)
    print(f'CSV file written: {file_name}')
    return 0

# region Main 
def main() -> int:
    """
Make sure the scale is at factory defaults, except for:
User -> COM1 -> Mode -> Continuous

Procedure for use:
1. Ensure the Gator, power supply, and scale are connected and turned on.
2. Run this script.
3. This script will automatically start everything neccesary to record data, and will refill the tank as needed. You shouldn't need to do anything.
4. You can stop the script at the next cycle gracefully by pressing CTRL+C. If you want to stop the script immediately, press CTRL+C a second time.
    """

    # region Argument parsing
    parser = argparse.ArgumentParser(description="AutoFOSS - 100% automated FOSS data collection", epilog=main.__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-s", "--scale-port", help="COM port for the scale", default="COM7")
    parser.add_argument("-p", "--power-port", help="COM port for the power supply", default="COM9")
    parser.add_argument("-S", "--no-log-scale", help="Don't log scale data to console", action="store_true")
    parser.add_argument("-g", "--log-gator", help="Log Gator data to console (warning: absolutely murders performance!)", action="store_true")
    parser.add_argument("--weight-timeout", help="Time in seconds before considering the tank drained", type=int, default=8)
    parser.add_argument("-b", "--bucket-weight", help="Weight of the bucket when empty (with a bit of wiggle room) in lbs", type=float, default=1.0)
    parser.add_argument("--pump-extra-runtime", help="How long to run the pump for (in seconds) additionally after the refill threshold is reached", type=float, default=5.0)
    parser.add_argument("-f", "--refill-first", help="Immediately jump to refilling the tank at the start of the script's cycle", action="store_true")
    parser.add_argument("-r", "--refill", help="Just refill the tank and exit", action="store_true")
    parser.add_argument("-o", "--out-dir", help="Output directory for CSV files", default="drains")
    parser.add_argument("--no-drain", help="Don't drain the tank, just take a continuous data sample", action="store_true")
    parser.add_argument("--full-tank-weight", help="Weight of the tank when full in lbs", type=float, default=15.45)
    args = parser.parse_args()
    
    # region Immediate arguments
    if args.no_drain:
        return do_nodrain(args)
    
    if args.refill:
        components = ComponentManager()
        components.add('power', \
                        power.AutofossPowersupply(components, address=args.power_port), \
                        priority=3)
        components.add('scale', \
                        scale.AutofossScale(components, log_scale=not args.no_log_scale, default_port=args.scale_port, weight_timeout=args.weight_timeout, full_weight=args.full_tank_weight), \
                        priority=2)
        components.add('gator', \
                        gator.AutofossGator(components, auto_end=True, log_gator=args.log_gator), \
                        priority=1)
        components.add('refill', \
                        refill.AutofossRefiller(components, threshold=args.bucket_weight, extra=args.pump_extra_runtime), \
                        priority=-1)
        components.start('power', 'scale')
        do_refill(components)
        return 0

    if args.log_gator:
        print("WARNING: Don't be an idiot and read this!")
        print("Logging Gator data to the console will kill performance and make the script run slower than a snail on a salt flat. You have been warned.")
        print("This feature should only *ever* be used for debugging purposes. If you're not debugging, turn it off.")
        yn = input("Do you really, actually, seriously want to continue? [y/N] ")
        if yn.lower() != 'y':
            return 1

    # region Components
    components = ComponentManager()
    ########### Place your components here! ###########
    components.add('power', \
                    power.AutofossPowersupply(components, address=args.power_port), \
                    priority=3)
    components.add('scale', \
                    scale.AutofossScale(components, log_scale=not args.no_log_scale, default_port=args.scale_port, weight_timeout=args.weight_timeout, full_weight=args.full_tank_weight), \
                    priority=2)
    components.add('gator', \
                    gator.AutofossGator(components, auto_end=True, log_gator=args.log_gator), \
                    priority=1)
    components.add('refill', \
                    refill.AutofossRefiller(components, threshold=args.bucket_weight, extra=args.pump_extra_runtime), \
                    priority=-1)

    # region Main loop
    running = True
    force_shutdown = False
    jump_refill = args.refill_first
    while running:
        components.start('power')

        if jump_refill:
            do_refill(components)
            jump_refill = False
            continue

        components.start('gator', 'scale')

        stop_next, force_shutdown = components.get('scale').wait_for_thread()

        print("Shutting down...")
        components.stop('gator', 'scale')
        if force_shutdown:
            components.stop('power')     
        print('Everything is off. Writing samples to CSV...')
        file_name = write_csv(components.get('gator').samples, out_folder=args.out_dir)
        print(f'CSV file written: {file_name}')
        if force_shutdown:
            return 128 # SIGINT

        if stop_next:
            print('Gracefully stopping.')
            for component in components.values():
                component.stop()
            return 0

        do_refill(components)
        print('And now, again!')
    return 0

# region Entry
if __name__ == '__main__':
    try:
        exit(main())
    except SystemExit:
        pass
    except:
        traceback.print_exc()
        exit(1)