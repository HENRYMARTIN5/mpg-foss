"""
helper functions for decoding CoG data
"""

def cog_to_wavelength(binary):
    return 1514+((int(binary, 2) * (1586-1514))/(2 ** 18))

def cog_to_strain(binary, initial_wavelength, strain_factor=0.78):
    return (((int(binary, 2) - initial_wavelength)/(initial_wavelength*strain_factor)) * (10 ** 6))