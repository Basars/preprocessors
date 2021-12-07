from .mode import Mode


class Masking(Mode):

    def __init__(self, root_dcm_dir, root_label_dir, root_dst_dir):
        super(Masking, self).__init__('Masking', root_dcm_dir, root_label_dir, root_dst_dir)

    def run(self, dst_dir, filename, dcm_filepath, label_filepath):
        # TODO: Add Masking processing
        super(Masking, self).run(dst_dir, filename, dcm_filepath, label_filepath)
