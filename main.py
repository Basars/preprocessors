import argparse
import sys
import textwrap

from modes import Inspector, Mask, ROI
from pipes import Resize

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
    parser.add_argument('--new-shape',
                        help='WxH. Resize the output image with desired width and height')
    parser.add_argument('--jobs',
                        default=-1,
                        help='Number of workers')

    args = parser.parse_args()

    if args.new_shape is not None:
        if 'x' not in args.new_shape:
            print('{}: error: the following argument --new-shape requires follow WxH format'.format(__file__))
            sys.exit(1)
        new_shape = args.new_shape.split('x')
    else:
        new_shape = None

    return args.dcm_dir, args.label_dir, args.target_dir, args.mode, int(args.jobs), new_shape


def main():
    print()
    dcm_dirpath, label_dirpath, target_dirpath, mode_name, jobs, new_shape = parse_arguments()
    mode_type = modes[mode_name]
    if mode_type is None:
        print('Unrecognizable mode argument: {}'.format(mode_name))
        return

    pipes = []
    if new_shape is not None:
        pipe = Resize((int(new_shape[1]), int(new_shape[0])))  # WxH -> HxW
        pipe.inform()
        pipes.append(pipe)

    mode = mode_type(dcm_dirpath, label_dirpath, target_dirpath, pipes)
    statistic = mode.parse_and_preprocess_dirs(jobs)
    print("Job statistics:")
    for name, count in statistic.container.items():
        print('\t{}: {}'.format(name, count))


if __name__ == '__main__':
    main()
