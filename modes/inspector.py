import os
import matplotlib.pyplot as plt

from .mode import Mode
from preprocessors import create_segment_mask


class Inspector(Mode):

    def __init__(self, root_dcm_dir, root_label_dir, root_dst_dir):
        super(Inspector, self).__init__('Inspector', root_dcm_dir, root_label_dir, root_dst_dir)

    @staticmethod
    def save_inspector(filename, segment_result, dst_filepath):
        fig = plt.figure(figsize=(12, 6))
        exclusive = []
        index = 0
        for i in range(len(segment_result)):
            if i in exclusive:
                continue
            index += 1
            img = segment_result[i]
            ax = fig.add_subplot(1, len(segment_result) - len(exclusive), index)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.imshow(img)

        fig.suptitle(filename)
        fig.tight_layout()
        fig.savefig(dst_filepath, transparent=False)
        plt.close(fig)

    def run(self, statistic, dst_dir, filename, dcm_filepath, label_filepath):
        dst_filepath = os.path.join(dst_dir, '{}_inspector.jpg'.format(filename))

        segmentation = create_segment_mask(dcm_filepath, label_filepath)
        if segmentation is None:
            statistic.increase('empty_annotations', 1)
            print(f"Annotations are not existed in '{label_filepath}'.")
            return False
        Inspector.save_inspector(filename, segmentation, dst_filepath)
        return True
