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
import time

import numpy as np
from numpy.random import default_rng
from sage.all import LyndonWords
from tqdm import tqdm

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
    if i > 0:
        yield chunk[:i] - 1


def lyndon(
    K,
    L,
    output_dir,
    objective_function,
    density=0.5,
    batch_bits=4096,
):
    """Search lyndon words of length L and fixed content for the best binary code.

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
    batch_bits: int
        The number of bits to try at once. Limits memory consumption.
    """
    logger.info(f"Fixed-content Lyndon words of length {K}..{L}.")
    logger.info(f"the objective is '{objective_function.__name__}'.")
    logger.info(f"code density is {density:g}.")

    for length in range(K, L + 1):
        before = time.time()
        with ArchiverPandas(output_dir=output_dir, L=length) as f:
            weight = int(length * density)  # number of 1s in the code
            batch_size = max(1, batch_bits // length)
            code_best, score_best, progress_best = f.fetch(
                'lyndon',
                objective_function.__name__,
                weight,
            )
            progress = 0

            codes = LyndonWords([length - weight, weight])
            ncodes = int(codes.cardinality())
            number_of_batches = (ncodes // batch_size +
                                 1 if batch_size < ncodes
                                 or ncodes % batch_size > 0 else 0)
            for batch in tqdm(
                    _lyndon_chunk(codes, (batch_size, length)),
                    desc=f"fixed-content Lyndon words 1D {length:d}-bit code",
                    smoothing=0.05,
                    total=number_of_batches,
            ):
                progress += len(batch)
                if progress < progress_best:
                    continue
                scores = objective_function(batch)
                best = np.argmax(scores)
                f.update(
                    'lyndon',
                    objective_function.__name__,
                    best_code=batch[best].astype('int', copy=False),
                    objective_cost=scores[best],
                    weight=weight,
                    progress=progress,
                )
        after = time.time()
        logger.info(f"This search took {after - before:.3e} seconds.")


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
        if count > 0:
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
    batch_bits: int
        The number of bits to try at once. Limits memory consumption.
    """
    logger.info(f"Fixed-content exhaustive words of length {K}..{L}.")
    logger.info(f"the objective is '{objective_function.__name__}'.")
    logger.info(f"code density is {density:g}.")

    for length in range(K, L + 1):
        before = time.time()
        with ArchiverPandas(output_dir=output_dir, L=length) as f:
            weight = int(length * density)  # number of 1s in the code
            batch_size = max(1, batch_bits // length)
            _, _, progress_best = f.fetch(
                'exhaustive',
                objective_function.__name__,
                weight,
            )
            progress = 0

            ncodes = (np.math.factorial(length) //
                      (np.math.factorial(weight) *
                       np.math.factorial(length - weight)))
            number_of_batches = (ncodes // batch_size +
                                 1 if batch_size < ncodes
                                 or ncodes % batch_size > 0 else 0)
            for batch in tqdm(
                    _exhaustive_batch(batch_size, length, weight),
                    desc="exhaustive 1D {:d}-bit code".format(length),
                    smoothing=0.05,
                    total=number_of_batches,
            ):
                progress += len(batch)
                if progress < progress_best:
                    continue
                scores = objective_function(batch)
                best = np.argmax(scores)
                f.update(
                    'exhaustive',
                    objective_function.__name__,
                    best_code=batch[best].astype('int', copy=False),
                    objective_cost=scores[best],
                    weight=weight,
                    progress=progress,
                )
        after = time.time()
        logger.info(f"This search took {after - before:.3e} seconds.")


def _random_batch(batch_size, L, k, num_batch):
    """Return a random batch of with length L and weight k."""
    rng = default_rng()
    for _ in range(num_batch):
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
    batch_bits: int
        The number of bits to try at once. Limits memory consumption.
    """
    logger.info(f"Fixed-content random words of length {K}..{L}.")
    logger.info(f"the objective is '{objective_function.__name__}'.")
    logger.info(f"code density is {density:g}.")

    for length in range(K, L + 1):
        before = time.time()
        with ArchiverPandas(output_dir=output_dir, L=length) as f:
            weight = int(length * density)  # number of 1s in the code
            batch_size = max(1, batch_bits // length)
            _, _, progress = f.fetch(
                'random',
                objective_function.__name__,
                weight,
            )

            ncodes = (np.math.factorial(length) //
                      (np.math.factorial(weight) *
                       np.math.factorial(length - weight))) // 10
            number_of_batches = (ncodes // batch_size +
                                 1 if batch_size < ncodes
                                 or ncodes % batch_size > 0 else 0)
            for batch in tqdm(
                    _random_batch(batch_size, length, weight,
                                  number_of_batches),
                    desc="random 1D {:d}-bit code".format(length),
                    smoothing=0.05,
                    total=number_of_batches,
            ):
                scores = objective_function(batch)
                best = np.argmax(scores)
                progress += len(scores)
                f.update(
                    'random',
                    objective_function.__name__,
                    best_code=batch[best].astype('int', copy=False),
                    objective_cost=scores[best],
                    weight=weight,
                    progress=progress,
                )
        after = time.time()
        logger.info(f"This search took {after - before:.3e} seconds.")
