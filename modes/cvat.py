import os

from xml.etree.ElementTree import Element, SubElement, ElementTree

import cv2

from .mode import Mode
from preprocessors import read_dcm_and_labels, create_segment_mask, translate_polygons_statically
from statistic import Statistic


PHASES = [1, 2, 3, 4]  # phase 1 ~ 4


class CVAT(Mode):

    def __init__(self, root_dcm_dir, root_label_dir, root_dst_dir, _, filters):
        super(CVAT, self).__init__('CVAT 1.1', root_dcm_dir, root_label_dir, root_dst_dir, [], filters)

        self._make_patient_dir = False

        self.images_dir = os.path.join(self.root_dst_dir, 'images')

        os.makedirs(self.root_dst_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)

        self.annotations = self.setup_template()
        self.id = 0

    def id_gen(self):
        self.id += 1
        return str(self.id)

    def setup_template(self):
        annotations = Element('annotations')
        version = SubElement(annotations, 'version')
        version.text = '1.1'

        meta = SubElement(annotations, 'meta')
        task = SubElement(meta, 'task')
        mode = SubElement(task, 'mode')
        mode.text = 'annotation'
        overlap = SubElement(task, 'overlap')
        overlap.text = '0'
        flipped = SubElement(task, 'flipped')
        flipped.text = 'False'
        labels = SubElement(task, 'labels')
        for phase in PHASES:
            label = SubElement(labels, 'label')
            name = SubElement(label, 'name')
            name.text = 'phase_{}'.format(phase)
            attributes = Element('attributes')
            label.append(attributes)
        return annotations

    def prettier(self, element, level=0):
        i = '\n' + level * '  '
        if len(element):
            if not element.text or not element.text.strip():
                element.text = i + '  '
            if not element.tail or not element.tail.strip():
                element.tail = i
            for element in element:
                self.prettier(element, level + 1)
            if not element.tail or not element.tail.strip():
                element.tail = i
        else:
            if level and (not element.tail or not element.tail.strip()):
                element.tail = i

    def finish(self):
        self.prettier(self.annotations)
        ElementTree(self.annotations).write(os.path.join(self.root_dst_dir, 'annotations.xml'),
                                            encoding='utf-8',
                                            xml_declaration=True)

    def run(self, dst_dir, filename, dcm_filepath, label_filepath) -> Statistic or None:
        filename = '{}.png'.format(filename)
        _, polygons, phase = read_dcm_and_labels(dcm_filepath, label_filepath)
        _, _, _, dcm_image = create_segment_mask(dcm_filepath, label_filepath, remove_noise_intersection=True)
        stats = []
        for polygon in polygons:
            if len(polygon) == 1 or len(polygon) == 2:
                stats.append(Statistic.from_key_value('invalid_polygons_{}'.format(len(polygon)), 1))
        if len(stats) > 0:
            return Statistic(*stats)
        dcm_image = self.apply_pipelines(dcm_image)
        if isinstance(dcm_image, Statistic):
            return dcm_image  # Statistic

        shape = dcm_image.shape

        image_el = SubElement(self.annotations, 'image')
        image_el.attrib['id'] = self.id_gen()
        image_el.attrib['name'] = filename
        image_el.attrib['width'] = str(shape[1])
        image_el.attrib['height'] = str(shape[0])

        for polygon in polygons:
            el = Element('polygon',
                         label='phase_{}'.format(phase),
                         occluded='0',
                         source='manual',
                         z_order='0')
            polygon = translate_polygons_statically(polygon)[0]
            coordinates = [','.join([str(point) for point in pair]) for pair in polygon]
            el.attrib['points'] = ';'.join(coordinates)
            image_el.append(el)

        dcm_image = cv2.cvtColor(dcm_image, cv2.COLOR_RGB2BGR)
        cv2.imwrite(os.path.join(self.images_dir, filename), dcm_image)
        return None
