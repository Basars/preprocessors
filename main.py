import argparse
import textwrap

from modes import Inspector, Mask, ROI

modes = {
    'inspector': Inspector,
    'mask': Mask,
    'roi': ROI
}


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='This is a preprocessor to remove DICOM masks '
                    'and generate segmentations and its inspectors, masks and ROIs.',
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument('--dcm-dir',
                        required=True,
                        help='The DICOM root directory')
    parser.add_argument('--label-dir',
                        required=True,
                        help='The JSON labels root directory')
    parser.add_argument('--target-dir',
                        required=True,
                        help='The destination root directory for outputs')
    parser.add_argument('--mode',
                        required=True,
                        choices=list(modes.keys()),
                        default=list(modes.keys())[0],
                        help=textwrap.dedent('''\
                        inspector    Generate four-in-one images to compare masks, overlay 
                                     and noise-eliminated with original image
                        mask         Generate binary masks that will be used as Dataset for segmentation models
                        roi          Generate region-of-interest images that will be used 
                                     as Dataset for classification model\
                        '''))
    parser.add_argument('--jobs',
                        default=-1,
                        help='Number of workers')

    args = parser.parse_args()
    return args.dcm_dir, args.label_dir, args.target_dir, args.mode, int(args.jobs)


def main():
    print()
    dcm_dirpath, label_dirpath, target_dirpath, mode_name, jobs = parse_arguments()
    mode_type = modes[mode_name]
    if mode_type is None:
        print('Unrecognizable mode argument: {}'.format(mode_name))
        return
    mode = mode_type(dcm_dirpath, label_dirpath, target_dirpath)
    statistic = mode.parse_and_preprocess_dirs(jobs)
    print("Job statistics:")
    for name, count in statistic.container.items():
        print('\t{}: {}'.format(name, count))


if __name__ == '__main__':
    main()
