class Status:
    """
    defines all the internal allowed states
    """

    def __init__(self):
        # valid states for tracking of samples
        self.states = {
            'entered': 0,
            'acquired': 100,
            'converted': 200,
            'processing': 300,
            'exported': 400
        }

    def priority(self, state):
        """
        associated priority
        :param state:
        :return:
        """
        if self.valid(state):
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
