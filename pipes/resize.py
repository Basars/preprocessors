import cv2
import numpy as np

from .pipe import Pipe
from statistic import Statistic


class Resize(Pipe):

    def __init__(self, new_size):
        super(Resize, self).__init__('Resize')

        self._new_size = new_size

    def apply(self, image) -> Statistic or np.ndarray:
        pre_height, pre_width = image.shape[0], image.shape[1]
        new_height, new_width = self._new_size

        larger_height = pre_height < new_height
        larger_width = pre_width < new_width
        shorter_height = pre_height > new_height
        shorter_width = pre_width > new_width

        is_stretching = (larger_height and shorter_width) or (larger_width and shorter_height)
        is_smaller = not larger_width and not larger_height
        is_bigger = not shorter_width and not shorter_height
        if is_stretching:
            interp = cv2.INTER_CUBIC
        elif is_smaller:
            interp = cv2.INTER_AREA
        elif is_bigger:
            interp = cv2.INTER_LINEAR
        else:
            return Statistic.from_key_value('out_of_resize_cases', 1)

        return cv2.resize(image, dsize=(new_height, new_width), interpolation=interp)
