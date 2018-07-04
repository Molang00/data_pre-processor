from datetime import datetime

class OchMessage:
    DATETIME_FORMAT = '%Y.%m.%d.%H.%M.%S.%f'

    def __init__(self):
        self.latitude = 0
        self.longitude = 0
        self.speed = -1
        self.datetime = None

    def isValid(self):
        return -90 <= self.latitude <= 90 and -180 <= self.longitude <= 180 and self.speed >= 0 and datetime is not None

    def toString(self):
        return "{} {} {} {:.6f}".format(self.datetime.strftime(OchMessage.DATETIME_FORMAT)[:-5], self.latitude, self.longitude, self.speed)
