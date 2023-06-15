#!/usr/env python3
import subprocess
import os

while True:

    print("MPG-FOSS Util Launcher")
    print("1. FOSS FFT")
    print("2. FOSS Grapher")
    print("3. FOSS Realtime Viewer")
    print("4. FOSS Recorder")
    print("5. CoG Value Calculator")
    print("6. Install dependencies")
    print("7. Exit")

    choice = input(" > ")

    if choice == "1":
        inp = input("Input file > ")
        out = input("Output file > ")
        subprocess.run(["python3", "fossfft/fossfft.py", inp, out])
    elif choice == "2":
        inp = input("Input file > ")
        out = input("Output file > ")
        usefourier = input("Use FFT? (y/n) > ")
        if usefourier == "y":
            usefourier = ""
        else:
            usefourier = "-n"
        subprocess.run(["python3", "fossgrapher/fossgrapher.py", inp, out, usefourier])
    elif choice == "3":
        subprocess.run(["python3", "fossrt/fossrt.py"])
    elif choice == "4":
        subprocess.run(["python3", "fossrt/fossfetch.py"])
    elif choice == "5":
        subprocess.run(["python3", "cogcalc/cogcalc.py"])
    elif choice == "6":
        # check to make sure user is running ubuntu
        print("Checking OS...")
        if os.name != "posix":
            print("Dependency installation is only supported on Ubuntu 20.04 LTS.")
            exit(1)
        _os = subprocess.run(["lsb_release", "-i"], stdout=subprocess.PIPE)
        _os = os.stdout.decode("utf-8")
        if "Ubuntu" not in _os:
            print("Dependency installation is only supported on Ubuntu 20.04 LTS.")
            continue
        subprocess.run(["sudo", "apt", "install", "python3-pip", "python3-tk", "python3-matplotlib", "python3-numpy"])
        subprocess.run(["python3", "-m", "pip", "install", "-r", "requirements.txt"])
    elif choice == "7":
        exit(0)