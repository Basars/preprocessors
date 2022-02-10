import os

from .mode import Mode
from preprocessors import read_dcm_and_labels
from statistic import Statistic


class Label(Mode):

    def __init__(self, root_dcm_dir, root_label_dir, root_dst_dir, _, filters):
        super(Label, self).__init__('Label', root_dcm_dir, root_label_dir, root_dst_dir, [], filters)

        self._make_patient_dir = False

        if not os.path.exists(root_dst_dir):
            os.makedirs(root_dst_dir, exist_ok=True)
        self.label_file = open(os.path.join(root_dst_dir, 'labels.csv'), 'w')
        self.label_file.write('filename,phase\n')

        self.lines = []

    def add_line(self, filename, phase):
        self.lines.append('{},{}\n'.format(filename, phase))

    def finish(self):
        sorted_lines = sorted(self.lines)
        max_bytes = 1024
        bytes_len = 0
        for line in sorted_lines:
            self.label_file.write(line)
            new_bytes = len(line.encode('utf-8'))
            if new_bytes + bytes_len >= max_bytes:
                self.label_file.flush()
                bytes_len = 0
            else:
                bytes_len += new_bytes
        self.label_file.close()

    def run(self, dst_dir, filename, dcm_filepath, label_filepath) -> Statistic or None:
        _, polygons, phase = read_dcm_and_labels(dcm_filepath, label_filepath)
        if len(polygons) == 0:
            phase = 0
        self.add_line(filename, phase)
        return None
