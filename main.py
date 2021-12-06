import argparse
from modes import Inspector


modes = {
    'inspectors': Inspector,
    'masking': None,
    'roi': None
}


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='This is a preprocessor to remote DICOM masks and generate segmentations and its inspectors.'
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
                        default=list(modes.keys())[0])
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
