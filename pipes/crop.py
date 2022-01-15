import numpy as np

from .pipe import Pipe
from statistic import Statistic


class Crop(Pipe):

    def __init__(self, x, y, w, h):
        super(Crop, self).__init__('Crop')

        self.x = int(x)
        self.y = int(y)
        self.w = int(w)
        self.h = int(h)

    def apply(self, image) -> Statistic or np.ndarray:
        return image[self.y:self.y + self.h, self.x:self.x + self.w]
