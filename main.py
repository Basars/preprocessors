import os
import cv2
import json
import argparse

import pydicom as dcm
import matplotlib.pyplot as plt
import numpy as np


def create_segment_mask(dicom_filepath, label_filepath):
    dcm_file = dcm.dcmread(dicom_filepath)
    dcm_image = dcm_file.pixel_array

    with open(label_filepath, 'r', encoding='euc-kr') as f:
        label = json.load(f)

    mask = np.zeros(dcm_image.shape, dtype=np.uint8)
    annotations = label['image']['annotations']
    n_annotations = len(annotations)

    for i in range(n_annotations):
        polygons = np.array(annotations[i]['polygon'], dtype=np.int32)
        cv2.fillPoly(mask, [polygons], (255, 255, 255))

    combined, segmentation = remove_mask_noise(dcm_image, mask)
    combined[segmentation > 0] = 255
    mask[(segmentation == 0) & (mask > 0)] = 127
    return dcm_image, mask, combined


def remove_mask_noise(rgb_img, segmentation):
    gray = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2GRAY)
    _, gray = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)
    gray = cv2.blur(gray, (5, 5))
    gray[gray > 254] = 0

    kernel_5x5 = np.ones((5, 5), np.uint8)
    kernel_50x50 = np.ones((50, 50), np.uint8)
    kernel_3x3 = np.ones((3, 3), np.uint8)
    gray = cv2.dilate(gray, kernel_5x5)
    gray = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel_50x50)  # erode -> dilate
    gray = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel_3x3)  # dilate -> erode

    src_img = rgb_img.copy()
    src_img[gray > 127] = 0

    segmentation = segmentation.copy()
    segmentation[gray > 127] = 0
    return src_img, segmentation


def save_segmentation_inspector(filename, segment_result, dst_filepath):
    fig = plt.figure(figsize=(14, 6))
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
    plt.suptitle(filename)
    plt.tight_layout()
    plt.savefig(dst_filepath, transparent=False)
    plt.close(fig)


def segment_dataset_inspector_pair(dcm_dir, label_dir, dst_dir, verbose=2):
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir, exist_ok=True)
    dcm_files = os.listdir(dcm_dir)
    label_files = os.listdir(label_dir)

    files = dcm_files if len(dcm_files) > len(label_files) else label_files
    if verbose > 0:
        print(f"Starting to generate {len(files)} segmentation inspector files...")
    success = 0
    not_existed = 0
    empty_annotations = 0
    for filename in files:
        filename = filename.split('.')[0]

        dcm_filepath = os.path.join(dcm_dir, '{}.dcm'.format(filename))
        json_filepath = os.path.join(label_dir, '{}.json'.format(filename))
        dst_filepath = os.path.join(dst_dir, '{}_inspector.jpg'.format(filename))

        dcm_existence = os.path.exists(dcm_filepath)
        json_existence = os.path.exists(json_filepath)
        if not dcm_existence or not json_existence:
            not_existed += 1
            if verbose > 0:
                if not dcm_existence:
                    print(f"'{dcm_filepath}' is not existed despite its label is existed.")
                else:
                    print(f"'{json_filepath} is not existed despite its DICOM file is existed.")
            continue

        segmentation = create_segment_mask(dcm_filepath, json_filepath)
        if segmentation is None:
            empty_annotations += 1
            if verbose > 0:
                print(f"Annotations are not existed in '{json_filepath}'.")
            continue

        save_segmentation_inspector(filename, segmentation, dst_filepath)
        success += 1
    if verbose > 1:
        print(f"Total {success} segmentation inspector files have been generated.")
        if not_existed > 0 or empty_annotations > 0:
            print(
                f"However, {not_existed} files are not matched each other, "
                f"{empty_annotations} files does not contains proper annotations"
            )

    return success, not_existed, empty_annotations


def create_dataset_inspector(root_dcm_dir, root_label_dir, root_dst_dir, mode):
    dcm_subdirs = sorted([subdir
                          for subdir in os.listdir(root_dcm_dir)
                          if os.path.isdir(os.path.join(root_dcm_dir, subdir))])
    label_subdirs = sorted([subdir
                            for subdir in os.listdir(root_label_dir)
                            if os.path.isdir(os.path.join(root_label_dir, subdir))])
    assert len(dcm_subdirs) == len(label_subdirs)

    success, not_existed, empty_annotations = 0, 0, 0
    for dcm_subdir, label_subdir in zip(dcm_subdirs, label_subdirs):
        assert dcm_subdir == label_subdir

        dcm_dir = os.path.join(root_dcm_dir, dcm_subdir, "ENDO")
        label_dir = os.path.join(root_label_dir, label_subdir, "ENDO")
        dst_dir = os.path.join(root_dst_dir, dcm_subdir)
        result = segment_dataset_inspector_pair(dcm_dir,
                                                label_dir,
                                                dst_dir,
                                                verbose=1)  # no totality announcements
        success += result[0]
        not_existed += result[1]
        empty_annotations += result[2]
    print(f"Total {success} segmentation inspector files have been generated.")
    if not_existed > 0 or empty_annotations > 0:
        print(
            f"However, {not_existed} files are not matched each other, "
            f"{empty_annotations} files does not contains proper annotations"
        )


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
                        choices=['inspectors', 'segments'],
                        default='inspectors')

    args = parser.parse_args()
    return args.dcm_dir, args.label_dir, args.target_dir, args.mode


if __name__ == '__main__':
    print()
    dcm_dirpath, label_dirpath, target_dirpath, mode = parse_arguments()
    create_dataset_inspector(dcm_dirpath, label_dirpath, target_dirpath, mode)
    print('Jobs finished.')
