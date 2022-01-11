"""Defines a CLI for jeweler."""

import logging
import os

import click

import jeweler.catalog
import jeweler.objective
import jeweler.search

logger = logging.getLogger(__name__)


@click.command()
@click.argument('length_min', type=int, default=8)
@click.argument('length_max', type=int, default=16)
@click.option('-o',
              '--output-dir',
              default=os.path.dirname(jeweler.catalog.__file__),
              type=click.Path(exists=False),
              help='Put the search results here.')
@click.option('-s',
              '--search-method',
              default=jeweler.search.__all__[0],
              type=click.Choice(jeweler.search.__all__),
              help='Use this method to search codes.')
@click.option('-f',
              '--objective-function',
              default=jeweler.objective.__all__[0],
              type=click.Choice(jeweler.objective.__all__),
              help='Use this function to score codes.')
@click.option('-l',
              '--log',
              default=None,
              type=click.Path(),
              help='Write logs to this file instead of the terminal.')
@click.option('-d',
              '--density',
              default=0.5,
              type=click.FLOAT,
              help='Fraction of bits that are one.')
@click.option('--verbose-archive/--no-verbose-archive',
              default=True,
              help='Record best from all batches or only when a new best code is found.')
def cli(
    length_min,
    length_max,
    output_dir,
    search_method,
    objective_function,
    log,
    density,
    verbose_archive,
):
    """Find the best binary sequences LENGTH_MIN..LENGTH_MAX.

    Save the best sequence for each length in a unique file named
    LENGTH.json. Restart previous searches from the best code on file.
    """
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
        filename=log,
    )
    getattr(jeweler.search, search_method)(
        length_min,
        length_max,
        output_dir=output_dir,
        objective_function=getattr(jeweler.objective, objective_function),
        density=density,
        verbose_archive=verbose_archive,
    )
