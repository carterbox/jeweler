"""Provides an interface for writing best codes to the disk.

Data is stored as a JSON in the following format:

```json
{
    2: {  # the code weight
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


class NotInCatalogError(ValueError):
    """Raised when a code does not exist in the catalog."""
    def __init__(self, L, weight, objective_function):
        message = (f"{weight}/{L} codes have not been evaluated "
                   f"with '{objective_function}'.")
        super(NotInCatalogError, self).__init__(message)


class Archiver(object):
    """Manages code records for competing disk writes.

    Attributes
    ----------
    filename : File
        Location of a JSON file to store records
    save_interval : float [s]
        How often to write to the disk

    """
    def __init__(self, output_dir):
        """Set up an Archiver instance."""
        self.output_dir = os.path.abspath(output_dir)
        # Create the file if it doesn't already exist
        os.makedirs(self.output_dir, exist_ok=True)
        self.f = None
        self.data = None
        self.L = None

    def __enter__(self, ):
        return self

    def __exit__(self, *args):
        self._close_file()

    def _get_data(self, L):
        if L == self.L:
            return self.data

        self._close_file()

        filename = os.path.join(self.output_dir, f"{L}.json")
        if not os.path.isfile(filename):
            with open(filename, 'w') as f:
                json.dump({}, f, indent=4)

        f = open(filename, 'a+')
        fcntl.flock(f, fcntl.LOCK_EX)
        f.seek(0)  # <--- should reset file position to the beginning.
        try:
            data = json.load(f)
        except json.decoder.JSONDecodeError:
            logger.warning(f"{filename} already exists "
                           f"and is improperly formatted.")
            raise

        self.f = f
        self.data = data
        self.L = L
        return data

    def _close_file(self):
        f = self.f
        if f is None:
            return
        else:
            data = self.data
            f.seek(0)  # <--- should reset file position to the beginning.
            f.truncate()  # remove remaining part
            json.dump(data, f, indent=4)
            fcntl.flock(f, fcntl.LOCK_UN)
            f.close()
            self.f = None

    def update(
        self,
        objective_function,
        best_code,
        objective_cost,
        weight,
    ):
        """Update the best codes on the disk."""
        W = str(weight)  # must be a string otherwise dupicate entries
        L = len(best_code)
        data = self._get_data(L)
        if W not in data:
            data[W] = {}
        if (objective_function not in data[W]
                or data[W][objective_function]['cost'] < objective_cost):
            data[W][objective_function] = {
                'cost': objective_cost,
                'code': best_code,
            }

    def fetch(
        self,
        L,
        objective_function,
        weight,
    ):
        """Get a code and its cost from the disk."""
        W = str(weight)  # must be a string otherwise dupicate entries
        filename = os.path.join(self.output_dir, f"{L}.json")
        if not os.path.isfile(filename):
            raise NotInCatalogError(L, W, objective_function)
        with open(filename, 'r') as f:
            try:
                data = json.load(f)
            except json.decoder.JSONDecodeError:
                logger.warning(f"{filename} exists, "
                               f"but it is improperly formatted.")
                raise
        if (W in data and objective_function in data[W]
                and 'code' in data[W][objective_function]):
            return data[W][objective_function]
        else:
            raise NotInCatalogError(L, W, objective_function)
