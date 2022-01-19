import os

from statistic import Statistic


class Overwriter:

    def __init__(self, name):
        self.name = name

    def parse_labels(self, label_file) -> Statistic or dict:
        if not os.path.exists(label_file):
            return Statistic.from_key_value('overwriter_label_not_found', 1)

        with open(label_file, 'r') as f:
            result = self.parse(f)

        return result

    def parse(self, label_file) -> Statistic or dict:
        raise NotImplemented('Overwriters is not implemented')
