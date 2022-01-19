from xml.etree.ElementTree import fromstring
from statistic import Statistic
from preprocessors import translate_polygons_statically
from .overwriter import Overwriter


class CVAT(Overwriter):

    def __init__(self):
        super(CVAT, self).__init__('CVAT')

    def parse(self, label_file) -> Statistic or dict:
        root = fromstring(label_file.read())
        overwritable_labels = {}
        for image_el in root.findall('image'):
            image_name = image_el.attrib['name']
            person_id = image_name.split('_')[0]
            width = int(image_el.attrib['width'])
            height = int(image_el.attrib['height'])

            polygons = image_el.findall('polygon')

            phase_id = None
            annotations = []
            for polygon in polygons:
                annotation = {
                    'category': 'cancer',
                    'label_type': 'polygon'
                }
                phase_id = polygon.attrib['label'].split('_')[1]  # phase_5 -> 5
                points = polygon.attrib['points']

                coordinates = []
                pairs = points.split(';')
                for pair in pairs:
                    coordinate = [float(s) for s in pair.split(',')]
                    coordinates.append(coordinate)
                coordinates = translate_polygons_statically(coordinates, reverse=True)[0]
                annotation['polygon'] = coordinates.tolist()
                annotations.append(annotation)

            body = {
                'image': {
                    'person_id': person_id,
                    'width': width,
                    'height': height,
                    'annotations': annotations
                }
            }
            if phase_id is not None:
                body['image']['phase_id'] = int(phase_id)
            overwritable_labels[image_name.split('.')[0]] = body
        return overwritable_labels
