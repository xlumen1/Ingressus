import pandas as pd
import scipy as sc
import numpy as np

def wavelength_to_rgb(wavelength):
    """
    Convert a wavelength in the range 380 nm through 780 nm to an RGB color.
    Returns a tuple of (R, G, B) with values from 0 to 255.
    """
    gamma = 0.8
    intensity_max = 255

    if 380 <= wavelength <= 440:
        R = -(wavelength - 440) / (440 - 380)
        G = 0.0
        B = 1.0
    elif 440 < wavelength <= 490:
        R = 0.0
        G = (wavelength - 440) / (490 - 440)
        B = 1.0
    elif 490 < wavelength <= 510:
        R = 0.0
        G = 1.0
        B = -(wavelength - 510) / (510 - 490)
    elif 510 < wavelength <= 580:
        R = (wavelength - 510) / (580 - 510)
        G = 1.0
        B = 0.0
    elif 580 < wavelength <= 645:
        R = 1.0
        G = -(wavelength - 645) / (645 - 580)
        B = 0.0
    elif 645 < wavelength <= 780:
        R = 1.0
        G = 0.0
        B = 0.0
    else:
        R = G = B = 0.0

    # Intensity correction
    if 380 <= wavelength <= 419:
        factor = 0.3 + 0.7 * (wavelength - 380) / (420 - 380)
    elif 420 <= wavelength <= 700:
        factor = 1.0
    elif 701 <= wavelength <= 780:
        factor = 0.3 + 0.7 * (780 - wavelength) / (780 - 700)
    else:
        factor = 0.0

    def adjust(color, factor):
        if color == 0.0:
            return 0
        else:
            return int(round(intensity_max * ((color * factor) ** gamma)))

    R = adjust(R, factor)
    G = adjust(G, factor)
    B = adjust(B, factor)

    return (R, G, B)

class ContinuousRange:
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.points = {}  # position: magnitude

    def add_data(self, position: float, magnitude: float):
        self.points[position] = magnitude

    def get(self, position: float):
        if not self.points:
            return None  # or raise an error

        if position in self.points:
            return self.points[position]

        # Sort the keys to find surrounding points
        keys = sorted(self.points.keys())

        before = None
        after = None

        for k in keys:
            if k < position:
                before = k
            elif k > position:
                after = k
                break

        if before is not None and after is not None:
            # Linear interpolation
            m1 = self.points[before]
            m2 = self.points[after]
            t = (position - before) / (after - before)
            return m1 + t * (m2 - m1)
        elif before is not None:
            return self.points[before]
        elif after is not None:
            return self.points[after]
        else:
            return None


def luminosity(radius: float, temperature: float) -> float:
    return 4.0 * sc.pi * np.pow(radius, 2.0) * sc.constants.Stefan_Boltzmann * np.pow(temperature, 4.0)

def spectrum(wavelength: float, temperature: float) -> float:
    return (2.0 * sc.constants.Planck * np.pow(sc.constants.speed_of_light, 2.0))/(np.pow(wavelength, 5.0))*(1.0/(np.exp((sc.constants.Planck * sc.constants.speed_of_light) / (wavelength * sc.constants.Boltzmann * temperature))-1.0))

def spectrum_range(temperature: float, resolution: int = 100) -> ContinuousRange:
    MIN_NM = 380
    MAX_NM = 700
    spectral_range = ContinuousRange(MIN_NM, MAX_NM)

    for i in range(resolution):
        wl_nm = MIN_NM + (MAX_NM - MIN_NM) * (i / (resolution - 1))  # in nm
        wl_m = wl_nm * 1e-9  # convert to meters for physics
        intensity = spectrum(wl_m, temperature)
        spectral_range.add_data(wl_nm, intensity)

    return spectral_range

def normalize_range(c_range: ContinuousRange):
    max_val = max(c_range.points.values())
    if max_val == 0:
        return
    for k in c_range.points:
        c_range.points[k] /= max_val

def perceived_color(spec):
    r = g = b = 0.0
    for wl, intensity in spec.points.items():
        rgb = wavelength_to_rgb(wl)
        r += rgb[0] * intensity
        g += rgb[1] * intensity
        b += rgb[2] * intensity
    max_val = max(r, g, b)
    if max_val > 0:
        r /= max_val
        g /= max_val
        b /= max_val
    return (r, g, b)

# Get The Peak Wavelength in meters
def peak_wavelength(temp):
    return 2.897e-3 / temp
