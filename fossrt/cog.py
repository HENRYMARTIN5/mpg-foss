"""
helper functions for decoding CoG data
"""

def cog_to_wavelength(binary):
    return 1514+((int(binary, 2) * (1586-1514))/(2 ** 18))