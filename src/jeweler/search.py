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
from sage.all import LyndonWords
from tqdm import tqdm

from jeweler.bracelet import bracelet_fc
from jeweler.io import ArchiverPandas

__all__ = [
    'exhaustive',
    'lyndon',
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


def _lyndon_chunk(necklaces, chunksize):
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


def lyndon(
    K,
    L,
    output_dir,
    objective_function,
    density=0.5,
    batch_size=64,
):
    """Search lyndon words of length L and fixed content for the best binary code.

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
    logger.info(f"Fixed-content Lyndon words of length {K}..{L}.")
    logger.info(f"the objective is '{objective_function.__name__}'.")
    logger.info(f"code density is {density:g}.")

    for L in range(K, L + 1):
        with ArchiverPandas(output_dir=output_dir, L=L) as f:

            logger.info(f"Generating Lyndon words of length {L}.")
            k = int(L * density)  # number of 1s in the code

            codes = LyndonWords([L - k, k])
            ncodes = codes.cardinality()
            chunks = _lyndon_chunk(codes, (batch_size, L))
            logger.info(f"{ncodes:,d} Lyndon words discovered.")

            title = f"fixed-content Lyndon words 1D {L:d}-bit code"
            code_best = None
            score_best = -np.inf
            progress = 0
            for _ in tqdm(
                    range(ncodes // batch_size + 1),
                    desc=title,
                    smoothing=0.05,
            ):
                batch = next(chunks)
                scores = objective_function(batch)
                best = np.argmax(scores)
                progress += batch_size
                if scores[best] > score_best:
                    score_best = scores[best]
                    code_best = batch[best].astype('int', copy=False)
                    f.update(
                        objective_function.__name__,
                        code_best,
                        score_best,
                        weight=k,
                        progress=progress,
                    )


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
    for length in range(K, L + 1):
        with ArchiverPandas(output_dir=output_dir) as f:
            weight = int(length * density)  # number of 1s in the code
            code_best = None
            score_best = -np.inf
            batch_size = max(1, batch_bits // length)
            progress = 0
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
                    code_best = batch[best].astype('int', copy=False)
                    progress += batch_size
                    f.update(
                        objective_function.__name__,
                        code_best,
                        score_best,
                        weight=weight,
                        progress=progress,
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
    for length in range(K, L + 1):
        with ArchiverPandas(output_dir=output_dir, L=L) as f:
            logger.info(f"Generating random codes of length {L}.")
            code_best = None
            score_best = -np.inf
            num_searched_codes = 0
            batch_size = max(1, batch_bits // length)
            logger.info(f"Batch size is {batch_size}.")
            weight = int(length * density)  # number of 1s in the code
            progress = 0
            for batch in tqdm(
                    _random_batch(batch_size, length, weight),
                    desc="random 1D {:d}-bit code".format(length),
                    smoothing=0.05,
            ):
                scores = objective_function(batch)
                best = np.argmax(scores)
                progress += batch_size
                if scores[best] > score_best:
                    score_best = scores[best]
                    code_best = batch[best].astype('int', copy=False).tolist()
                    f.update(
                        objective_function.__name__,
                        code_best,
                        score_best,
                        weight=weight,
                        progress=progress,
                    )
