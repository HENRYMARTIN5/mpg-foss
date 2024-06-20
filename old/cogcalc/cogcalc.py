import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

from common.cog import cog_to_wavelength, cog_to_strain
import os

def clear():
    if os.name == "posix":
        os.system("clear")
    else:
        os.system("cls")

def main():
    while True:
        clear()
        print("CoG Value Calculator")
        print("1. Wavelength from CoG")
        print("2. Microstrain Variation from CoG")
        print("3. Exit")
        choice = input(" > ")
        choice = choice.strip()
        if choice == "1":
            clear()
            print("Wavelength from CoG")
            cog = input("CoG value > ")
            print("Wavelength: " + str(cog_to_wavelength(cog)))
            input("Press enter to continue.")
        elif choice == "2":
            clear()
            print("Microstrain from CoG")
            cog = input("CoG value > ")
            initial = input("Initial wavelength (int or CoG value accepted) > ")
            # check if initial is a CoG value
            try:
                int(initial, 2)
                initial = cog_to_wavelength(initial)
            except ValueError:
                initial = int(initial)
            print("Microstrain: " + str(cog_to_strain(cog, initial)))
            input("Press enter to continue.")
        elif choice == "3":
            exit(0)
        else:
            print("Invalid option.")
            input("Press enter to continue.")

if __name__ == "__main__":
    main()