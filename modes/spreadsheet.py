import os

from .mode import Mode
from statistic import Statistic


class Spreadsheet(Mode):

    def __init__(self, root_dcm_dir, root_label_dir, root_dst_dir, _):
        super(Spreadsheet, self).__init__('Spreadsheet', root_dcm_dir, root_label_dir, root_dst_dir, [])

        self._make_patient_dir = False

        if not os.path.exists(root_dst_dir):
            os.makedirs(root_dst_dir, exist_ok=True)
        self.spreadsheet_file = open(os.path.join(root_dst_dir, 'spreadsheet.csv'), 'w')
        self.spreadsheet_file.write('dirname,filename\n')

        self.lines = []

    def add_line(self, dirname, filename):
        self.lines.append('{},{}\n'.format(dirname, filename))

    def finish(self):
        sorted_lines = sorted(self.lines)
        max_bytes = 1024
        bytes_len = 0
        for line in sorted_lines:
            self.spreadsheet_file.write(line)
            new_bytes = len(line.encode('utf-8'))
            if new_bytes + bytes_len >= max_bytes:
                self.spreadsheet_file.flush()
                bytes_len = 0
            else:
                bytes_len += new_bytes
        self.spreadsheet_file.close()
        pass

    def run(self, dst_dir, filename, dcm_filepath, label_filepath) -> Statistic or None:
        patient_identifier = dst_dir.split('/')[-1]
        self.add_line(patient_identifier, filename)
        return None
