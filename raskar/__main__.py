"""Functions for finding optimal codes for coded aperture.

To reduce the search space of the brute force search we need to skip redundant
codes. In order to do this we can take advantage of the invariance of the
Fourier transform to rotation and translation. This means that 1D codes which
are a translation of another code are redundant, and that 2D codes rotated are
redundant.

We need to figure out degerate codes due to:
    four-fold rotation
    flip across horizontal vertical or two-diagonal axes

We can use the 1D Lyndon Words to reduce the search space for 1D codes.
"""

import itertools
import os
import time

import click
import numpy as np
from tqdm import tqdm

from raskar.lyndon import LengthLimitedLyndonWords


def cost_function(code):
    """Return the quality of a code. Larger is better.

    We chose a code that (i) maximizes the minimum of the magnitude of the DFT
    values and (ii) minimizes the variance of the DFT values. Using a rating
    parameter, score = magnitude - variance.
    """
    dft = np.fft.rfft(code)
    return np.min(np.abs(dft)) - np.var(dft)


def find_codes_lyndon(K, L, output_dir, density=0.5):
    """Search 1D binary Lyndon words of K <= length <= L for the best codes.

    For the 32-bit space, searching only Lydon words reduces the search space
    to only 3.12% of the full search space.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Stats are L + 1 to avoid repeated subtraction inside search loop
    score_best = np.full(L + 1, -np.inf, dtype=np.float32)
    num_allowed_ones = tuple(int(n * density) for n in range(L + 1))
    num_searched_codes = np.zeros(L + 1, dtype=int)

    # Skip many codes by skipping to the longest one with the desired density.
    w = [0] * (L - num_allowed_ones[-1]) + [1] * num_allowed_ones[-1]

    title = "Lyndon 1D {:d}-bit code".format(L)
    for code in LengthLimitedLyndonWords(2, L, w):
        if len(code) >= K and np.sum(code) == num_allowed_ones[len(code)]:
            num_searched_codes[len(code)] += 1
            score = cost_function(code)
            if score > score_best[len(code)]:
                score_best[len(code)] = score
                filename = os.path.join(output_dir, f"{len(code)}.txt")
                with open(filename, mode='w', encoding='utf-8') as f:
                    print(
                        f"# Best code from searching",
                        f"{num_searched_codes[len(code)]:,d} Lyndon codes",
                        f"\n{code}\n{score}",
                        file=f,
                    )


def find_codes_bfs(L, density=0.5, batch_size=2**25, filename=None):
    """Find the best binary code of length L using a brute force search.

    Parameters
    ----------
    density: float
        The fraction of indices that are one.
    batch_size: int
        The number of bits to try at once. Limits memory consumption.
    filename: string
        The name of a file to dump the best result at the completion of every
        batch.
    """
    k = int(L * density)  # number of 1s in the code
    code_generator = itertools.combinations(range(L), k)
    num_combinations = (np.math.factorial(L) //
                        (np.math.factorial(k) * np.math.factorial(L - k)))
    # Determine the number of codes to try in one go and make a code generator
    num_codes_in_batch = max(batch_size // L, 1)
    num_batches = np.ceil(num_combinations / num_codes_in_batch).astype(int)

    code_best = None
    score_best = -np.inf
    num_searched_codes = 0

    title = "brute force 1D {:d}-bit code".format(L)
    for i in tqdm(range(0, num_batches), desc=title):
        # Get the next batch of codes
        indices = list(itertools.islice(code_generator, num_codes_in_batch))
        if len(indices) == 0:
            # Quit if there are no more codes to try
            break
        num_searched_codes += len(indices)
        # convert indices to a binary code
        codes = np.zeros([len(indices), L], dtype=np.float32)
        rows, cols = np.meshgrid(
            range(len(indices)), range(k), indexing='ij')
        codes[rows, indices] = 1
        # compute the DFT of the code
        dft = np.fft.rfft(codes, axis=1)
        # rate all of the DFTs
        score = np.min(np.abs(dft), axis=1) - np.var(dft, axis=1)
        best = np.argmax(score)
        if score[best] > score_best:
            code_best = codes[best]
            score_best = score[best]
            if filename is not None:
                with open(filename, mode='w', encoding='utf-8') as f:
                    print(
                        "# Best code from searching {:,d} codes".format(
                            num_searched_codes),
                        file=f)
                    print(code_best.astype(int), file=f, flush=True)
    return code_best


@click.command()
@click.argument('length_min', type=int, default=8)
@click.argument('length_max', type=int, default=16)
@click.option(
    '-o', 'output_dir', default='best_codes', type=click.Path(exists=False))
def main(length_min, length_max, output_dir):
    """Search for the best codes from LENGTH_MIN to LENGTH_MAX.

    Put the result for each code length in a separate text file named after
    the length of the code. Skip codes whose files already exist.
    """
    before = time.time()
    find_codes_lyndon(
        length_min,
        length_max,
        output_dir=os.path.join(output_dir, f"lyndon-{length_max}")
    )
    after = time.time()
    print(f"This search took {after - before} seconds.")

if __name__ == '__main__':
    main()
