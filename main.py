import argparse
import sys
import textwrap
import overwriters

from modes import Inspector, Mask, ROI, Spreadsheet, CVAT, Transform
from pipes import Resize, Crop
from filters import PhaseFilter, FilterableFilter
from statistic import Statistic

MODES = {
    'inspector': Inspector,
    'mask': Mask,
    'roi': ROI,
    'spreadsheet': Spreadsheet,
    'cvat': CVAT,
    'transform': Transform
}


OVERWRITERS = {
    'cvat': overwriters.CVAT
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
                        choices=list(MODES.keys()),
                        default=list(MODES.keys())[0],
                        help=textwrap.dedent('''\
                        inspector    Generate four-in-one images to compare masks, overlay 
                                     and noise-eliminated with original image
                        mask         Generate binary masks that will be used as Dataset for segmentation models
                        roi          Generate region-of-interest images that will be used 
                                     as Dataset for classification model
                        spreadsheet  Generate CSV files that contains encrypted
                                     patients identifiers and its file name
                        cvat         Generate a XML file that contains segmentation mask polygons
                                     to be uploaded on CVAT
                        transform    Generate the original dataset images but necessarily transformed
                        '''))
    parser.add_argument('--filterable-csv-file',
                        help='The CSV file to be used for filtering broken datasets out')
    parser.add_argument('--filterable-dataset-type',
                        choices=['train', 'valid', 'test'],
                        help='The type of dataset source directory for querying filterable CSV file')
    parser.add_argument('--filterable-keep-issues',
                        action='store_true',
                        help='A flag to keep issued rows in filterable CSV file')
    parser.add_argument('--overwrite-label-type',
                        choices=['cvat'],
                        help=textwrap.dedent('''\
                        The type of overrideable labels format to parse
                        
                        cvat        CVAT 1.1 XML annotation format
                                    Pass 'annotations.xml' file to --overwrite-label-file argument
                        '''))
    parser.add_argument('--overwrite-label-file',
                        help='The label file to be used for overwriting dataset labels')
    parser.add_argument('--new-shape',
                        help='WxH. Resize the output image with desired width and height - e.g.) 224x224')
    parser.add_argument('--crop-image',
                        help='X:Y,W:H. Crop the output image to desired rectangle - e.g.) 90:0,480:480')
    parser.add_argument('--jobs',
                        default=-1,
                        help='Number of workers')

    args = parser.parse_args()

    if args.new_shape is not None:
        if 'x' not in args.new_shape:
            print('{}: error: the following argument --new-shape requires to follow WxH format'.format(__file__))
            sys.exit(1)
        new_shape = args.new_shape.split('x')
    else:
        new_shape = None

    if args.crop_image is not None:
        pairs = args.crop_image.split(',')
        if ':' not in args.crop_image or ',' not in args.crop_image or len(pairs) != 2:
            print('{}: error: the following argument --crop-image requires to follow X:Y,W:H format'.format(__file__))
            sys.exit(1)

        coordinate, size = [pair.split(':') for pair in pairs]
        crop_rect = {
            'x': coordinate[0],
            'y': coordinate[1],
            'w': size[0],
            'h': size[1]
        }
    else:
        crop_rect = None

    filterable_csv_file = args.filterable_csv_file
    filterable_dataset_type = args.filterable_dataset_type
    filterable_keep_issues = args.filterable_keep_issues
    if (filterable_csv_file is not None and filterable_dataset_type is None) or \
       (filterable_csv_file is None and filterable_dataset_type is not None):
        print('{}: error: --filterable-csv-file and --filterable-dataset-type'
              ' arguments must be existed at the same time.'.format(__file__))
        sys.exit(1)
    if filterable_keep_issues and (filterable_csv_file is None or filterable_dataset_type is None):
        print('{}: error: --filterable-csv-file and --filterable-dataset-type'
              ' arguments must be existed when --filterable-keep-issues exists.'.format(__file__))
        sys.exit(1)

    overwrite_label_type = args.overwrite_label_type
    overwrite_label_file = args.overwrite_label_file
    if (overwrite_label_type is not None and overwrite_label_file is None) or \
       (overwrite_label_type is None and overwrite_label_file is not None):
        print('{}: error: --overwrite-label-type and --overwrite-label-file'
              ' arguments must be existed at the same time.'.format(__file__))
        sys.exit(1)

    return args.dcm_dir, args.label_dir, args.target_dir, \
           args.mode, int(args.jobs), \
           new_shape, crop_rect, filterable_csv_file, filterable_dataset_type, filterable_keep_issues, \
           overwrite_label_type, overwrite_label_file


def main():
    print()
    dcm_dirpath, label_dirpath, target_dirpath, \
    mode_name, jobs, \
    new_shape, crop_rect, \
    filterable_csv_file, filterable_dataset_type, filterable_keep_issues, \
    overwrite_label_type, overwrite_label_file = parse_arguments()

    if mode_name not in MODES:
        print('Unrecognizable mode argument: {}'.format(mode_name))
        return

    mode_type = MODES[mode_name]

    pipes = []
    filters = []

    # Cropping have lower priority than resizing
    if crop_rect is not None:
        pipe = Crop(**crop_rect)
        pipes.append(pipe)

    if new_shape is not None:
        pipe = Resize((int(new_shape[1]), int(new_shape[0])))  # WxH -> HxW
        pipes.append(pipe)

    if filterable_csv_file is not None and filterable_dataset_type is not None:
        filters.append(FilterableFilter(filterable_csv_file, filterable_dataset_type, filterable_keep_issues))

    for pipe in pipes:
        pipe.inform()

    # Filters
    filters.append(PhaseFilter())

    # Overwriters
    overwriter = None
    if overwrite_label_type is not None and overwrite_label_file is not None:
        if overwrite_label_type not in OVERWRITERS:
            print('Unrecognizable overwriter argument: {}'.format(overwrite_label_type))
            return
        overwriter = OVERWRITERS[overwrite_label_type]

    if overwriter is not None:
        overwriter = overwriter()
        print('Current overwriter: {}'.format(overwriter.name))
        overwritable_labels = overwriter.parse_labels(overwrite_label_file)
    else:
        overwritable_labels = None

    if overwritable_labels is None or not isinstance(overwritable_labels, Statistic):
        mode = mode_type(dcm_dirpath, label_dirpath, target_dirpath, pipes, filters)
        if overwritable_labels is not None:
            mode.set_overwritable_labels(overwritable_labels)
        statistic = mode.parse_and_preprocess_dirs(jobs)
    else:
        statistic = overwritable_labels

    print("Job statistics:")
    for name, count in statistic.container.items():
        print('\t{}: {}'.format(name, count))


if __name__ == '__main__':
    main()
