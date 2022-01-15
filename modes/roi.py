import os
import cv2

from .mode import Mode
from preprocessors import create_segment_mask


class ROI(Mode):

    def __init__(self, root_dcm_dir, root_label_dir, root_dst_dir, pipes, filters):
        super(ROI, self).__init__('ROI', root_dcm_dir, root_label_dir, root_dst_dir, pipes, filters)

    def run(self, dst_dir, filename, dcm_filepath, label_filepath):
        dst_filepath = os.path.join(dst_dir, '{}.png'.format(filename))

        _, mask, _, noise_eliminated = create_segment_mask(dcm_filepath, label_filepath, remove_noise_intersection=True)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
        mask = cv2.dilate(mask, kernel)

        image = cv2.bitwise_and(noise_eliminated, mask)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        return self.pipelines(dst_filepath, image)
