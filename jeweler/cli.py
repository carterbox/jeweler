"""Defines a CLI for jeweler."""

import logging
import os
import time

import click

from jeweler.search import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.argument('length_min', type=int, default=8)
@click.argument('length_max', type=int, default=16)
@click.option('-o',
              '--output_dir',
              default='best_codes',
              type=click.Path(exists=False),
              help='Put the search results here.')
def cli(length_min, length_max, output_dir):
    """Find the best binary sequences [LENGTH_MIN...LENGTH_MAX).

    Save the best sequence for each length in a unique text file named
    LENGTH.txt. Restart previous searches from the best code on file.
    """
    before = time.time()
    find_codes_lyndon(length_min,
                      length_max,
                      output_dir=os.path.join(output_dir,
                                              f"lyndon-{length_max}"))
    after = time.time()
    logger.info(f"This search took {after - before} seconds.")
