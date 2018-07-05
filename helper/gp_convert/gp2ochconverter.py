from helper.gp_convert.nmealib import *
from helper.gp_convert.ochlib import *
import pytz

class GpToOchConverter:
    def __init__(self):
        self.__ochMessageList = []

    def __readGpFile(self, filepath):
        file = open(filepath, "r")
        contents = file.readlines()
        return contents

    def __parseNmeaMessageToOchMessage(self, nmeaMessage):
        if nmeaMessage is None or not nmeaMessage.isValid():
            return None

        ochMessage = OchMessage()
        if nmeaMessage.messageCode in NmeaUtils.MessageType.RMC:
            ochMessage.latitude = NmeaParser.messageToLatitudeDecimal(nmeaMessage.latitudeDms, nmeaMessage.northOrSouth)
            ochMessage.longitude = NmeaParser.messageToLongitudeDecimal(nmeaMessage.longitudeDms,
                                                                        nmeaMessage.eastOrWest)
            ochMessage.speed = NmeaParser.messageToSpeedKilos(nmeaMessage.speedKnot)
            ochMessage.datetime = NmeaParser.messageToDatetime(nmeaMessage.utcDateStamp, nmeaMessage.utcTimeStamp)
            ochMessage.datetime = ochMessage.datetime.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Seoul'))  # UTC+09 Korea Standard Time

        if ochMessage is not None and ochMessage.isValid():
            return ochMessage
        else:
            return None

    def __convert(self, sourceFilepath):
        contents = self.__readGpFile(sourceFilepath)

        self.__ochMessageList.clear()
        for i in range(len(contents)):
            strLine = contents[i]

            if not NmeaUtils.isNmeaFormat(strLine):
                continue

            try:
                nmeaMessageType = NmeaMessage.getMessageType(strLine)

                nmeaMessage = None
                if nmeaMessageType == NmeaUtils.MessageType.RMC:
                    nmeaMessage = NmeaRmcMessage(strLine)
                    if not nmeaMessage.isStable():
                        continue

                ochElement = self.__parseNmeaMessageToOchMessage(nmeaMessage)
            except ValueError:
                continue

            if ochElement is not None:
                self.__ochMessageList.append(ochElement)

    def convertToOchFile(self, sourceFilepath, targetFilepath):
        self.__convert(sourceFilepath)

        f = open(targetFilepath, 'w+')
        for i in range(len(self.__ochMessageList)):
            f.write(self.__ochMessageList[i].toString() + '\r\n')

