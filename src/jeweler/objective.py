"""Defines objective functions for rating codes."""

import numpy as np

__all__ = [
    'spectral_flatness',
    'minimal_variance',
    'coded_factor',
]


def minimal_variance(code, axis=-1):
    """Return an objective function that minimizes variance of the FFT.

    We chose a code that (i) maximizes the minimum of the magnitude of the DFT
    values and (ii) minimizes the variance of the magnitude of the DFT values.
    Using a rating parameter, score = magnitude - variance.

    References
    ----------
    Raskar, R., Agrawal, A., & Tumblin, J. (2006). Coded exposure photography:
    Motion deblurring using fluttered shutter. Acm Transactions on Graphics,
    25(3), 795–804. https://doi.org/10.1145/1179352.1141957

    """
    # TODO: For future 2D arrays use np.fft.rfftn
    dft_mag = np.abs(np.fft.rfft(code, axis=axis))
    return np.min(dft_mag, axis=axis) - np.var(dft_mag, axis=axis)


def spectral_flatness(code, axis=-1):
    """Return the spectral flatness of the code. Flat is 1.0. Tonal is 0.0.

    The spectral flatness is the geometric mean of the power spectrum divided
    by the arithmetic mean of the power spectrum.

    """
    dft = np.fft.rfft(code, axis=axis)
    power_spectrum = np.square(np.abs(dft))
    N = power_spectrum.shape[-1]
    return np.prod(power_spectrum, axis=axis)**(1 / N) / np.mean(
        power_spectrum, axis=axis)


def _cui_criterion(code, axis=-1, alpha=[2, 1, 0.075, 0.024]):
    """Return the binary fluttering sequence criterion from Cui et al (2021).

    References
    ----------
    Cui, Guangmang, Xiaojie Ye, Jufeng Zhao, Liyao Zhu, Ying Chen,
    and Yu Zhang. 2021. “An Effective Coded Exposure Photography Framework
    Using Optimal Fluttering Pattern Generation.” Optics and Lasers in
    Engineering 139 (November 2020): 106489.
    https://doi.org/10.1016/j.optlaseng.2020.106489.
    """
    L = code.shape[axis]
    mtf = np.abs(np.fft.rfft(code, axis=axis))
    raise NotImplementedError()
    # FIXME: Signal-to-noise objective requires information about camera
    # P = [1]
    # H = np.sqrt(np.trace(np.inv(P.T @ P)) / L)
    # snr = (I0 * t * R / L) / H * np.sqrt()
    return (
        # minimum MTF amplitude
        + alpha[0] * np.min(mtf, axis=axis)
        # sequence autocorrelation
        + alpha[1] * np.var(L * L / mtf, axis=axis)
        # signal to noise of captured image
        + alpha[2] * snr
        # image low frequency components
        + alpha[3] * np.mean(mtf / np.square(code + 1), axis=axis))


def coded_factor(code, axis=-1, λ=8.5):
    """Return the coded factor from Jeon et al (2017).

    This coded factor aims to preserve the spatial frequency in a blurred image
    and minimize the variance of the MTF of the code (which is related to the
    deconvolution noise).

    It is defined as: (L * L) / var(MTF) + λ min(log(MTF)) where L is the
    length of the code, λ is an arbitrary weighting factor, and MTF is the
    modulation transfer function of the code (the magnitude of the Fourier
    Transform).

    References
    ----------
    Jeon, Hae Gon, Joon Young Lee, Yudeog Han, Seon Joo Kim, and In So Kweon.
    2017. “Generating Fluttering Patterns with Low Autocorrelation for Coded
    Exposure Imaging.” International Journal of Computer Vision 123 (2):
    1–18. https://doi.org/10.1007/s11263-016-0976-4.
    """
    L = code.shape[axis]
    mtf = np.abs(np.fft.fft(code, axis=axis))
    v = np.var(mtf, axis=axis) + 1e-16
    return (L * L) / v + λ * np.min(np.log(mtf + 1e-16), axis=axis)
