from enum import Enum


class States(Enum):
    """
    some standard states
    """

    SCHEDULING = "scheduling",
    SCHEDULED = "scheduled",
    PROCESSING = "processing",
    PROCESSED = "processed",
    AGGREGATING = "aggregating",
    AGGREGATED = "aggregated",
    FAILED = "failed",
    AGGREGATION_SCHEDULED = "aggregation_scheduled"
    DONE = "done"

    def __str__(self):
        return '%s' % self.value
