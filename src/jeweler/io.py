"""Provides an interface for writing best codes to the disk."""

import fcntl
import json
import logging
import os
import time

import pandas
import numpy as np

all = ['Archiver', 'ArchiverPandas']

logger = logging.getLogger(__name__)


class NotInCatalogError(ValueError):
    """Raised when a code does not exist in the catalog."""
    def __init__(self, L, weight, objective_function):
        message = (f"{weight}/{L} codes have not been evaluated "
                   f"with '{objective_function}'.")
        super(NotInCatalogError, self).__init__(message)


class Archiver(object):
    """Manages code records for competing disk writes.

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


class ArchiverPandas(object):
    """Manages code records for competing disk writes.

    Stores information about possible best codes in a Pandas table in a file
    named by the length of the code. i.e. all data on codes length 24 are
    stored together in "24.json".

    Attributes
    ----------
    output_dir : str
        The path of the folder into which the file will be saved.
    L : int > 0
        The length of the code in the archive.
    table : pandas.DataFrame
        A table of all the best code candidates.
    filename : str
        The name of the file where the codes will be stored.
    """
    def __init__(self, output_dir: str, L: int):
        """Set up an Archiver instance."""
        self.output_dir = os.path.abspath(output_dir)
        # Create the file if it doesn't already exist
        os.makedirs(self.output_dir, exist_ok=True)
        self.table = pandas.DataFrame(dtype='object')
        if L > 0:
            self.L = L
        else:
            raise ValueError("L must be a positive integer!")
        self.filename = os.path.join(self.output_dir, f"{self.L}.json")
        self.last_write = None
        self._needs_dump = False

    def __enter__(self):
        self.last_write = time.time()
        self.best_cost = -np.inf
        self._needs_dump = False
        return self

    def __exit__(self, *args):
        self.__dump__()

    def __dump__(self):
        self.last_write = time.time()
        self._needs_dump = False
        if os.path.isfile(self.filename):
            already_exists = True
            mode = 'r+'
        else:
            already_exists = False
            mode = 'w'
        with open(self.filename, mode) as f:
            if already_exists:
                existing_table = pandas.io.json.read_json(f)
                f.seek(0)  # <--- should reset file position to the beginning.
                f.truncate()  # remove remaining part
                self.table = existing_table.append(
                    self.table,
                    ignore_index=True,
                    verify_integrity=True,
                )
            self.table = self.table.round({"cost": 6})
            self.table.drop_duplicates(
                subset=[
                    "objective",
                    "weight",
                    "progress",
                ],
                keep='last',
                inplace=True,
            )
            pandas.io.json.to_json(
                f,
                self.table,
                indent=2,
            )

    def update(
        self,
        search_method: str,
        objective_function: str,
        best_code,
        objective_cost,
        weight,
        progress=0,
    ):
        """Update the best codes on the disk."""
        if objective_cost > self.best_cost:
            self._needs_dump = True
            new_entry = pandas.DataFrame({
                "search": search_method,
                "objective": objective_function,
                "code": [best_code],
                "cost": objective_cost,
                "weight": weight,
                "progress": progress,
            })
            self.table = self.table.append(
                new_entry,
                ignore_index=True,
                verify_integrity=True,
            )
        if self._needs_dump and ((time.time() - self.last_write) > 1860):
            # Dump to file every 31 minutes
            self.__dump__()

    def fetch(
        self,
        search_method: str,
        objective_function: str,
        weight: int,
    ):
        """Get a code and its cost from the disk."""
        if os.path.isfile(self.filename):
            with open(self.filename, 'r+') as f:
                table = pandas.io.json.read_json(f)
            try:
                table = table[(table["objective"] == objective_function)
                              & (table["weight"] == weight)
                              & (table["search"] == search_method)]
                best = table.loc[table['cost'].idxmax()]
                self.best_cost = best["cost"]
                return best["code"], best["cost"], best["progress"]
            except (ValueError, KeyError):
                pass
        return None, -np.inf, 0
