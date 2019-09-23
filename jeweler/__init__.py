"""Jeweler is a module for finding sequences optimized for coded aperture.

Coded aperature imaging is a computational imaging technique in which light
fields are filtered with some kind of modulating device before interacting with
the detector. The modulating pattern makes the inverse problem easier to solve
by reducing the number of possible solutions.

Not every light modulating code/sequence is equally effective. Each code
improves the recovery of only a finite number of spatial frequencies. It
is impossible to find a code that will help recover all spatial frequencies
equally.

This package provides a framework for testing all of the codes of a requested
length and weight/density against an objective function as efficiently as
possible. The main strategy it employs is targeting the shift invariance of the
Fourier tranform.

A combinatoric necklace is a representative of an equivalence class representing
all of the circular shifts of sequence. By only testing combinatoric necklaces,
we significantly reduce the search space.


API Structure
-------------

Jeweler has a command line interface (CLI) for convenience. This API is defined
in the `cli` module which called from the `__main__` module if Jeweler is called
directly using `python -m jeweler` or `jeweler` if Jeweler is installed to the
PATH.

The `catalog` module contains already computed best codes using the included
cost functions. This catalog may be searched using the `best` function.

The `io` module contains a class for saving and fetching codes to/from the disk.

The `objective` module contains the available objective functions which codes
are evaluated against.

The `search` module contains functions which orchestrate various search
strategies.
"""

import logging

from jeweler.catalog import *
from jeweler.objective import *
from jeweler.search import *

logging.getLogger(__name__).addHandler(logging.NullHandler())
