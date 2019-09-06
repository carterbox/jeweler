"""Defines a CLI for jeweler."""

import logging
import os
import time

import click

import jeweler.search
import jeweler.objective

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.argument('length_min', type=int, default=8)
@click.argument('length_max', type=int, default=16)
@click.option('-o',
              '--output-dir',
              default='best_codes.json',
              type=click.Path(exists=False),
              help='Put the search results here.')
@click.option('-s',
              '--search-method',
              default='lyndon',
              type=click.Choice(jeweler.search.__all__),
              help='Use this method to search codes.')
@click.option('-f',
              '--objective-function',
              default='minimal_variance',
              type=click.Choice(jeweler.objective.__all__),
              help='Use this function to score codes.')
def cli(length_min, length_max, output_dir, search_method, objective_function):
    """Find the best binary sequences LENGTH_MIN...LENGTH_MAX.

    Save the best sequence for each length in a unique text file named
    LENGTH.txt. Restart previous searches from the best code on file.
    """
    before = time.time()
    getattr(jeweler.search, search_method)(
        length_min,
        length_max,
        output_dir=output_dir,
        objective_function=getattr(jeweler.objective, objective_function),
    )
    after = time.time()
    logger.info(f"This search took {after - before} seconds.")
