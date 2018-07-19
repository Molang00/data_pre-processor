import pandas as pd
import math
import glob
import os

# gps좌표를 meter scale의 distance로 바꾸어준다
class Find_field_csv:

    def expand_field(self, pointA, pointB, pointC, pointD, expansion_rate=1):
        center = ((pointA[0] + pointB[0] + pointC[0] + pointD[0]) / 4, (pointA[1] + pointB[1] + pointC[1] + pointD[1]) / 4)
        new_A = self.expansion(pointA, center, expansion_rate)
        new_B = self.expansion(pointB, center, expansion_rate)
        new_C = self.expansion(pointC, center, expansion_rate)
        new_D = self.expansion(pointD, center, expansion_rate)


        return new_A, new_B, new_C, new_D

    def expansion(self, point, center, rate):
        x = center[0] + (point[0] - center[0]) * rate
        y = center[1] + (point[1] - center[1]) * rate
        return (x, y)


    def check_slash(self, path_string):
        # path_string 원하는 경로를 string으로 저장

        # path의 마지막 경로에 /혹은 \가 없다면 /를 추가하여 return
        if path_string[len(path_string) - 1] != '/' and path_string[len(path_string) - 1] != '\\':
            path_string = path_string + '/'
        return path_string

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

            pointA, pointB, pointC, pointD = self.expand_field(pointA, pointB, pointC, pointD, 1.2)

            if self.checkPointInRectangle(pointP, pointA, pointB, pointC, pointD):
                output = list(df.values[i])  # 필드정보를 찾은 후 그 정보를 output에 담아낸다.
                break

        return output

    def find_field_csv_file(self, csv_file_path, field_info_path):
        tmp_field_data = []
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
                    if output == field_data: #단위 시간 이후 같은 경기장에 있을 경우에 break and return 하도록 한다
                        break
                    else:
                        output = field_data
                i += 3000  # 5분단위
        return output

    def find_field_csv_folder(self, csv_folder_path, field_info_path, path_to_save):
        outputList = []
        csv_folder_path=self.check_slash(csv_folder_path)
        path_to_save=self.check_slash(path_to_save)
        files_csv = glob.glob(csv_folder_path + '*.csv')
        # int로 바꿔서 sorting해주는 알고리즘도 해주면 좋을듯
        for file_csv in files_csv:
            csv_file_path = os.path.join(str(file_csv)).replace("\\", "/")
            field_data = self.find_field_csv_file(csv_file_path, field_info_path)
            name_file_csv = file_csv.replace('\\', '/,')
            outputList.append([name_file_csv, field_data])
            # 디렉토리가 없으면은 생성해준다.
            try:
                if not os.path.exists(path_to_save):
                    os.makedirs(path_to_save)
            except OSError:
                print('Error: Creating directory.' + path_to_save)

        with open(path_to_save + "fieldmatch.txt", "w+", encoding="utf-8") as f:
            f.write(
                'path of data file,file name,field number,field name,pointA(lon,lat),pointB(lon,lat),pointC(lon,lat),pointD(lon,lat)\n')
            lines = "\n".join(e[0] + ", " + str(e[1]) for e in outputList)
            f.writelines(lines)


if __name__ == "__main__":
    # 현재는 data/2.data_csv_format/폴더만 하는데 이것도 선택할 수 있게 인자로 처리할 수 있을 것 같고, 그경우마다 위에 시간체크하는거 달라질수 있을듯
    csv_dir_path = 'data/2. data_csv_format/'
    info_path = 'helper/output.csv'
    path_to_save = 'data/8. data_field_find/'
    name_of_dir = '수원'

    Find_field_csv()
    find_field = Find_field_csv()
    find_field.find_field_csv_folder(csv_dir_path + name_of_dir, info_path, path_to_save + name_of_dir)
