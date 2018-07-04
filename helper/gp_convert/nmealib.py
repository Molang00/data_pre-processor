from enum import Enum
from abc import abstractmethod
from datetime import datetime

class NmeaUtils:
    Delimiter = ','

    class MessageType():
        AAM = 'AAM'
        ALM = 'ALM'
        APA = 'APA'
        APB = 'APB'
        BOD = 'BOD'
        BWC = 'BWC'
        DTM = 'DTM'
        GGA = 'GGA'
        GLL = 'GLL'
        GRS = 'GRS'
        GSA = 'GSA'
        GST = 'GST'
        GSV = 'GSV'
        MSK = 'MSK'
        MSS = 'MSS'
        RMA = 'RMA'
        RMB = 'RMB'
        RMC = 'RMC'
        RTE = 'RTE'
        TRF = 'TRF'
        STN = 'STN'
        VBW = 'VBW'
        VTG = 'VTG'
        WCV = 'WCV'
        WPL = 'WPL'
        XTC = 'XTC'
        XTE = 'XTE'
        ZTG = 'ZTG'
        ZDA = 'ZDA'

    @staticmethod
    def isNmeaFormat(message):
        return message[0] is '$'

class NmeaMessage:

    def __init__(self, message):
        message = message.replace('\n', ' ').replace('\r', '')
        self._fullMessage = message
        self._tokens = message.split(NmeaUtils.Delimiter)
        self._messageType = self._tokens[0][3:6]

    @staticmethod
    def getMessageType(message):
        return message[:message.index(',')][3:6]

    @abstractmethod
    def __setData(self, message):
        pass

    @abstractmethod
    def isValid(self):
        return self._tokens[0] is not None and self._tokens[0][0] == '$'

    def toString(self):
        return self._fullMessage

    @property
    def messageCode(self):
        return self._messageType


class NmeaRmcMessage(NmeaMessage):
    def __init__(self, message):
        NmeaMessage.__init__(self, message)
        self.utcDateStamp = []
        self.utcTimeStamp = []
        self.latitudeDms = []
        self.northOrSouth = '' # north=N, south=S for latitude
        self.longitudeDms = []
        self.eastOrWest = '' # east=E, west=W for longitude
        self.altitude = -1
        self.speedKnot = -1
        self.activeOrVoid = '' # active=A, void=V
        self.__setData()

    def __setData(self):
        self.utcTimeStamp = self._tokens[1]
        self.activeOrVoid = self._tokens[2]
        self.latitudeDms = self._tokens[3]
        self.northOrSouth = self._tokens[4]
        self.longitudeDms = self._tokens[5]
        self.eastOrWest = self._tokens[6]
        self.speedKnot = self._tokens[7]
        self.utcDateStamp = self._tokens[9]

    def isValid(self):
        return super(NmeaRmcMessage, self).isValid and self._messageType == NmeaUtils.MessageType.RMC and self.activeOrVoid == 'A'


class NmeaParser:

    @staticmethod
    def messageToLatitudeDecimal(msg_latitude_dms, n_or_s):
        degree = int(msg_latitude_dms[0:(msg_latitude_dms.index('.') - 2)])
        minute = float(msg_latitude_dms[(msg_latitude_dms.index('.') - 2):])

        latitude = degree + minute / 60.0
        if n_or_s == 'S':
            latitude = - latitude
        return latitude

    @staticmethod
    def messageToLongitudeDecimal(msg_longitude_dms, e_or_w):
        degree = int(msg_longitude_dms[0:(msg_longitude_dms.index('.') - 2)])
        minute = float(msg_longitude_dms[(msg_longitude_dms.index('.') - 2):])

        longitude = degree + minute / 60.0
        if e_or_w == 'W':
            longitude = - longitude
        return longitude

    @staticmethod
    def messageToSpeedKilos(msg_speed_knots):
        return float(msg_speed_knots) * 1.852

    @staticmethod
    def messageToDatetime(utcDateStamp, utcTimeStamp):
        date = int(utcDateStamp[0:2])
        month = int(utcDateStamp[2:4])
        year = int(utcDateStamp[4:6]) + 2000
        hour = int(utcTimeStamp[0:2])
        minute = int(utcTimeStamp[2:4])
        second = int(utcTimeStamp[4:6])
        strms = utcTimeStamp[(utcTimeStamp.index('.') + 1):]
        for i in range(len(strms), 3):
            strms = strms + '0'
        millisecond = int(strms)

        dt = datetime(year, month, date, hour, minute, second, millisecond * 1000)
        return dt