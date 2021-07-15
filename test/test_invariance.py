import unittest
from jeweler.objective import minimal_variance, spectral_flatness

import numpy as np


def magnitude(x):
    """Return the magnitude of the DFT of x."""
    return np.abs(np.fft.rfft(x, axis=-1))


class TestDFTInvarianceAssumptions(unittest.TestCase):
    """Check if the DFT magnitude is invariant to various transformations."""
    def setUp(self):
        super().setUp()
        self.invariant_function = magnitude
        self.codes = np.array([
            [1, 0, 0, 0, 0, 0],
            [1, 0, 1, 0, 1, 0],
            [0, 0, 1, 1, 0, 1],
            [1, 1, 0, 1, 0, 0],
            [1, 1, 1, 1, 1, 1],
            [0, 0, 1, 0, 0, 1],
        ])

    # @unittest.skip("For debugging purposes only.")
    # def test_name_function(self):
    #     print(self.invariant_function.__name__)

    def test_rotation_invariant(self):
        ref = self.invariant_function(self.codes)
        for i in range(self.codes.shape[-1]):
            mod = self.invariant_function(np.roll(self.codes, shift=i,
                                                  axis=-1))
            np.testing.assert_allclose(ref, mod, rtol=1)

    def test_reverse_invariant(self):
        ref = self.invariant_function(self.codes)
        mod = self.invariant_function(np.flip(self.codes, axis=-1))
        np.testing.assert_allclose(ref, mod, rtol=1)


class TestSpectralFlatnessInvarianceAssumptions(TestDFTInvarianceAssumptions):
    def setUp(self):
        super().setUp()
        self.invariant_function = spectral_flatness


class TestMinimalVarianceInvarianceAssumptions(TestDFTInvarianceAssumptions):
    def setUp(self):
        super().setUp()
        self.invariant_function = minimal_variance


if __name__ == '__main__':
    unittest.main()
