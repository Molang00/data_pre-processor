import os
import glob
import math
import re

class Write_log:

    def check_slash(self, path_string):
        # path_string 원하는 경로를 string으로 저장

        # path의 마지막 경로에 /혹은 \가 없다면 /를 추가하여 return
        if path_string[len(path_string) - 1] != '/' and path_string[len(path_string) - 1] != '\\':
            path_string = path_string + '/'
        return path_string

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
        file_read=open(parsedFieldFilePath,'r',encoding="utf-8")
        values = file_read.readlines()
        infield=False
        for i in range(len(values)):
            data=values[i].split(',')
            data[11]=data[11].replace("]",'0')
            # 경로,파일명,번호,구장이름,위도,경도
            lonA, latA, lonB, latB, lonC, latC, lonD, latD = data[4:]
            lonA, latA, lonB, latB, lonC, latC, lonD, latD =float(lonA),float(latA),float(lonB),float(latB),float(lonC),float(latC),float(lonD),float(latD)
            pointP = (longitude, latitude)
            pointA = (lonA, latA)
            pointB = (lonB, latB)
            pointC = (lonC, latC)
            pointD = (lonD, latD)

            if self.checkPointInRectangle(pointP, pointA, pointB, pointC, pointD):
                infield=True

        return infield

    def check_sub(self,check_sub,count,time_sub):
        check_point = False
        # 아직 덜 적은게 남으면
        if time_sub[count+1]>1:
            check_point=True
        else:#그게아니면은
            check_point = False
        return check_point

    def check_activation(self,speed):
        statu=False
        if speed>3 and speed<40:#속도평균이 5이상이면 플레잉중
            statu=True
        return statu

    def detect_playing(self,path_csv_folder,path_field_info):
        players=[]
        path_csv_folder=self.check_slash(path_csv_folder)
        files_csv = glob.glob(path_csv_folder + '*.csv')
        write_order = '//event,time,player_out,plater_in'
        i=0
        length=len(files_csv)
        while(i<length):
            files_csv[i]=files_csv[i].replace('\\','/')
            i=i+1

        for file_csv in files_csv:
            player = []
            filename=file_csv.replace(path_csv_folder,'')

            file_to_read=open(file_csv,'r')
            read_values = file_to_read.readlines()
            data = read_values[1].split(',')
            check_time_temp = data[3:5]
            check_time_temp[0] = int(check_time_temp[0])  # hour
            check_time_temp[1] = int(check_time_temp[1])  # minute
            value_temp = data[6:9]
            value_temp[0]=float(value_temp[0]) #longitude
            value_temp[1] = float(value_temp[1]) #latitude
            value_temp[2] = float(value_temp[2]) #speed
            longi=value_temp[0]
            lati=value_temp[1]
            count = 1
            for read_value in read_values[2:]:
                data = read_value.split(',')
                check_time = data[3:5]
                check_time[0] = int(check_time[0])  # hour
                check_time[1] = int(check_time[1])  # minute
                value = data[6:9]
                value[0] = float(value[0])  # longitude
                value[1] = float(value[1])  # latitude
                value[2] = float(value[2])  # speed

                if check_time==check_time_temp:
                    for i, v in enumerate(value):
                        value_temp[i] = value_temp[i] + v
                    count = count + 1
                else:
                    longi=float(value_temp[0])/count
                    lati=float(value_temp[1])/count
                    speed = float(value_temp[2])/count
                    playing = self.check_activation(speed)
                    infield = self.check_in_field(longi,lati,path_field_info)

                    if playing==True and infield==True:
                        check=True
                    else:
                        check=False
                    player.append([filename,check_time_temp[0],check_time_temp[1],check])
                    #매 분마다 활동중인지 여부를 검사한 후 이를 배열로저장
                    check_time_temp=check_time
                    value_temp=value
                    count=1
            players.append(player)
        # 이 위에까지 모든 csv파일을 읽어들여서 활동여부를 체크하는 형태로 저장

        # 그리고 여기서 sub시간찾아내야함
        for u,p in enumerate(players):
            hour = players[u][0]  # hour
            minute = players[u][1]  # minute
            stamp_playing = players[u][2]  # 활동여부

            if hour<min_hour and minute<min_minute:
                min_hour=int(hour)
                min_minute=int(minute)


        # log.csv적는부분(초기화부분고쳐야함)
        file_to_write=open(path_csv_folder+'log.csv','w')

        start1,end1,start2,end2=1
        count = 0
        player_in=[]
        player_out=[]
        time_sub=[]
        check_sub=[3]
        check_sub[0],check_sub[1],check_sub[2]=False


        file_to_write.write('START1,'+start1+'\n')
        while (check_sub[0]==True):
            file_to_write.write('SUB,'+time_sub[count]+','+player_out[count]+','+player_in[count]+'\n')
            check_sub[0]=self.check_sub(check_sub,count,time_sub)
        file_to_write.write('END1,' + end1)
        while (check_sub[0]==False and check_sub[1]==True):
            file_to_write.write('SUB,'+time_sub[count]+','+player_out[count]+','+player_in[count]+'\n')
            check_sub[1]=self.check_sub(check_sub,count,time_sub)
        file_to_write.write('START2,' + start2)
        while (check_sub[0]==False and check_sub[1]==False and check_sub[2]==True):
            file_to_write.write('SUB,'+time_sub[count]+','+player_out[count]+','+player_in[count]+'\n')
            check_sub[2]=self.check_sub(check_sub,count,time_sub)
        file_to_write.write('END2,' + end2)

        file_to_write.close()



csv_path = 'data/3. data_csv_second_average/'
field = 'data/2. data_csv_format/'
name_of_dir='드래곤즈 0617'

Write_log()
writeObject = Write_log()
writeObject.detect_playing(csv_path+name_of_dir,field+name_of_dir+'/fieldmatch.txt')



