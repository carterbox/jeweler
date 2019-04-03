import itertools
import os

import click
import numpy as np
from tqdm import tqdm


def find_codes_bfs(L, density=0.5, batch_size=2**25, filename=None):
    """Find the best binary code of length L using a brute force search.

    We chose a code that (i) maximizes the minimum of the magnitude of the DFT
    values and (ii) minimizes the variance of the DFT values. Using a rating
    parameter, score = magnitude - variance.

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
                    print(codes[best].astype(int), file=f, flush=True)
    return codes[best]


@click.command()
@click.argument('length_min', type=int)
@click.argument('length_max', type=int)
@click.option(
    '-o', 'output_dir', default='best_codes', type=click.Path(exists=False))
def main(length_min, length_max, output_dir):
    """Search for the best codes from LENGTH_MIN to LENGTH_MAX.

    Put the result for each code length in a separate text file named after
    the length of the code. Skip codes whose files already exist.
    """
    os.makedirs(output_dir, exist_ok=True)
    for L in range(length_min, length_max, 1):
        filename = os.path.join(output_dir, "{}.txt".format(L))
        if not os.path.isfile(filename):
            code = find_codes_bfs(L, density=0.5, filename=filename)
        else:
            print(filename + " exists!")


if __name__ == '__main__':
    main()
