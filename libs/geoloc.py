class Coordinates:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude
    def __repr__(self):
        return "%s;%s" % (self.latitude, self.longitude)
    def __add__(self, other):
        return Coordinates(self.latitude + other.latitude,
            self.longitude + other.longitude)


class Area:
    def __init__(self, coord1, coord2):
        self.corner_1 = coord1
        self.corner_2 = coord2

    def __repr__(self):
        return "%s TO %s" % (self.corner_1, self.corner_2)

    # Size of area is one side times the other
    def __size__(self):
        return corner_1.latitude - corner_2.latitude * corner_1.longitude - corner_2.longitude


class Path(list):
    def __init__(self):
        return self.list()

    def __repr__(self):
        # Calculate scale for cli representation
        pass
