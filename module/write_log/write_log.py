import glob
import math
from collections import Counter

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
        values[0]=values[1]
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

    def check_activation(self,speed):
        statu=False
        if speed>3 and speed<40:#속도평균이 3이상이면 플레잉중
            statu=True
        return statu

    def detect_playing(self,path_csv_folder,path_field_info):
        players=[]
        path_csv_folder=self.check_slash(path_csv_folder)
        files_csv = glob.glob(path_csv_folder + '*.csv')
        files_csv.__delitem__(-1)
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
        left_hour = 24
        left_min = 60
        right_hour = 1
        right_min = 1
        for player in players:
            if left_hour>player[0][1] or (left_hour==player[0][1] and left_min>player[0][2]):
                left_hour = player[0][1]
                left_min = player[0][2]
            if right_hour<player[-1][1] or (right_hour==player[-1][1] and right_min < player[-1][2]):
                right_hour = player[-1][1]
                right_min = player[-1][2]
        #최소시간과 최대시간을 찾는다.
        time_table=[]
        while(left_hour<right_hour+1):
            time_table.append([left_hour,left_min,0])
            if left_hour==right_hour and left_min==right_min:
                break
            if not left_min ==59:
                left_min=left_min+1
            else:
                left_min=0
                left_hour=left_hour+1
        #찾은 후 time_table에 1분단위로 끊어서 최소시간과 최대시간을 저장한다.

        for player in players:
            i=0
            stamp=0
            while (i < len(player)):
                j=0
                while(player[i][1]!=time_table[j][0] or player[i][2] != time_table[j][1]):
                    if time_table[j][0]<player[i][1] or (time_table[j][0]==player[i][1] and time_table[j][1] < player[i][2]): #time table의 시간보다 더 큰 시간이 잡힌 경우
                        j=j+1
                    elif time_table[j][0]>player[i][1] or (time_table[j][0]==player[i][1] and time_table[j][1] > player[i][2]): #time table의 시간이 더 큰 시간이 잡힌 경우
                        i=i+1

                if player[i][3]==True:
                    time_table[j][2] = time_table[j][2]+1
                elif player[i][3]==False:
                    time_table[j][2] = time_table[j][2]
                else:
                    time_table[j][2] = time_table[j][2]
                stamp=stamp+1
                i = stamp

        # log.csv적는부분(초기화부분고쳐야함)
        # file_to_write=open(path_csv_folder+'log.csv','w')
        i=0
        k=0
        l=0
        p=0
        q=0
        timestp_fh=0
        timestp_break=0
        timestp_sh=0
        start1_hour=-1
        start1_minute=-1
        start2_hour=1
        start2_minute=-1
        end1_hour=-1
        end1_minute=-1
        end2_hour=-1
        end2_minute=-1

        while(i<len(time_table)): #start,end정하는 알고리즘
            num_playing_1=time_table[i][2]
            if i<len(time_table)-1:
                num_playing_2=time_table[i+1][2]
            else:
                num_playing_2 = time_table[i][2]

            if (num_playing_2 - num_playing_1)>8 and k==0: #활동중이아니다가 활동중인 시간체크 가장먼저->전반시작
                start1_hour= time_table[i+1][0]
                start1_minute=time_table[i+1][1]
                k=1
            if (num_playing_1 - num_playing_2)>8 and l==0 and timestp_fh>45:#활동중이다가 활동중이 아니게 되면서 시간이 45분이상지난경우->전반끝
                end1_hour=time_table[i+1][0]
                end1_minute=time_table[i+1][1]
                l=1

            if l==1 and p==0: #전반이 끝난 후에 후반시작 전까지 휴식시간 체크
                timestp_break=timestp_break+1

            if timestp_break>7 and (num_playing_2 - num_playing_1)>8 and p==0: #휴식이 끝난 후 활동이 시작하면 start2로 지정
                start2_hour = time_table[i + 1][0]
                start2_minute = time_table[i + 1][1]
                p=1

            if p==1 and (num_playing_1 - num_playing_2)>6 and (timestp_sh>45 and timestp_sh < 60) and q==0: #start2가 정해지고 나서 활동중이다가 활동중이 아니게 되면서 45분이상 흐르면 후반끝지정
                end2_hour = time_table[i][0]
                end2_minute = time_table[i][1]
                q=1

            if k==1: #전반시작시점이후부터 1분당 지나는 시간 체크
                timestp_fh=timestp_fh+1
            if p==1: #후반시작지점이후부터 1분당 지나는 시간 체크
                timestp_sh=timestp_sh+1

            i=i+1
        #교체선수 찾아보기 여기알고리즘부족함
        list_sub=[]
        sub=[]
        for player in players:
            i=0
            playing_num = 0
            playing_num1 = 0
            break_num = 0
            while(i<len(player)):

                if (player[i][1]>start1_hour or (player[i][1]==start1_hour and player[i][2]>start1_minute)) and(player[i][1]<end1_hour or (player[i][1]==end1_hour and player[i][2]<end1_minute)): #전반전 내의 시간대만 체크
                    if player[i][3]==True:
                        playing_num=playing_num+1
                    elif player[i][3]==False:
                        break_num=break_num+1


                if (player[i][1]>end1_hour or (player[i][1]==end1_hour and player[i][2]>end1_minute)) and(player[i][1]<start2_hour or (player[i][1]==start2_hour and player[i][2]<start2_minute)): # 휴식시간 체크
                    playing_num = playing_num
                    break_num = break_num

                if (player[i][1]>start2_hour or (player[i][1]==start2_hour and player[i][2]>start2_minute)) and(player[i][1]<end2_hour or (player[i][1]==end2_hour and player[i][2]<end2_minute)): #후반전 내의 시간대만 체크
                    if player[i][3]==True:
                        playing_num1=playing_num1+1
                    elif player[i][3] == False:
                        break_num = break_num + 1

                i=i+1
            sub.append([player[0][0], playing_num, break_num,playing_num1])
        #선수들의 활동 시간 체크
        revise=[]
        fh=[]
        sh=[]
        i = 0
        while i<len(sub):
            revise.append(sub[i][2])
            fh.append(sub[i][1])
            sh.append(sub[i][3])
            i=i+1
        cnt=Counter(revise)
        real_break=cnt.most_common(1)[0][0]
        fhtime=max(fh)
        shtime=max(sh)

        pout=[]
        pin=[]
        for s in sub:
            print(s)
            if s[2]>90:
                continue
            if (s[1]<5 and s[3]<5 and s[2]>80):
                continue
            #후반전에 교체in
            if s[1]<fhtime and s[2]>=shtime-real_break-5: #전반전시간보다 적게 뛰고 휴식이 후반전보다 많으면
                time=shtime-s[3]
                hh=end2_hour
                if end2_minute-time<0:
                    time=60-(time-end2_minute)
                    hh=end2_hour-1
                else:
                    time=end2_minute-time
                pin.append([s[0],hh,time])
            #후반전에 교체out
            if s[1]>=fhtime-real_break and s[3]<shtime and s[2]>real_break+3: #전반전을 다 소화하고서 후반전을 다 뛰지 않고 나간 선수
                time=shtime-s[3]
                hh=end2_hour
                if end2_minute-time<0:
                    time=60-(time-end2_minute)
                    hh=end2_hour-1
                else:
                    time=end2_minute-time
                pout.append([s[0],hh,time])

        for i in range(len(pout) - 1):
            for j in range(len(pout) - 1):
                if pout[j][1]*60+ pout[j][2]> pout[j + 1][1]*60+pout[j+1][2]:
                    temp = pout[j + 1]
                    pout[j + 1] = pout[j]
                    pout[j] = temp

        for i in range(len(pout) - 1):
            for j in range(len(pout) - 1):
                if pin[j][1]*60+ pin[j][2]< pin[j + 1][1]*60+pin[j+1][2]:
                    temp = pin[j + 1]
                    pin[j + 1] = pin[j]
                    pin[j] = temp

        #log.csv생성하는부분임
        file_to_write=open(path_csv_folder+'log.csv','w')
        file_to_write.write(write_order+'\n')

        file_to_write.write('START1,' + str(start1_hour) + ':' + str(start1_minute) + ':00' + '\n')
        # 교체
        file_to_write.write('END1,' + str(end1_hour) + ':' + str(end1_minute) + ':00' + '\n')
        # 교체
        file_to_write.write('START2,' + str(start2_hour) + ':' + str(start2_minute) + ':00' + '\n')
        i=0
        while(i<len(pout)):
            name=pout[i][0].replace('.csv','')
            name1=pin[i][0].replace('.csv','')
            file_to_write.write('SUB,' +str(pout[i][1])+ ':'+str(pout[i][2]-2) + ':00,'+name+','+name1 + '\n')
            i=i+1
        file_to_write.write('END2,' + str(end2_hour) + ':' + str(end2_minute) + ':00' + '\n')

        file_to_write.close()

if __name__ == "__main__":

    csv_path = 'data/3. data_csv_second_average/'
    field = 'data/2. data_csv_format/'
    name_of_dir='전북'

    Write_log()
    writeObject = Write_log()
    writeObject.detect_playing(csv_path+name_of_dir,field+name_of_dir+'/fieldmatch.txt')
