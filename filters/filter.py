from statistic import Statistic


class Filter:

    def __init__(self):
        pass

    def apply(self, label_json) -> Statistic or None:
        raise NotImplementedError('Filter must implement Filter.apply() method')
