FAILED = 'failed'

FINISHED = 'finished'

AGGREGATED = 'aggregated'

AGGREGATING = 'aggregating'

AGGREGATING_SCHEDULING = 'aggregating_scheduling'

EXPORTED = 'exported'

REPLACED = 'replaced'

QUANTIFIED = 'quantified'

ANNOTATED = 'annotated'

CORRECTED = 'corrected'

DECONVOLUTED = 'deconvoluted'

PROCESSING = 'processing'

SCHEDULED = 'scheduled'

SCHEDULING = 'scheduling'

CONVERTED = 'converted'

ACQUIRED = 'acquired'

ENTERED = 'entered'


class States:
    """
    defines all the internal allowed states
    """

    def __init__(self):
        # valid states for tracking of samples and jobs
        self.states = {
            ENTERED: 1,
            ACQUIRED: 100,
            CONVERTED: 200,
            SCHEDULING: 299,
            SCHEDULED: 300,
            PROCESSING: 400,
            DECONVOLUTED: 410,
            CORRECTED: 420,
            ANNOTATED: 430,
            QUANTIFIED: 440,
            REPLACED: 450,
            EXPORTED: 500,
            AGGREGATING_SCHEDULING: 549,
            AGGREGATING: 550,
            AGGREGATED: 590,
            FINISHED: 600,
            FAILED: 900
        }

    def priority(self, state):
        """
        associated priority
        :param state:
        :return:
        """
        if self.valid(str(state)):
            return self.states[state.lower()]
        else:
            return None

    def valid(self, state):
        """
            is the state valid
            :param state:
            :return:
        """

        if state.lower() in self.states:
            return True
        else:
            return False
