import os
import logging

import jeweler

logger = logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    from pyinstrument import Profiler
    profiler = Profiler()
    profiler.start()
    jeweler.search.bracelet(
        K=31,
        L=31,
        output_dir=os.path.dirname(jeweler.catalog.__file__),
        objective_function=jeweler.objective.minimal_variance,
    )
    profiler.stop()
    print(profiler.output_text(unicode=True, color=True))

""" Checking the number of ones in the code to see if it matches the desired
weight is most expensive. Try switching to necklaces of defined weight to
avoid computing this sum. The second most expensive thing is the cost function.
Surprisingly, the FFT is not as expensive as the mean, product, and variance
operations combined."""
