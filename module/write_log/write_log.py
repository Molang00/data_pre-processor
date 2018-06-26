#함수전반적으로 전달인자만 고치면된다.


import pandas as pd
import numpy as np
import os
import glob
import math

class Write_log:
    # gps좌표를 meter scale의 distance로 바꾸어준다
    def measure_position(self, lat1, lon1, lat2, lon2):
        R = 6378.137
        dLat = (lat1 - lat2) * math.pi / 180
        dLon = (lon1 - lon2) * math.pi / 180
        a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(lat1 * math.pi / 180) * math.cos(
            lat2 * math.pi / 180) * math.sin(dLon / 2) * math.sin(dLon / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d = R * c
        return d * 1000

    def checkPointInRectangle(self, pointP, pointA, pointB, pointC, pointD):
        b1 = False
        b2 = False

        if self.measure_position(pointP[0], pointP[1], pointA[0], pointA[1]) < 200:
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

    def check_in_field(self, longitude, latitude, parsedFieldFilePath):
        df = pd.read_csv(parsedFieldFilePath)
        infield=False
        for i in range(len(df)):
            # 경로,파일명,번호,구장이름,위도,경도
            lonA, latA, lonB, latB, lonC, latC, lonD, latD = df.values[i][4:]

            pointP = (longitude, latitude)
            pointA = (lonA, latA)
            pointB = (lonB, latB)
            pointC = (lonC, latC)
            pointD = (lonD, latD)

            if self.checkPointInRectangle(pointP, pointA, pointB, pointC, pointD):
                infield=True

        return infield

    # speed인자는 정보를 넘길때 잘 정해서 넘겨주면 되는 걸로 정하자.
    def check_activation(self,speed):
        statu = False
        if speed>3:#속도정보
            statu = True
        return statu

    def find_event(self,csv_files,time1,time2,fieldtext):
        df=pd.read_csv(fieldtext)
        for i in range(len(df)):
            lonA,latA,lonB,latB,lonC,latC,lonD,latD=df.values[i][4:]
            pointA = (lonA, latA)
            pointB = (lonB, latB)
            pointC = (lonC, latC)
            pointD = (lonD, latD)



        longitude,latitude=
        pointP = (longitude, latitude)


    # 선수교체여부를 판단하는 함수이다.
    # 그근처시간을 찾아서
    def notice_substitution(self,starters,benches,fieldtext):

        # fieldtext에서 점정보를 끌어와야한다.
        i=0
        player_in_game = self.check_in_field(starters[i],fieldtext)
        player_statu = self.check_activation(starters[i])

        player_in_game = self.check_in_field(benches[i],fieldtext)
        player_statu = self.check_activation(benches[i])

    # event1인 시간들 중에서 경기시간을 결정하는 함수이다.
    def assign_game_time(self,event1,event2):
        start_time=[]
        end_time=[]
        start = 0
        end = 0
        start_time=event1
        end_time=event2

        for i in start_time:
            for j in end_time:
                if start_time[i]-end_time[j]>45 and start_time[i]-end_time[j]<55:
                    start_time[i]=start
                    end_time[j]=end

        if start==0 and end ==0:
            print("searching error: no specific time!")
    # 다같이필드밖으로나가는시간찾기

    def check_csv_file(self, csv_file_path, field_info_path):
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
                # 이 사이에 판단하는 문장 넣어서 체크하자
                if field_data != []:
                    output = field_data
                    break
                i += 600  # 1분단위
        return output

    def find_field_csv_folder(self, csv_folder_path, field_info_path, path_to_save):
        outputList = []
        files_csv = glob.glob(csv_folder_path + '*.csv')

        for file_csv in files_csv:
            csv_file_path = os.path.join(str(file_csv)).replace("\\", "/")
            field_data = self.check_csv_file(csv_file_path, field_info_path)
            name_file_csv = file_csv.replace('\\', '/,')
            # 여기도 교체
            outputList.append([name_file_csv, field_data])

            # 디렉토리가 없으면은 생성해준다.
            try:
                if not os.path.exists(path_to_save):
                    os.makedirs(path_to_save)
            except OSError:
                print('Error: Creating directory.' + path_to_save)

        # 여기도 경로하고 내용바꿔서 적어줘야함
        with open(path_to_save + "log.csv", "w+", encoding="utf-8") as f:
            f.write('//event,time,player_out,player_in')
            # 이 아래 부분 write해주는 거 교체
            lines = "\n".join(e[0] + ", " + str(e[1]) for e in outputList)
            f.writelines(lines)

if __name__=="__main__":
    csv_dir_path = 'data/2. data_csv_format/'
    fieldtext='fieldtext.txt'
    name_of_dir='드래곤즈 0617/'

    Write_log()
    write_log=Write_log()