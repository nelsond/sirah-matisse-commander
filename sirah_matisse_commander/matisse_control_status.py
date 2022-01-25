from enum import Enum


class MatisseControlStatus(Enum):
    """Control status of slow piezo, piezo etalon, or thin etalon."""
    RUN = 1
    STOP = 0
