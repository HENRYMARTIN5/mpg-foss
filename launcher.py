#!/usr/env python3
import subprocess
import os

while True:

    print("MPG-FOSS Util Launcher")
    print("1. FOSS FFT (calcualte the FFT of a recording, either microstrain or wavelength - deprecated, use FOSS Grapher instead)")
    print("2. FOSS Grapher (graph a recording or FFT with matplotlib)")
    print("3. FOSS Realtime Viewer (live data viewing, graphing WIP)")
    print("4. FOSS Recorder (fetch data from a gator)")
    print("5. CoG Value Calculator (convert between CoG and wavelength/microstrain)")
    print("6. Data Converter (get a csv from unofficial to official format)")
    print("7. Install dependencies")
    print("8. Exit")

    choice = input(" > ")

    if choice == "1":
        inp = input("Input file (csv) > ")
        out = input("Output file (csv) > ")
        subprocess.run(["python3", "fossfft/fossfft.py", inp, out])
    elif choice == "2":
        inp = input("Input file (csv) > ")
        out = input("Output file (png) > ")
        useofficial = input("Is the input file in official format? (y/n) > ")
        if useofficial == "y":
            useofficial = "fossgrapher/fossgrapher.py"
        else:
            useofficial = "fossgrapher/fossgraphermpg.py"
        usefourier = input("Use FFT? (y/n) > ")
        if usefourier == "y":
            usefourier = ""
        else:
            usefourier = "-n"
        subprocess.run(["python3", useofficial, inp, out, usefourier])
    elif choice == "3":
        subprocess.run(["python3", "fossrt/fossrt.py"])
    elif choice == "4":
        subprocess.run(["python3", "fossrt/fossfetch.py"])
    elif choice == "5":
        subprocess.run(["python3", "cogcalc/cogcalc.py"])
    elif choice == "6":
        inp = input("Input file (csv) > ")
        out = input("Output file (csv) > ")
        subprocess.run(["python3", "converter/converter.py", inp, out])
    elif choice == "7":
        # check to make sure user is running ubuntu
        print("Checking OS...")
        forcecontinue = False
        if os.name != "posix":
            print("Dependency installation is only supported on Ubuntu 20.04 LTS.")
            inp = input("Continue anyway? (y/n) > ")
            if inp == "y":
                forcecontinue = True
            else:
                continue
        _os = subprocess.run(["lsb_release", "-i"], stdout=subprocess.PIPE)
        _os = os.stdout.decode("utf-8")
        if not forcecontinue:
            if "Ubuntu" not in _os:
                print("Dependency installation is only supported on Ubuntu 20.04 LTS.")
                inp = input("Continue anyway? (y/n) > ")
                if inp == "y":
                    forcecontinue = True
                else:
                    continue
        subprocess.run(["sudo", "apt", "install", "python3-pip", "python3-tk", "python3-matplotlib", "python3-numpy"])
        subprocess.run(["python3", "-m", "pip", "install", "-r", "requirements.txt"])
    elif choice == "8":
        exit(0)