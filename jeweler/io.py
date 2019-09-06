"""Provides an interface for writing best codes to the disk.

Data is stored as a JSON in the following format:

```json
{
    5: {  # the code length
        "minimal_variance" : {  # the objective function
            "code" : [0, 1, 0, 0, 1],
            "cost" : -145641.4124,
        },
        "spectral_flatness" : {
            "code" : [0, 1, 0, 0, 1],
            "cost" : -145641.4124,
        }
    }
}
```
"""

import fcntl
import json
import logging
import os

all = [
    'Archiver',
]

logger = logging.getLogger(__name__)


class Archiver(object):
    """Manages code records for competing disk writes.

    Attributes
    ----------
    filename : File
        Location of a JSON file to store records
    save_interval : float [s]
        How often to write to the disk

    """

    def __init__(self, filename):
        self.filename = filename
        # Create the file if it doesn't already exist
        os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
        if not os.path.isfile(filename):
            with open(self.filename, 'w') as f:
                json.dump({}, f, indent=4)

    def __update_disk__(self, ):
        """Write the current buffer to the disk."""
        with open(self.filename, 'r+') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            data = json.load(f)
            # resolve disk with self data
            f.seek(0)  # <--- should reset file position to the beginning.
            json.dump(data, f, indent=4)
            f.truncate()  # remove remaining part
            fcntl.flock(f, fcntl.LOCK_UN)

    def update(
            self,
            objective_function,
            best_code,
            objective_cost,
    ):
        """Update the best codes on the disk."""
        L = str(len(best_code))
        with open(self.filename, 'a+') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            f.seek(0)  # <--- should reset file position to the beginning.
            try:
                data = json.load(f)
            except json.decoder.JSONDecodeError:
                logger.warning(f"{self.filename} already exists "
                               f"and is improperly formatted.")
                raise
            if L not in data:
                data[L] = {}
            if (objective_function not in data[L]
                    or data[L][objective_function]['cost'] < objective_cost):
                data[L][objective_function] = {
                    'cost': objective_cost,
                    'code': best_code,
                }
            f.seek(0)  # <--- should reset file position to the beginning.
            f.truncate()  # remove remaining part
            json.dump(data, f, indent=4)
            fcntl.flock(f, fcntl.LOCK_UN)
        return
