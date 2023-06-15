#!/usr/env python3
import subprocess
import os

def clear():
    if os.name == "posix":
        subprocess.run(["clear"])
    else:
        subprocess.run(["cls"])

while True:

    clear()
    print("MPG-FOSS Util Launcher")
    print("1. FOSS FFT (calcualte the FFT of a recording, either microstrain or wavelength - deprecated, use FOSS Grapher instead)")
    print("2. FOSS Grapher (graph a recording or FFT with matplotlib)")
    print("3. FOSS Realtime Viewer (live data viewing, graphing WIP)")
    print("4. FOSS Recorder (fetch data from a gator)")
    print("5. CoG Value Calculator (convert between CoG and wavelength/microstrain)")
    print("6. Data Converter (get a csv from unofficial to official format)")
    print("7. Install dependencies")
    print("8. Update Repo")
    print("9. Exit")

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
        subprocess.run(["sudo", "python3", "fossrt/fossfetch.py"])
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
            print("Dependency installation is only supported on Ubuntu 20.04 LTS or Raspberry Pi OS.")
            inp = input("Continue anyway? (y/n) > ")
            if inp == "y":
                forcecontinue = True
            else:
                continue
        _os = subprocess.run(["lsb_release", "-d"], capture_output=True).stdout.decode("utf-8")
        if not forcecontinue:
            if "Ubuntu" not in _os or "Raspbian" not in _os:
                print("Dependency installation is only supported on Ubuntu 20.04 LTS or Raspberry Pi OS.")
                inp = input("Continue anyway? (y/n) > ")
                if inp == "y":
                    forcecontinue = True
                else:
                    continue
        subprocess.run(["sudo", "apt", "install", "-y", "python3-pip", "python3-tk", "python3-matplotlib", "python3-numpy", "gfortran"])
        subprocess.run(["python3", "-m", "pip", "install", "-r", "requirements.txt"])
        alternatePkgNames = {
            "GitPython": "git",
            "pyusb": "usb.core"
        }
        failed = False
        with open("requirements.txt", "r") as f:
            for line in f:
                if line.startswith("#"):
                    continue
                line = line.strip()
                if line in alternatePkgNames:
                    line = alternatePkgNames[line]
                try:
                    __import__(line)
                except ImportError:
                    print("Failed to install module " + line + ". Try installing manually?")
                    failed = True
        if failed:
            print("Some packages failed to install. Try installing them manually with python3 -m pip install <package name>.")
    elif choice == "8":
        # we double-check here that nothing has been modified locally. if there are unpushed commits, we prompt to push them. if there are uncommitted changes, we prompt to stash, commit, or discard them.
        # if there are no unpushed commits or uncommitted changes, we just pull.
        # we also want to make sure that conflicts are taken into account - if there are any, we have to let the user resolve them.

        # check for unpushed commits
        print("Checking for unpushed commits...")
        unpushed = subprocess.run(["git", "log", "@{u}..", "--oneline"], capture_output=True).stdout.decode("utf-8")
        if unpushed != "":
            print("You have unpushed commits. Please push them before updating.")
            inp = input("Push commits? (y/n) > ")
            if inp == "y":
                subprocess.run(["git", "push"])
            else:
                continue
        # check for uncommitted changes
        print("Checking for uncommitted changes...")
        uncommitted = subprocess.run(["git", "status", "--porcelain"], capture_output=True).stdout.decode("utf-8")
        if uncommitted != "":
            print("You have uncommitted changes. Please stash, commit, or discard them before updating.")
            inp = input("Stash changes? (y/n) > ")
            if inp == "y":
                message = input("Stash message > ")
                subprocess.run(["git", "stash", "push", "-m", message])
            else:
                inp = input("Commit changes? (y/n) > ")
                if inp == "y":
                    message = input("Commit message > ")
                    subprocess.run(["git", "commit", "-m", message])
                    inp = input("Push changes? (y/n) > ")
                    if inp == "y":
                        subprocess.run(["git", "push"])
                else:
                    inp = input("Discard changes? (y/n) > ")
                    if inp == "y":
                        subprocess.run(["git", "reset", "--hard"])
                    else:
                        continue
        # pull
        print("Pulling...")
        subprocess.run(["git", "pull"])
    elif choice == "9":
        exit(0)