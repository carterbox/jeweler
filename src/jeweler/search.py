"""Functions for finding optimal codes for coded aperture.

To reduce the search space of the brute force search we need to skip redundant
codes. In order to do this we can take advantage of the invariance of the
Fourier transform to translation. This means that codes which are a translation
of another code are redundant.

The following transformations are not redundant:
    rotation
    flips across any axis

"""

import itertools
import logging
import os

import numpy as np
from numpy.random import default_rng
from sage.all import Necklaces
from tqdm import tqdm

from jeweler.bracelet import bracelet_fc
from jeweler.lyndon import LengthLimitedLyndonWords
from jeweler.io import Archiver

__all__ = [
    'bracelet',
    'exhaustive',
    'lyndon',
    'necklace',
    'random',
]

logger = logging.getLogger(__name__)


def _find_codes_prototype(K, L, output_dir, objective_function, density):
    """Search module expects a function with this signature.

    Parameters
    ----------
    K : int
        The minimimum code length inclusive
    L : int
        The maximum code length inclusive
    output_dir : path
        Location to put the output files
    objective_function : function
        A function from jeweler.objective where better scores are larger
    density : float
        The sum of the code divided by the length of the code

    """
    pass


def lyndon(K, L, output_dir, objective_function, density=0.5):
    """Search 1D binary Lyndon words of K <= length <= L for the best codes.

    For the 32-bit space, searching only Lydon words reduces the search space
    to only 3.12% of the full search space.
    """
    logger.info(f"Searching lyndon words of lengths {K}..{L}; "
                f"the objective is '{objective_function.__name__}'.")

    # Stats are L + 1 to avoid repeated subtraction inside search loop
    score_best = np.full(L + 1, -np.inf, dtype=np.float32)
    num_allowed_ones = tuple(int(n * density) for n in range(L + 1))
    num_searched_codes = np.zeros(L + 1, dtype=int)

    # Skip many codes by skipping to the longest one with the desired density.
    w = [0] * (L - num_allowed_ones[-1]) + [1] * num_allowed_ones[-1]

    with Archiver(output_dir=output_dir) as f:
        for code in LengthLimitedLyndonWords(2, L, w):
            if len(code) >= K and np.sum(code) == num_allowed_ones[len(code)]:
                num_searched_codes[len(code)] += 1
                score = objective_function(code)
                if score > score_best[len(code)]:
                    score_best[len(code)] = score
                    f.update(objective_function.__name__,
                             code,
                             score,
                             weight=num_allowed_ones[len(code)])


def _exhaustive_batch(batch_size, length, weight):
    combinations = itertools.combinations(range(length), weight)
    try:
        while True:
            count = 0
            codes = np.zeros((batch_size, length), dtype=np.float32)
            for row in codes:
                row[list(next(combinations))] = 1
                count += 1
            yield codes
    except StopIteration:
        yield codes[:count]


def exhaustive(
    K,
    L,
    output_dir,
    objective_function,
    density=0.5,
    batch_bits=4096,
):
    """Find the best binary code of length L using a brute force search.

    Parameters
    ----------
    density: float
        The fraction of indices that are one.
    batch_bits: int
        The number of bits to try at once. Limits memory consumption.
    filename: string
        The name of a file to dump the best result at the completion of every
        batch.

    """
    with Archiver(output_dir=output_dir) as f:
        for length in range(K, L + 1):
            weight = int(length * density)  # number of 1s in the code
            code_best = None
            score_best = -np.inf
            batch_size = max(1, batch_bits // length)
            number_of_batches = 1 + (
                np.math.factorial(length) //
                (np.math.factorial(weight) *
                 np.math.factorial(length - weight))) // batch_size
            for batch in tqdm(
                    _exhaustive_batch(batch_size, length, weight),
                    desc="exhaustive 1D {:d}-bit code".format(length),
                    smoothing=0.05,
                    total=number_of_batches,
            ):
                scores = objective_function(batch)
                best = np.argmax(scores)
                if scores[best] > score_best:
                    score_best = scores[best]
                    code_best = batch[best].astype('int', copy=False).tolist()
                    f.update(
                        objective_function.__name__,
                        code_best,
                        score_best,
                        weight=weight,
                    )


def _random_batch(batch_size, L, k):
    """Return a random batch of with length L and weight k."""
    rng = default_rng()
    while True:
        codes = np.zeros((batch_size, L), dtype=np.float32)
        for row in codes:
            row[rng.choice(L, k, replace=False)] = 1
        yield codes


def random(
    K,
    L,
    output_dir,
    objective_function,
    density=0.5,
    batch_bits=4096,
):
    """Find the best binary code of length L using a random search.

    Parameters
    ----------
    K : int
        The minimimum code length inclusive
    L : int
        The maximum code length inclusive
    output_dir : path
        Location to put the output files
    objective_function : function
        A function from jeweler.objective where better scores are larger
    density : float
        The sum of the code divided by the length of the code

    """
    with Archiver(output_dir=output_dir) as f:
        for length in range(K, L + 1):
            logger.info(f"Generating random codes of length {L}.")
            code_best = None
            score_best = -np.inf
            num_searched_codes = 0
            batch_size = max(1, batch_bits // length)
            logger.info(f"Batch size is {batch_size}.")
            weight = int(length * density)  # number of 1s in the code
            for batch in tqdm(
                    _random_batch(batch_size, length, weight),
                    desc="random 1D {:d}-bit code".format(length),
                    smoothing=0.05,
            ):
                scores = objective_function(batch)
                best = np.argmax(scores)
                if scores[best] > score_best:
                    score_best = scores[best]
                    code_best = batch[best].astype('int', copy=False).tolist()
                    f.update(
                        objective_function.__name__,
                        code_best,
                        score_best,
                        weight=weight,
                    )


def bracelet(
    K,
    L,
    output_dir,
    objective_function,
    density=0.5,
    batch_size=2048,
):
    """Search bracelets of length L and fixed content for the best binary code.

    Parameters
    ----------
    L : int
        The maximum code length
    output_dir : path
        Location to put the output files
    objective_function : function
        A function from jeweler.objective where better scores are larger
    density : float
        The sum of the code divided by the length of the code
    """
    logger.info(f"Fixed-content bracelets of length {K}..{L}.")
    logger.info(f"the objective is '{objective_function.__name__}'.")
    logger.info(f"code density is {density:g}.")

    with Archiver(output_dir=output_dir) as f:

        for L in range(K, L + 1):

            logger.info(f"Generating bracelets of length {L}.")
            k = int(L * density)  # number of 1s in the code
            codes = bracelet_fc(L, 2, [L - k, k])
            logger.info(f"{len(codes):,d} bracelets discovered.")

            title = f"fixed-content bracelets 1D {L:d}-bit code"
            code_best = None
            score_best = -np.inf
            for _ in tqdm(
                    range(len(codes) // batch_size + 1),
                    desc=title,
                    smoothing=0.05,
            ):
                batch = codes[-batch_size:]
                del codes[-batch_size:]
                scores = objective_function(batch)
                best = np.argmax(scores)
                if scores[best] > score_best:
                    score_best = scores[best]
                    code_best = batch[best]
                    f.update(
                        objective_function.__name__,
                        code_best,
                        score_best,
                        weight=k,
                    )


def _necklace_chunk(necklaces, chunksize):
    """Wrap a sage.Necklaces instance in a Python generator.

    Parameters
    ----------
    necklages : sage.Necklaces
        A SageMath necklage class instance.
    chunksize : 2-tuple
        The shape of the desired chunk of necklaces.
    """
    assert chunksize[1] == len(necklaces.first())
    chunk = np.empty(chunksize, dtype='float32')
    i = 0
    for x in necklaces:
        chunk[i] = x
        i += 1
        if i >= chunksize[0]:
            yield chunk - 1
            chunk = np.empty(chunksize, dtype='float32')
            i = 0
    if i < chunksize[0]:
        yield chunk[:i] - 1


def necklace(
    K,
    L,
    output_dir,
    objective_function,
    density=0.5,
    batch_size=2048,
):
    """Search necklaces of length L and fixed content for the best binary code.

    Parameters
    ----------
    L : int
        The maximum code length
    output_dir : path
        Location to put the output files
    objective_function : function
        A function from jeweler.objective where better scores are larger
    density : float
        The sum of the code divided by the length of the code
    """
    logger.info(f"Fixed-content necklaces of length {K}..{L}.")
    logger.info(f"the objective is '{objective_function.__name__}'.")
    logger.info(f"code density is {density:g}.")

    with Archiver(output_dir=output_dir) as f:

        for L in range(K, L + 1):

            logger.info(f"Generating necklaces of length {L}.")
            k = int(L * density)  # number of 1s in the code

            codes = Necklaces([L - k, k])
            ncodes = codes.cardinality()
            chunks = _necklace_chunk(codes, (batch_size, L))
            logger.info(f"{ncodes:,d} necklaces discovered.")

            title = f"fixed-content necklaces 1D {L:d}-bit code"
            code_best = None
            score_best = -np.inf
            for _ in tqdm(
                    range(ncodes // batch_size + 1),
                    desc=title,
                    smoothing=0.05,
            ):
                batch = next(chunks)
                scores = objective_function(batch)
                best = np.argmax(scores)
                if scores[best] > score_best:
                    score_best = scores[best]
                    code_best = batch[best].astype('int', copy=False).tolist()
                    f.update(
                        objective_function.__name__,
                        code_best,
                        score_best,
                        weight=k,
                    )
