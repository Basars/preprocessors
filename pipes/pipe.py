import numpy as np

from statistic import Statistic


class Pipe:

    def __init__(self, name):
        self._name = name

    def inform(self):
        print('{} pipe have been initialized'.format(self.name))

    @property
    def name(self):
        return self._name

    def apply(self, image) -> Statistic or np.ndarray:
        raise NotImplementedError("Pipe haven't not implemented.")