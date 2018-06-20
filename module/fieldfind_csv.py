import pandas as pd
import numpy as np
import math

# gps좌표를 meter scale의 distance로 바꾸어준다
def measure(lat1, lon1, lat2, lon2):
    R = 6378.137
    dLat = (lat1 - lat2) * math.pi / 180
    dLon = (lon1 - lon2) * math.pi / 180
    a = math.sin(dLat / 2) * math.sin(dLat / 2) + \
        math.cos(lat1 * math.pi / 180) * math.cos(lat2 * math.pi / 180) * \
        math.sin(dLon / 2) * math.sin(dLon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = R * c
    return d * 1000

def checkPointInRectangle2(pointP, pointA, pointB, pointD):

    vectorAB = np.array(np.subtract(pointB, pointA))
    vectorAD = np.array(np.subtract(pointD, pointA))
    vectorAP = np.array(np.subtract(pointP, pointA))

    ABsquare = np.dot(vectorAB ,vectorAB)
    ADsquare = np.dot(vectorAD, vectorAD)
    ABmulAP  = np.dot(vectorAB, vectorAP)
    ADmulAP  = np.dot(vectorAD, vectorAP)

    if(0 < ABmulAP and ABmulAP < ABsquare and 0 < ADmulAP and ADmulAP < ADsquare):
        return True
    else:
        return  False

def checkPointInRectangle(pointP, pointA, pointB, pointC, pointD):
    b1 = False
    b2 = False

    if measure(pointP[0], pointP[1], pointA[0], pointA[1]) < 200:
        b1 = checkPointInTriangle(pointP, pointA, pointB, pointC)
        b2 = checkPointInTriangle(pointP, pointC, pointD, pointA)

    insideSquare = (b1 or b2)
    return insideSquare


def checkPointInTriangle(pointP, pointA, pointB, pointC):
    '''return True if inside, return False if outside Triangle '''

    def sign(pointP, pointA, pointB):
        # distinguish side of point, criteria: line AB
        updown = (pointP[0] - pointB[0]) * (pointA[1] - pointB[1]) - (pointP[1] - pointB[1]) * (pointA[0] - pointB[0])
        if updown >= 0:
            output = True
        else:
            output = False
        return output

    b1 = sign(pointP, pointA, pointB)
    b2 = sign(pointP, pointB, pointC)
    b3 = sign(pointP, pointC, pointA)

    insideTriangle = ((b1 == b2) and (b2 == b3))

    return  insideTriangle

def findField(longitude, latitude, parsedFieldFilePath):
    df = pd.read_csv(parsedFieldFilePath)
    output = []
    for i in range(len(df)):

        lonA, latA, lonB, latB, lonC, latC, lonD, latD = df.values[i][2:]

        pointP = (longitude, latitude)
        pointA = (lonA, latA)
        pointB = (lonB, latB)
        pointC = (lonC, latC)
        pointD = (lonD, latD)

        if checkPointInRectangle(pointP, pointA, pointB, pointC, pointD):
            output = list(df.values[i])
            break

    return output

def findFieldWithOchFile(ochFilePath, parsedFieldFilePath):
    output = []

    with open(ochFilePath,"r") as f:
        lines =  f.readlines()
        length = len(lines)
        i = 0
        while ( i < length):
            try:
                lon, lat = lines[i].split(" ")[1:3]
            except Exception as e:
                print(e)
            fieldData = findField(float(lon), float(lat), parsedFieldFilePath)
            if fieldData != []:
                output = fieldData
                break
            i += 3000 #5분단위
    return output

def  findFieldWithOchFolder(ochFolderPath, parsedFieldFilePath):

    import model.ochFolder as ochFolder
    import os
    ochFolderObject = ochFolder.ochFolder()
    ochFolderObject.setFolder(ochFolderPath)
    dirpath = ochFolderObject.dirpath
    ochFiles = ochFolderObject.purefiles

    outputList = []
    for ochFile in ochFiles:
        ochFilePath = os.path.join(dirpath, str(ochFile)).replace("\\","/") + ".och"

        fieldData = findFieldWithOchFile(ochFilePath, parsedFieldFilePath)
        outputList.append([ochFile+".och", fieldData])

    with open(dirpath+"/fieldmatch.txt", "w+", encoding="utf-8") as f:
        lines = "\n".join(e[0] + ", " + str(e[1]) for e in outputList)
        f.writelines(lines)

if __name__ == "__main__":
    parsedFieldFilePath = "output.csv"

    # ---------------------------------------------------------------------
    # 단일 och폴더 (다중 och파일)
    ochFolderPath = input("폴더를 입력하세요").replace("\\", "/")
    #ochFolderPath = "C:/Users/fitogether/Documents/AuFe/temp/testFolder5 All in"

    import model.ochFolder as ochFolder
    import os
    ochFolderObject = ochFolder.ochFolder()
    ochFolderObject.setFolder(ochFolderPath)
    dirpath = ochFolderObject.dirpath
    ochFiles = ochFolderObject.purefiles

    outputList = []
    for ochFile in ochFiles:
        ochFilePath = os.path.join(dirpath, str(ochFile)).replace("\\","/") + ".och"

        fieldData = findFieldWithOchFile(ochFilePath, parsedFieldFilePath)
        outputList.append([ochFile+".och", fieldData])

    with open(dirpath+"/fieldmatch.txt", "w+", encoding="utf-8") as f:
        lines = "\n".join(e[0] + ", " + str(e[1]) for e in outputList)
        f.writelines(lines)

'''
    # ---------------------------------------------------------------------
    #단일 좌표
    fieldData = findField(34.9411808333333, 127.72042966666, parsedFieldFilePath)
    print(fieldData)

    # ---------------------------------------------------------------------
    #단일 och파일 (다중 좌표)
    ochFilePath = "C:/Users/fitogether/Documents/AuFe/temp/10.och"
    fieldData = findFieldWithOchFile(ochFilePath, parsedFieldFilePath)
    print(fieldData)
'''