class MinutiaeFeature(object):
    def __init__(self, locX, locY, Orientation, Type):
        self.locX = locX
        self.locY = locY
        self.Orientation = Orientation
        self.Type = Type

class MinutiaeConverter(object):
    def convert_minutiae_to_descriptors(self, minutiae_features):
        minutiae_dicts = []
        for feature in minutiae_features:
            minutiae_dict = {
                'locX': int(feature.locX),
                'locY': int(feature.locY),
                'Orientation': [int(x) for x in feature.Orientation],
                'Type': feature.Type
            }
            minutiae_dicts.append(minutiae_dict)
        return minutiae_dicts