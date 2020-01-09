from enum import Enum


class States(Enum):
    """
    some standard states
    """

    SCHEDULED = "scheduled",
    PROCESSING = "processing",
    PROCESSED = "processed",
    AGGREGATING = "aggregating",
    AGGREGATED = "aggregated",
    FAILED = "failed",
    DONE = "done"

    def __str__(self):
        return '%s' % self.value