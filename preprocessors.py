import cv2
import json

import pydicom as dcm
import numpy as np


def create_segment_mask(dicom_filepath, label_filepath, remove_noise_intersection=False):
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

    noise_eliminated, segmentation = remove_mask_noise_statically(dcm_image, mask)
    mask = segmentation  # override masks with translated segmentation
    combined = noise_eliminated.copy()
    combined[segmentation > 0] = 255
    mask[(segmentation == 0) & (mask > 0)] = 0 if remove_noise_intersection else 127
    return dcm_image, mask, combined, noise_eliminated


@DeprecationWarning
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


def remove_mask_noise_statically(rgb_img, segmentation):
    LEFT_PAD = 142

    M = np.array([[1, 0, (LEFT_PAD / 2 - 20) * -1],
                  [0, 1, 0]]).astype(np.float32)
    img = rgb_img.copy()
    img[0:img.shape[1], 0:LEFT_PAD] = (0, 0, 0)
    img[0:50, 0:LEFT_PAD + 28] = (0, 0, 0)

    height, width = img.shape[:2]
    img = cv2.warpAffine(img, M, (width, height))
    segmentation = cv2.warpAffine(segmentation, M, (width, height))
    return img, segmentation
