class Status:
    """
    defines all the internal allowed states
    """

    def __init__(self):
        # valid states for tracking of samples
        self.states = {
            'entered': 1,
            'acquired': 100,
            'converted': 200,
            'scheduled': 300,
            'processing': 400,
            'deconvoluted': 410,
            'corrected': 420,
            'annotated': 430,
            'quantified': 440,
            'replaced': 450,
            'exported': 500,
            'failed': 900
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
