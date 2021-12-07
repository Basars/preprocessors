from .mode import Mode


class ROI(Mode):

    def __init__(self, root_dcm_dir, root_label_dir, root_dst_dir):
        super(ROI, self).__init__('ROI', root_dcm_dir, root_label_dir, root_dst_dir)

    def run(self, dst_dir, filename, dcm_filepath, label_filepath):
        # TODO: Add ROI processing
        super(ROI, self).run(dst_dir, filename, dcm_filepath, label_filepath)
