import pandas as pd
import numpy as np
import math
import glob
import os


# gps좌표를 meter scale의 distance로 바꾸어준다
class Find_field_csv:

    # gps좌표를 meter scale의 distance로 바꾸어준다
    def measure(self, lat1, lon1, lat2, lon2):
        R = 6378.137
        dLat = (lat1 - lat2) * math.pi / 180
        dLon = (lon1 - lon2) * math.pi / 180
        a = math.sin(dLat / 2) * math.sin(dLat / 2) + \
            math.cos(lat1 * math.pi / 180) * math.cos(lat2 * math.pi / 180) * \
            math.sin(dLon / 2) * math.sin(dLon / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d = R * c
        return d * 1000

    def checkPointInRectangle2(self, pointP, pointA, pointB, pointD):

        vectorAB = np.array(np.subtract(pointB, pointA))
        vectorAD = np.array(np.subtract(pointD, pointA))
        vectorAP = np.array(np.subtract(pointP, pointA))

        ABsquare = np.dot(vectorAB, vectorAB)
        ADsquare = np.dot(vectorAD, vectorAD)
        ABmulAP = np.dot(vectorAB, vectorAP)
        ADmulAP = np.dot(vectorAD, vectorAP)

        if (0 < ABmulAP and ABmulAP < ABsquare and 0 < ADmulAP and ADmulAP < ADsquare):
            return True
        else:
            return False

    def checkPointInRectangle(self, pointP, pointA, pointB, pointC, pointD):
        b1 = False
        b2 = False

        if self.measure(pointP[0], pointP[1], pointA[0], pointA[1]) < 200:
            b1 = self.checkPointInTriangle(pointP, pointA, pointB, pointC)
            b2 = self.checkPointInTriangle(pointP, pointC, pointD, pointA)

        insideSquare = (b1 or b2)
        return insideSquare

    def checkPointInTriangle(self, pointP, pointA, pointB, pointC):
        '''return True if inside, return False if outside Triangle '''

        def sign(pointP, pointA, pointB):
            # distinguish side of point, criteria: line AB
            updown = (pointP[0] - pointB[0]) * (pointA[1] - pointB[1]) - (pointP[1] - pointB[1]) * (
                        pointA[0] - pointB[0])
            if updown >= 0:
                output = True
            else:
                output = False
            return output

        b1 = sign(pointP, pointA, pointB)
        b2 = sign(pointP, pointB, pointC)
        b3 = sign(pointP, pointC, pointA)

        insideTriangle = ((b1 == b2) and (b2 == b3))

        return insideTriangle

    # parsedfieldpath는 output.csv를 읽히는 것이다.
    def findField(self, longitude, latitude, parsedFieldFilePath):
        df = pd.read_csv(parsedFieldFilePath)
        output = []
        for i in range(len(df)):

            lonA, latA, lonB, latB, lonC, latC, lonD, latD = df.values[i][2:]

            pointP = (longitude, latitude)
            pointA = (lonA, latA)
            pointB = (lonB, latB)
            pointC = (lonC, latC)
            pointD = (lonD, latD)

            if self.checkPointInRectangle(pointP, pointA, pointB, pointC, pointD):
                output = list(df.values[i])  # 필드정보를 찾은 후 그 정보를 output에 담아낸다.
                break

        return output

    def find_field_csv_file(self, csv_file_path, field_info_path):
        output = []
        with open(csv_file_path, 'r') as f:
            lines = f.readlines()
            length = len(lines)
            i = 0
            while (i < length):  # if문으로 2.의 csv랑 3.의 csv읽을때마다 다르게 나오게 해주어야 함.
                try:
                    lon, lat = lines[i + 1].split(',')[7:9]  # 10hz기준
                except Exception as e:
                    print(e)
                field_data = self.findField(float(lon), float(lat), field_info_path)
                if field_data != []:
                    output = field_data
                    break
                i += 3000  # 5분단위
        return output

    def find_field_csv_folder(self, csv_folder_path, field_info_path, path_to_save):
        outputList = []
        files_csv = glob.glob(csv_folder_path + '*.csv')
        # int로 바꿔서 sorting해주는 알고리즘도 해주면 좋을듯
        for file_csv in files_csv:
            csv_file_path = os.path.join(str(file_csv)).replace("\\", "/")
            print('csvfilepath:' + csv_file_path)
            field_data = self.find_field_csv_file(csv_file_path, field_info_path)
            outputList.append([file_csv, field_data])
            # 디렉토리가 없으면은 생성해준다.
            try:
                if not os.path.exists(path_to_save):
                    os.makedirs(path_to_save)
            except OSError:
                print('Error: Creating directory.' + path_to_save)

        with open(path_to_save + "fieldmatch.txt", "w+", encoding="utf-8") as f:
            lines = "\n".join(e[0] + ", " + str(e[1]) for e in outputList)
            f.writelines(lines)

if __name__ == "__main__":
    # 현재는 data/2.data_csv_format/폴더만 하는데 이것도 선택할 수 있게 인자로 처리할 수 있을 것 같고, 그경우마다 위에 시간체크하는거 달라질수 있을듯
    csv_dir_path = 'data/2. data_csv_format/'
    info_path = 'helper/output.csv'
    path_to_save = 'data/8. data_field_find/'
    name_of_dir = '드래곤즈 0617/'

    Find_field_csv()
    find_field = Find_field_csv()
    find_field.find_field_csv_folder(csv_dir_path + name_of_dir, info_path, path_to_save + name_of_dir)
