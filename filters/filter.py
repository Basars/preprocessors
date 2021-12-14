from statistic import Statistic


class Filter:

    def __init__(self):
        pass

    def apply(self, filename, label_filepath, label_json) -> Statistic or None:
        raise NotImplementedError('Filter must implement Filter.apply() method')
