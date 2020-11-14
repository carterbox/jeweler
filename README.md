# jeweler
A Python module for finding binary sequences optimized for coded aperture.

## Goal
[Coded aperture](https://en.wikipedia.org/wiki/Coded_aperture) is a data-collection strategy whose goal is to make solving an imaging inverse problem easier by intentionally modulating or controlling the light source with a specially designed sequence. Examples of these imaging inverse problems include deblurring, lensless imaging, and depth-of-field recovery. The success of the coded aperture approach depends on the properties of code, however, and finding a code with "optimal properties" remains difficult.

The aim of this library is to assist in quickly checking many equivalence classes of sequences against a metric. The equivalence classes targeted by this library are [combinatoric necklaces](https://en.wikipedia.org/wiki/Necklace_(combinatorics)), bracelets, and [Lyndon words](https://en.wikipedia.org/wiki/Lyndon_word) because FFT-based metrics of "good properties" should be invariant against a rotation or reversal of the sequence.


## References
Karim, S., J. Sawada, Z. Alamgir, and S. M. Husnine. 2013. “Generating Bracelets with Fixed Content.” Theoretical Computer Science 475: 103–12. https://doi.org/10.1016/j.tcs.2012.11.024.
