import os
import cv2

from .mode import Mode
from preprocessors import create_segment_mask


class ROI(Mode):

    def __init__(self, root_dcm_dir, root_label_dir, root_dst_dir, pipes):
        super(ROI, self).__init__('ROI', root_dcm_dir, root_label_dir, root_dst_dir, pipes)

    def run(self, dst_dir, filename, dcm_filepath, label_filepath):
        dst_filepath = os.path.join(dst_dir, '{}.png'.format(filename))

        dcm_image, mask, _, _ = create_segment_mask(dcm_filepath, label_filepath, remove_noise_intersection=True)
        image = cv2.bitwise_and(dcm_image, mask)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        return self.finish_and_save(dst_filepath, image)
