import argparse
import sys
import textwrap

from modes import Inspector, Mask, ROI, Spreadsheet
from pipes import Resize
from filters import PhaseFilter, FilterableFilter

modes = {
    'inspector': Inspector,
    'mask': Mask,
    'roi': ROI,
    'spreadsheet': Spreadsheet
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
                                     as Dataset for classification model
                        spreadsheet  Generate CSV files that contains encrypted
                                     patients identifiers and its file name
                        '''))
    parser.add_argument('--filterable-csv-file',
                        help='The CSV file to be used for filtering broken datasets out')
    parser.add_argument('--filterable-dataset-type',
                        choices=['train', 'valid', 'test'],
                        help='The type of dataset source directory for querying filterable CSV file')
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

    filterable_csv_file = args.filterable_csv_file
    filterable_dataset_type = args.filterable_dataset_type
    if (filterable_csv_file is not None and filterable_dataset_type is None) or \
       (filterable_csv_file is None and filterable_dataset_type is not None):
        print('{}: error: --filterable-csv-file and --filterable-dataset-type'
              ' arguments must be existed at the same time.')
        sys.exit(1)

    return args.dcm_dir, args.label_dir, args.target_dir, args.mode, int(args.jobs), new_shape, filterable_csv_file, filterable_dataset_type


def main():
    print()
    dcm_dirpath, label_dirpath, target_dirpath, mode_name, jobs, new_shape, filterable_csv_file, filterable_dataset_type = parse_arguments()
    mode_type = modes[mode_name]
    if mode_type is None:
        print('Unrecognizable mode argument: {}'.format(mode_name))
        return

    pipes = []
    filters = []
    if new_shape is not None:
        pipe = Resize((int(new_shape[1]), int(new_shape[0])))  # WxH -> HxW
        pipes.append(pipe)

    if filterable_csv_file is not None and filterable_dataset_type is not None:
        filters.append(FilterableFilter(filterable_csv_file, filterable_dataset_type))

    for pipe in pipes:
        pipe.inform()

    # Filters
    filters.append(PhaseFilter())

    mode = mode_type(dcm_dirpath, label_dirpath, target_dirpath, pipes, filters)
    statistic = mode.parse_and_preprocess_dirs(jobs)
    print("Job statistics:")
    for name, count in statistic.container.items():
        print('\t{}: {}'.format(name, count))


if __name__ == '__main__':
    main()
