#!/usr/env python3
import subprocess
import os
import sys

def clear():
    if os.name == "posix":
        os.system("clear")
    else:
        os.system("cls")

while True:
    clear()
    print("MPG-FOSS Util Launcher")
    print("1. AutoFOSS")
    print("2. Install dependencies")
    print("3. Update Repo")
    print("4. Exit")
    choice = input(" > ")
    if choice == "1":
        yn = input("Add launch options? [y/N] ")
        if yn.lower() == "y":
            options = input("Options > ")
            subprocess.run([sys.executable, "autofoss/autofoss.py", options])
        else:
            subprocess.run([sys.executable, "autofoss/autofoss.py"])
    elif choice == "2":
        # check to make sure user is running ubuntu
        print("Checking OS...")
        forcecontinue = False
        if os.name != "posix":
            print("Installing pip dependencies...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
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
        subprocess.run(["sudo", "apt", "install", "-y", "python3-pip", "python3-tk", "python3-matplotlib", "python3-numpy", "python3-scipy", "libatlas3-base"])
        if "Raspbian" in _os:
            subprocess.run(["python3", "-m", "pip", "install", "-r", "--no-warn-script-location", "requirements-pi.txt"])
        else:
            subprocess.run(["python3", "-m", "pip", "install", "-r", "--no-warn-script-location", "requirements.txt"])
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
    elif choice == "3":
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
    elif choice == "4":
        exit(0)