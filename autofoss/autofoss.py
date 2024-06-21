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

import scale
import gator
import power
import refill
from csv_util import write_csv
import argparse

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
    parser = argparse.ArgumentParser(description="AutoFOSS - 100% automated FOSS data collection", epilog=main.__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--scale-port", help="COM port for the scale", default="COM7")
    parser.add_argument("--power-port", help="COM port for the power supply", default="COM9")
    parser.add_argument("--no-log-scale", help="Don't log scale data to console", action="store_false")
    parser.add_argument("--log-gator", help="Log Gator data to console (warning: absolutely murders performance!)", action="store_true")
    parser.add_argument("--weight-timeout", help="Time in seconds before considering the tank drained", type=int, default=8)
    parser.add_argument("--bucket-weight", help="Weight of the bucket when empty (with a bit of wiggle room) in lbs", type=float, default=3.65) # NOTE: this is with the 1kg weight inside the bucket to hold down the pump hose, which is a stupid solution
    args = parser.parse_args()

    if args.log_gator:
        print("WARNING: Don't be an idiot and read this!")
        print("Logging Gator data to the console will kill performance and make the script run slower than a snail on a salt flat. You have been warned.")
        print("This feature should only *ever* be used for debugging purposes. If you're not debugging, turn it off.")
        yn = input("Do you really, actually, seriously want to continue? [y/N] ")
        if yn.lower() != 'y':
            return 1

    components = {}
    components['scale'] = scale.AutofossScale(components, log_scale=not args.no_log_scale, default_port=args.scale_port)
    components['gator'] = gator.AutofossGator(components, auto_end=True, log_gator=args.log_gator)
    components['power'] = power.AutofossPowersupply(components, address=args.power_port) # NOTE: no start() or stop() methods
    components['refill'] = refill.AutofossRefiller(components, threshold=args.bucket_weight)

    running = True
    interrupted = False
    force_shutdown = False
    while running:
        if not interrupted:
            components['gator'].start()
            components['scale'].start()
        try:
            while components['scale'].thread_running:
                pass
        except KeyboardInterrupt:
            print("Interrupted!")
            if not interrupted:
                print("Press CTRL+C again to force shutdown. This script will sto gracefully after this drain.")
                interrupted = True
                continue
            print("Forcing shutdown...")
            force_shutdown = True
        print("Shutting down...")
        components['gator'].stop()
        components['scale'].stop()
        if force_shutdown:
            components['power'].stop()
            return 128 # SIGINT
        print('Everything is off. Writing samples to CSV...')
        file_name = write_csv(components['gator'].samples)
        print(f'CSV file written: {file_name}')
        if not interrupted:
            print('Refilling tank...')
            components['refill'].start()
            res = components['refill'].wait_for_refill()
            if not res:
                print("Refill failed! Pausing for human intervention. Press ENTER to continue.")
                input()
            print('Tank refilled.')
            print('Resetting components...')
            for component in components.values():
                components[component].reset()
            print('And now, again!')
        else:
            running = False
            break # really neccesary? probably not
    return 0

if __name__ == '__main__':
    exit(main())