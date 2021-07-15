import unittest

import numpy as np


def invariant_function(x):
    return np.abs(np.fft.rfft(x, axis=-1))


class TestDFTInvarianceAssumptions(unittest.TestCase):
    """Check if the DFT magnitude is invariant to various transformations."""
    def setUp(self):
        super().setUp()
        self.codes = np.array([
            [1, 0, 0, 0, 0, 0],
            [1, 0, 1, 0, 1, 0],
            [0, 0, 1, 1, 0, 1],
            [1, 1, 0, 1, 0, 0],
            [1, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0],
        ])
        self.ref = invariant_function(self.codes)

    def test_rotation_invariant(self):
        for i in range(self.codes.shape[-1]):
            mod = invariant_function(np.roll(self.codes, shift=i, axis=-1))
            np.testing.assert_allclose(self.ref, mod)

    def test_reverse_invariant(self):
        mod = invariant_function(np.flip(self.codes, axis=-1))
        np.testing.assert_allclose(self.ref, mod)


if __name__ == '__main__':
    unittest.main()
