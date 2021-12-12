import os
import shutil
import argparse
import pandas as pd
import numpy as np


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='This is an assigner for assigning dataset validation job fairly.',
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument('--csv-file',
                        required=True,
                        help='The assignees CSV file')
    parser.add_argument('--source-dirs',
                        required=True,
                        help='dir1,dir2,dir3,..  The source directories to be assigned to')
    parser.add_argument('--target-dir',
                        required=True,
                        help='The destination directory where the assigned directory will be located')

    args = parser.parse_args()
    return args.csv_file, args.source_dirs, args.target_dir


def main():
    print()
    csv_file, source_dirs, target_dir = parse_arguments()
    source_dirs = [dirname for dirname in source_dirs.split(',')]
    dirs_map = {}
    for source_dir in source_dirs:
        dirs = [f for f in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, f))]
        for dirname in dirs:
            dirs_map[dirname] = os.path.join(source_dir, dirname)
    print('Gathered {} available directories'.format(len(dirs_map.keys())))

    df = pd.read_csv(csv_file, dtype=str)
    df = df.dropna(how='all')

    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    os.makedirs(target_dir, exist_ok=True)

    columns = list(df.columns)
    print('Assigning the patients to {} assignees'.format(len(columns)))
    for column in columns:
        os.mkdir(os.path.join(target_dir, column))

        patients = [e for e in list(df.loc[:, column].values) if e is not np.nan]
        print('Assigning {} patients to {}'.format(len(patients), column))
        for patient in patients:
            dirpath = dirs_map[patient]
            shutil.copytree(dirpath, os.path.join(target_dir, column, patient))
        print('Assigned {} patients to {}'.format(len(patients), column))
    print('All jobs have finished')


if __name__ == '__main__':
    main()
