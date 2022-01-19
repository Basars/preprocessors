import os

import cv2

from statistic import Statistic
from .mode import Mode
from preprocessors import create_segment_mask


class Transform(Mode):

    def __init__(self, root_dcm_dir, root_label_dir, root_dst_dir, pipes, filters):
        super(Transform, self).__init__('Transform', root_dcm_dir, root_label_dir, root_dst_dir, pipes, filters)

    def run(self, dst_dir, filename, dcm_filepath, label_filepath) -> Statistic or None:
        dst_filepath = os.path.join(dst_dir, '{}.png'.format(filename))

        _, _, _, dcm_image = create_segment_mask(dcm_filepath, label_filepath, remove_noise_intersection=True)
        dcm_image = cv2.cvtColor(dcm_image, cv2.COLOR_RGB2BGR)
        return self.pipelines(dst_filepath, dcm_image)
