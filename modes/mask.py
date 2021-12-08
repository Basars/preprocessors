import os

from .mode import Mode
from preprocessors import create_segment_mask


class Mask(Mode):

    def __init__(self, root_dcm_dir, root_label_dir, root_dst_dir, pipes):
        super(Mask, self).__init__('Mask', root_dcm_dir, root_label_dir, root_dst_dir, pipes)

    def run(self, dst_dir, filename, dcm_filepath, label_filepath):
        dst_filepath = os.path.join(dst_dir, '{}.png'.format(filename))

        _, mask, _, _ = create_segment_mask(dcm_filepath, label_filepath, remove_noise_intersection=True)
        return self.finish_and_save(dst_filepath, mask)
