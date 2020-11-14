"""Defines objective functions for rating codes."""

import numpy as np

__all__ = [
    'spectral_flatness',
    'minimal_variance',
]


def minimal_variance(code):
    """Return an objective function that minimizes variance of the FFT.

    We chose a code that (i) maximizes the minimum of the magnitude of the DFT
    values and (ii) minimizes the variance of the DFT values. Using a rating
    parameter, score = magnitude - variance.

    References
    ----------
    Raskar, R., Agrawal, A., & Tumblin, J. (2006). Coded exposure photography:
    Motion deblurring using fluttered shutter. Acm Transactions on Graphics,
    25(3), 795–804. https://doi.org/10.1145/1179352.1141957

    """
    # TODO: For future 2D arrays use np.fft.rfftn
    dft = np.fft.rfft(code)
    return np.min(np.abs(dft)) - np.var(dft)


def spectral_flatness(code):
    """Return the spectral flatness of the code. Flat is 1.0. Tonal is 0.0.

    The spectral flatness is the geometric mean of the power spectrum divided
    by the arithmetic mean of the power spectrum.

    """
    dft = np.fft.rfft(code)
    power_spectrum = np.square(np.abs(dft))
    N = power_spectrum.size
    return np.prod(power_spectrum)**(1 / N) / np.mean(power_spectrum)
