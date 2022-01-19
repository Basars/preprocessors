import os

from .mode import Mode
from .roi import ROI
from statistic import Statistic
from preprocessors import read_dcm_and_labels


class Classify(Mode):

    def __init__(self, root_dcm_dir, root_label_dir, root_dst_dir, pipes, filters):
        super(Classify, self).__init__('Classify',
                                       root_dcm_dir, root_label_dir, root_dst_dir,
                                       pipes, filters)

        self._make_patient_dir = False

    def run(self, dst_dir, filename, dcm_filepath, label_filepath) -> Statistic or None:
        _, polygons, phase = read_dcm_and_labels(dcm_filepath, label_filepath)
        if len(polygons) == 0:
            return Statistic.from_key_value('no_polygons', 1)

        image = ROI.extract_region_of_interest(dcm_filepath, label_filepath)

        dst_dir = os.path.join(self.root_dst_dir, str(phase))
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir, exist_ok=True)

        dst_filepath = os.path.join(dst_dir, '{}.png'.format(filename))
        return self.pipelines(dst_filepath, image)
