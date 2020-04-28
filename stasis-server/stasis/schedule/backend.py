from enum import Enum


class Backend(Enum):
    """
    these are the different permitted backends for processing. Might be extended down the line
    """
    FARGATE = "FARGATE"
    LOCAL = "LOCAL"
    NO_BACKEND_REQUIRED = "NO_BACKEND"


DEFAULT_PROCESSING_BACKEND = Backend.FARGATE
