from statistic import Statistic
from .filter import Filter


class PhaseFilter(Filter):

    MIN_PHASE = 0
    MAX_PHASE = 5

    def __init__(self):
        super(PhaseFilter, self).__init__()

    def apply(self, label_filepath, label_json) -> Statistic or None:
        phase = int(label_json['image']['phase_id'])
        if PhaseFilter.MIN_PHASE < phase < PhaseFilter.MAX_PHASE:
            return None

        print(f"'{label_filepath}' contains invalid phase state: {phase}")
        return Statistic.from_key_value('invalid_phase_{}'.format(phase), 1)
