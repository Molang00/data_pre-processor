import glob
import math
import os


class Write_log:

    # expand_field함수에서 경기장 보정치만큼 필드크기를 늘려줌
    def expand_field(self, pointA, pointB, pointC, pointD, expansion_rate=1):

        def expansion(point, center, rate):
            x = center[0] + (point[0] - center[0]) * rate
            y = center[1] + (point[1] - center[1]) * rate
            return (x, y)

        center = (
            (pointA[0] + pointB[0] + pointC[0] + pointD[0]) / 4, (pointA[1] + pointB[1] + pointC[1] + pointD[1]) / 4)
        new_A = expansion(pointA, center, expansion_rate)
        new_B = expansion(pointB, center, expansion_rate)
        new_C = expansion(pointC, center, expansion_rate)
        new_D = expansion(pointD, center, expansion_rate)
        return new_A, new_B, new_C, new_D

    # check_slash에서 파일경로에 슬래쉬를 마지막에 삽입

    def check_slash(self, path_string):
        # path의 마지막 경로에 /혹은 \가 없다면 /를 추가하여 return
        if path_string[len(path_string) - 1] != '/' and path_string[len(path_string) - 1] != '\\':
            # path_string = os.path.join(path_string, '/')
            path_string=path_string+'/'
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

    # 점의 위치가 직사각형 안에 있으면True 아니면 False를 return

    def checkPointInRectangle(self, pointP, pointA, pointB, pointC, pointD):
        b1 = False
        b2 = False

        if self.measure_position(pointP[0], pointP[1], pointA[0], pointA[1]) < 200:
            b1 = self.checkPointInTriangle(pointP, pointA, pointB, pointC)
            b2 = self.checkPointInTriangle(pointP, pointC, pointD, pointA)

        insideSquare = (b1 or b2)
        return insideSquare

    # 점의 위치가 삼각형 안에있으면 True 아니면 False를 return

    def checkPointInTriangle(self, pointP, pointA, pointB, pointC):

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

    # 필드 정보를 읽어들여서 선수가 필드 안에있는지 바깥에 있는지 check해서 안에있으면 true, 바깥에 있으면 False
    def check_in_field(self, longitude, latitude, fieldmatch):
        file_read = open(fieldmatch, 'r', encoding="utf-8")
        values = file_read.readlines()
        values[0] = values[1]
        infield = False

        for i in range(len(values)):
            data = values[i].split(',')
            data[11] = data[11].replace("]", '0')
            # 경로,파일명,번호,구장이름,위도,경도
            lonA, latA, lonB, latB, lonC, latC, lonD, latD = data[4:]
            lonA, latA, lonB, latB, lonC, latC, lonD, latD = float(lonA), float(latA), float(lonB), float(latB), float(
                lonC), float(latC), float(lonD), float(latD)

            pointP = (longitude, latitude)
            pointA = (lonA, latA)
            pointB = (lonB, latB)
            pointC = (lonC, latC)
            pointD = (lonD, latD)

            # expandfield로 필드를 찾을 때 보정값을 넣은 후에
            pointA, pointB, pointC, pointD = self.expand_field(pointA, pointB, pointC, pointD, 1.0)
            # 만약 직사각형 필드 안에 선수가 있으면 True를 반환
            if self.checkPointInRectangle(pointP, pointA, pointB, pointC, pointD):
                infield = True
        return infield

    # 선수의 속도값을 읽어들여서 3~40사이의 속도를 가지면 활동중이라고 판단함
    def check_activation(self, speed):
        statu = False
        if speed > 3 and speed < 40:  # 속도평균이 3이상이면 플레잉중
            statu = True
        return statu

    # 교체선수 명단 리스트를 시간순서에 맞게 배열해주는 함수
    def sort_sub(self, p):
        # 먼저 버블소팅으로 시간순서에 맞게 이른 시간부터 나중시간 순으로 정렬해준다.

        for i in range(len(p) - 1):
            for j in range(len(p) - 1):
                if p[j][1] * 60 + p[j][2] > p[j + 1][1] * 60 + p[j + 1][2]:
                    temp = p[j + 1]
                    p[j + 1] = p[j]
                    p[j] = temp
        i = 0
        # 그리고 나서 만약 교체 리스트에 같은 등번호의 선수가 존재하면 가장 뒷 시간대만 남기고 삭제(이게 해보니까 가장 정확함.)
        while i < len(p) - 1:
            if p[i][0] == p[i + 1][0]:
                p.remove(p[i])
            i = i + 1
        return p

    def read_csv_files(self, players, files_csv, path_csv_folder, path_field_info):
        # csvfolder에 있는 csvfile들을 읽어들여서 활동 여부를 판단해주는 리스트를 만든다.
        path_csv_folder=path_csv_folder[:len(path_csv_folder)-1]+'\\'
        for file_csv in files_csv:
            player = []
            filename = file_csv.replace(path_csv_folder,'')
            file_to_read = open(file_csv, 'r')
            read_values = file_to_read.readlines()
            data = read_values[1].split(',')
            check_time_temp = data[3:5]
            check_time_temp[0] = int(check_time_temp[0])  # hour
            check_time_temp[1] = int(check_time_temp[1])  # minute
            value_temp = data[6:9]
            value_temp[0] = float(value_temp[0])  # longitude
            value_temp[1] = float(value_temp[1])  # latitude
            value_temp[2] = float(value_temp[2])  # speed
            longi = value_temp[0]
            lati = value_temp[1]
            count = 1
            for read_value in read_values[2:]:
                data = read_value.split(',')  # csv형식의 파일을 ','단위로 parsing한 자료를 가진다.
                check_time = data[3:5]
                check_time[0] = int(check_time[0])  # hour
                check_time[1] = int(check_time[1])  # minute
                value = data[6:9]
                value[0] = float(value[0])  # longitude
                value[1] = float(value[1])  # latitude
                value[2] = float(value[2])  # speed

                if check_time == check_time_temp:  # 분단위가 같으면 계속 longi,lati,speed값을 더해나가고
                    for i, v in enumerate(value):
                        value_temp[i] = value_temp[i] + v
                    count = count + 1
                else:  # 만약 분단위가 달라지게 될 경우, 1분간 모은 자료에 대한 평균치의 위치와 속도로 활동여부를 판단해준다.
                    longi = float(value_temp[0]) / count
                    lati = float(value_temp[1]) / count
                    speed = float(value_temp[2]) / count
                    playing = self.check_activation(speed)
                    infield = self.check_in_field(longi, lati, path_field_info)
                    # 만약 속도와 위치 모두가 활동성이 있다고 확인되면 True고 아니면 False이다.
                    if playing == True and infield == True:
                        check = True
                    else:
                        check = False
                    player.append([filename, check_time_temp[0], check_time_temp[1], check])
                    # 매 분마다 활동중인지 여부를 검사한 후 이를 배열로저장
                    check_time_temp = check_time
                    value_temp = value
                    count = 1
            players.append(player) #이렇게 읽어드린csv파일들을 player라는 형태의 list로 players에 저장
        return players

    def find_time_table(self, time_table, players):
        # 초기화해준다. (left time은 모든 파일들 중 가장 먼저 시작되는 시간이고 right time은 가장 나중에 끝나는 시간임)
        left_hour, left_min, right_hour, right_min = 24, 60, 1, 1 #left time과 right time변수의 초기화
        for player in players:
            if left_hour > player[0][1] or (left_hour == player[0][1] and left_min > player[0][2]):
                #만약 읽어드린 파일의 가장 첫번째 시간대가 left time보다 이를 경우 lefttime으로 지정
                left_hour = player[0][1]
                left_min = player[0][2]
            if right_hour < player[-1][1] or (right_hour == player[-1][1] and right_min < player[-1][2]):
                #만약 읽어드린 파일의 가장 마지막 시간대가 right time보다 추후일 경우 righttime으로 지정
                right_hour = player[-1][1]
                right_min = player[-1][2]
        # 최소시간과 최대시간을 찾는다.
        while (left_hour < right_hour + 1):
            # 찾아낸 최소시간부터 최대시간까지 1분단위로 time_table을 append해서 활동중인 player갯수를 담을 공간을 확보한다.
            time_table.append([left_hour, left_min, 0])
            if left_hour == right_hour and left_min == right_min:
                break
            if not left_min == 59:#append할시 분단위가60이 넘어가게 될 경우 시간이 오르게설정
                left_min = left_min + 1
            else:
                left_min = 0
                left_hour = left_hour + 1
            #23시59분이후 시간을 0 0으로해주는 것을 구현안했으니 만약에 그 문제가 생기면은 여기를 보도록하자.
        return time_table

    def check_number_playing_in_time_table(self, time_table, players):
        # time_table의 있는 시간대로 찾아가서 만약 해당 시간대에서 플레이어가 활동중이면 활동중인 횟수를+1해준다.
        for player in players:
            i = 0
            stamp = 0 #stamp는 활동중인 선수의 수를 세어주는 변수이다.
            while (i < len(player)):
                j = 0
                #밑의 반복문으로 timetable에 적힌 시간대에서의 player의 원소로 찾아가서 활동성을 체크한다.
                while (player[i][1] != time_table[j][0] or player[i][2] != time_table[j][1]):
                    if time_table[j][0] < player[i][1] or (
                            time_table[j][0] == player[i][1] and time_table[j][1] < player[i][
                        2]):  # time table의 시간보다 더 큰 시간이 잡힌 경우
                        j = j + 1
                    elif time_table[j][0] > player[i][1] or (
                            time_table[j][0] == player[i][1] and time_table[j][1] > player[i][
                        2]):  # time table의 시간이 더 큰 시간이 잡힌 경우
                        i = i + 1
                #선수가 활동중이면은 1을 더해준다.
                if player[i][3] == True:
                    time_table[j][2] = time_table[j][2] + 1
                elif player[i][3] == False:
                    time_table[j][2] = time_table[j][2]
                else:
                    time_table[j][2] = time_table[j][2]
                stamp = stamp + 1
                #i를 stamp로 초기화해줌으로 한번 검사한 항은 건너뛰고 반복문을 돌게함으로 시간을 절약해줌
                i = stamp
        return time_table

    def detect_start_end_time(self, time_table, time_list):
        i, k, l, p, q = 0, 0, 0, 0, 0
        timestp_fh, timestp_break, timestp_sh = 0, 0, 0
        start1_hour, start1_minute, start2_hour, start2_minute = -1, -1, -1, -1
        end1_hour, end1_minute, end2_hour, end2_minute = -1, -1, -1, -1
        while (i < len(time_table) - 2):  # start,end정하는 알고리즘
            num_playing_1 = time_table[i][2]
            if i < len(time_table) - 1:
                num_playing_2 = time_table[i + 1][2]
            else:
                num_playing_2 = time_table[i][2]

            if (num_playing_2 - num_playing_1) > 6 and k == 0 and time_table[i + 1][2] > 6 and time_table[i + 2][
                2] > 6:  # 활동중이아니다가 활동중인 시간체크 가장먼저->전반시작
                start1_hour = time_table[i + 1][0]
                start1_minute = time_table[i + 1][1]
                k = 1
            if (num_playing_1 - num_playing_2) < 3 and l == 0 and timestp_fh > 45 and time_table[i + 1][2] < 9 and \
                    time_table[i + 2][2] < 9:  # 활동중이다가 활동중이 아니게 되면서 시간이 45분이상지난경우->전반끝
                end1_hour = time_table[i - 1][0]
                end1_minute = time_table[i - 1][1]
                l = 1

            if l == 1 and p == 0:  # 전반이 끝난 후에 후반시작 전까지 휴식시간 체크
                timestp_break = timestp_break + 1

            if timestp_break > 5 and (num_playing_2 - num_playing_1) > 6 and p == 0 and time_table[i + 1][2] > 6 and \
                    time_table[i + 2][2] > 6:  # 휴식이 끝난 후 활동이 시작하면 start2로 지정
                start2_hour = time_table[i + 1][0]
                start2_minute = time_table[i + 1][1]
                p = 1

            if p == 1 and (num_playing_1 - num_playing_2) < 3 and (timestp_sh > 45 and timestp_sh < 60) and q == 0 and \
                    time_table[i + 1][2] < 9 and time_table[i + 2][
                2] < 9:  # start2가 정해지고 나서 활동중이다가 활동중이 아니게 되면서 45분이상 흐르면 후반끝지정
                end2_hour = time_table[i - 1][0]
                end2_minute = time_table[i - 1][1]
                q = 1

            if k == 1:  # 전반시작시점이후부터 1분당 지나는 시간 체크
                timestp_fh = timestp_fh + 1
            if p == 1:  # 후반시작지점이후부터 1분당 지나는 시간 체크
                timestp_sh = timestp_sh + 1
            i = i + 1
        #정해진 시간들을 timelist에 append한 다음에 return해준다.
        time_list.append(start1_hour)
        time_list.append(start1_minute)
        time_list.append(end1_hour)
        time_list.append(end1_minute)
        time_list.append(start2_hour)
        time_list.append(start2_minute)
        time_list.append(end2_hour)
        time_list.append(end2_minute)

        return time_list
    #교체선수의 교체시간을 찾아낸다.
    def find_sub_list(self, players, sub_list, time_list):
        pout_fh = []
        pin_fh = []
        pout_sh = []
        pin_sh = []
        pout_h = []
        pin_h = []
        start1_hour, start1_minute,end1_hour, end1_minute =  time_list[0], time_list[1], time_list[2], time_list[3]
        start2_hour,start2_minute,end2_hour, end2_minute = time_list[4], time_list[5], time_list[6], time_list[7]
        sub_list[0], sub_list[1], sub_list[2] = pout_fh, pin_fh, pout_h
        sub_list[3], sub_list[4], sub_list[5] = pin_h, pout_sh, pin_sh
        #sublist들에 담길 필요한 정보들과 리스트 초기화해줌

        for p in players:
            i = 0
            out_checker = 0
            while (i < len(p) - 10):
                #해당시간대의 앞뒤의 true false갯수를 세기 위한 변수 초기화
                stamp_true_fh, stamp_false_fh, stamp_true_sh, stamp_false_sh = 0, 0, 0, 0
                j = i - 10
                while j < i:
                    if p[j][3] == True:
                        stamp_true_fh = stamp_true_fh + 1
                    elif p[j][3] == False:
                        stamp_false_fh = stamp_false_fh + 1
                    j = j + 1
                    #_fh가 붙은 애들이 해당시간 앞의 트루 폴스 갯수를 센다.
                while j < i + 10:
                    if p[j][3] == True:
                        stamp_true_sh = stamp_true_sh + 1
                    elif p[j][3] == False:
                        stamp_false_sh = stamp_false_sh + 1
                    j = j + 1
                    #_sh가 붙은 애들이 해당시간 뒤의 트로 폴스 갯수를 센다.

                out_ap = stamp_true_fh - stamp_false_fh #해당시간 앞 10개에 대한 true-false
                out_dui = stamp_false_sh - stamp_true_sh #해당시간 뒤 10개에 대한 false-true
                in_ap = stamp_false_fh - stamp_true_fh#해당시간 앞 10개에 대한 false-true
                in_dui = stamp_true_sh - stamp_false_sh#해당시간 뒤 10개에 대한 true-false

                if i == len(p) - 11:  # 반복문마지막에 다다랐을때 후반종료가 아니면 교체out으로 잡아주어야 한다.
                    if p[i + 10][1] < end2_hour or (
                            p[i + 10][1] == end2_hour and p[i + 10][2] < end2_minute):  # 끝나는 시간보다 더 일찍 기계가 꺼진경우(교체된경우)
                        out_checker = 1

                if (p[i][1] > start1_hour or (p[i][1] == start1_hour and p[i][2] > start1_minute)) and (p[i][1] < end1_hour or (p[i][1] == end1_hour and p[i][2] < end1_minute)):  # 전반전동안에
                    if p[i + 8][1] > end1_hour or (p[i + 8][1] == end1_hour and p[i + 8][2] > end1_minute) and out_checker == 0:  # 전반전 끝에 걸릴즘 즉 단체로 쉬러가는거는 교체아웃안잡는다
                        i = i + 1
                        continue
                    if (p[i - 1][3] == True and p[i][3] == False and out_ap > 3 and out_dui > 3) or out_checker == 1:  # 전반전 교체out찾기
                        pout_fh.append([p[i][0].replace('.csv', ''), p[i][1], p[i][2]])
                    if p[i - 1][3] == False and p[i][3] == True and in_ap > 3 and in_dui > 3:  # 전반전 교체in찾기
                        pin_fh.append([p[i][0].replace('.csv', ''), p[i][1], p[i][2]])
                if ((p[i][1] > end1_hour or (p[i][1] == end1_hour and p[i][2] > end1_minute)) and (p[i][1] < start2_hour or (p[i][1] == start2_hour and p[i][2] < start2_minute))):  # 하프타임동안에
                    if p[i + 8][1] > end1_hour or (p[i + 8][1] == end1_hour and p[i + 8][2] > end1_minute):  # 전반전 끝에 걸릴즘 즉 단체로 쉬러가는거는 교체아웃안잡는다
                        i = i + 1
                        continue
                    if p[i - 8][1] < start2_hour or (p[i - 8][1] == start2_hour and p[i - 8][2] < start2_minute) and out_checker == 0:  # 후반전 맨 앞에 걸릴즘 즉 단체로 쉬러가는거는 교체아웃안잡는다
                        i = i + 1
                        continue
                    # 하프타임교체잡는 알고리즘 다시 생각해보자->전반에뛰다가 후반에는 안뛰는 그런걸로 찾아줘야 할 것 같다.
                    if (p[i - 1][3] == True and p[i][
                        3] == False and out_ap > 3 and out_dui > 3) or out_checker == 1:  # 하프타임 교체out찾기
                        pout_h.append([p[i][0].replace('.csv', ''), p[i][1], p[i][2]])
                    if p[i - 1][3] == False and p[i][3] == True and in_ap > 3 and in_dui > 3:  # 하프타임 교체in찾기
                        pin_h.append([p[i][0].replace('.csv', ''), p[i][1], p[i][2]])
                if (p[i][1] > start2_hour or (p[i][1] == start2_hour and p[i][2] > start2_minute)) and (
                        p[i][1] < end2_hour or (p[i][1] == end2_hour and p[i][2] < end2_minute)):  # 후반전동안에
                    if p[i - 8][1] < start2_hour or (p[i - 8][1] == start2_hour and p[i - 8][
                        2] < start2_minute) and out_checker == 0:  # 후반전 맨 앞에 걸릴즘 즉 단체로 쉬러가는거는 교체아웃안잡는다
                        i = i + 1
                        continue
                    if (p[i - 1][3] == True and p[i][
                        3] == False and out_ap > 3 and out_dui > 3) or out_checker == 1:  # 후반전 교체out찾기
                        pout_sh.append([p[i][0].replace('.csv', ''), p[i][1], p[i][2]])
                    if p[i - 1][3] == False and p[i][3] == True and in_ap > 3 and in_dui > 3:  # 후반전 교체in찾기
                        pin_sh.append([p[i][0].replace('.csv', ''), p[i][1], p[i][2]])
                i = i + 1

        pout_fh = self.sort_sub(pout_fh)
        pin_fh = self.sort_sub(pin_fh)
        pout_h = self.sort_sub(pout_h)
        pin_h = self.sort_sub(pin_h)
        pout_sh = self.sort_sub(pout_sh)
        pin_sh = self.sort_sub(pin_sh)
        print(pout_fh)
        if (len(pout_sh) + len(pout_fh) + len(pout_h)) != (len(pin_fh) + len(pin_h) + len(pin_sh)):
            pout_fh, pin_fh = self.check_none_sub(pout_fh, pin_fh)
            pout_h, pin_h = self.check_none_sub(pout_h, pin_h)
            pout_sh, pin_sh = self.check_none_sub(pout_sh, pin_sh)

        return sub_list
    #교체선수의 시간정보와 등번호 정보를 담은 리스트들을 인자로 전달받음
    def check_none_sub(self, pout, pin):

        if len(pout) > len(pin):  # 교체 나가는 선수가 더 많이 잡혔을경우
            i = 0
            while (i < len(pout)):
                j = 0
                while (j < len(pin)):
                    if abs((pout[i][1] * 60 + pout[i][2]) - (
                            pin[j][1] * 60 + pin[j][2])) < 4:  # 같은시간대로 판단이 되는 시간이 있으면은그냥넘어간다.
                        break
                    elif abs((pout[i][1] * 60 + pout[i][2]) - (
                            pin[j][1] * 60 + pin[j][2])) > 3:  # 만약에 같은시간대로 판단이 안되는 경우에는 계속비교
                        j = j + 1
                        if j == len(pin):
                            pin.append(['', pout[i][1], pout[i][2]])
                            pin = self.sort_sub(pin)
                i = i + 1

        elif len(pout) < len(pin):  # 교체들어오는선수가 더 많이 잡혔을 경우
            i = 0
            while (i < len(pin)):
                j = 0
                while (j < len(pout)):
                    if abs((pin[i][1] * 60 + pin[i][2]) - (pout[j][1] * 60 + pout[j][2])) < 4:
                        break
                    elif abs((pin[i][1] * 60 + pin[i][2]) - (pout[j][1] * 60 + pout[j][2])) > 3:
                        j = j + 1
                        if j == len(pout):
                            pout.append(['', pin[i][1], pin[i][2]])
                            pout = self.sort_sub(pout)
                i = i + 1
        return pout, pin
    #log를 써주는 함수
    def write_log_file(self, sub_list, path_to_save, time_list):
        write_order = '//event,time,player_out,player_in'
        start1_hour, start1_minute, end1_hour, end1_minute = time_list[0], time_list[1], time_list[2], time_list[3]
        start2_hour, start2_minute, end2_hour, end2_minute = time_list[4], time_list[5], time_list[6], time_list[7]
        pout_fh, pin_fh, pout_h = sub_list[0], sub_list[1], sub_list[2]
        pin_h, pout_sh, pin_sh = sub_list[3], sub_list[4], sub_list[5]

        # 디렉토리가 없으면은 생성해준다.
        try:
            if not os.path.exists(path_to_save):
                os.makedirs(path_to_save)
        except OSError:
            print('Error: Creating directory.' + path_to_save)

        file_to_write = open(path_to_save + 'log.csv', 'w')
        file_to_write.write(write_order + '\n')
        file_to_write.write('START1,' + str(start1_hour).zfill(2) + ':' + str(start1_minute).zfill(2) + ':00' + '\n')
        i = 0
        while i < len(pout_fh):
            file_to_write.write(
                'SUB,' + str(pin_fh[i][1]).zfill(2) + ':' + str(pin_fh[i][2]).zfill(2) + ':00,' + pout_fh[i][0] + ',' +
                pin_fh[i][0] + '\n')
            i = i + 1
        file_to_write.write('END1,' + str(end1_hour).zfill(2) + ':' + str(end1_minute).zfill(2) + ':00' + '\n')
        i = 0
        while i < len(pout_h):
            file_to_write.write(
                'SUB,' + str(pin_h[i][1]).zfill(2) + ':' + str(pin_h[i][2]).zfill(2) + ':00,' + pout_h[i][0] + ',' +
                pin_h[i][0] + '\n')
            i = i + 1
        file_to_write.write('START2,' + str(start2_hour).zfill(2) + ':' + str(start2_minute).zfill(2) + ':00' + '\n')
        i = 0
        while i < len(pout_sh):
            file_to_write.write(
                'SUB,' + str(pin_sh[i][1]).zfill(2) + ':' + str(pin_sh[i][2]).zfill(2) + ':00,' + pout_sh[i][0] + ',' +
                pin_sh[i][0] + '\n')
            i = i + 1
        file_to_write.write('END2,' + str(end2_hour).zfill(2) + ':' + str(end2_minute).zfill(2) + ':00' + '\n')

        file_to_write.close()
    #모든 메소드들을 콜해주는 함수
    def detect_playing(self, path_csv_folder, path_field_info, name, path_to_save):
        players = []
        time_table = []
        time_list = []
        sub_list = []
        p=[]
        i=0
        while i<6:
            sub_list.append(p)
            i=i+1
        #필요한 리스트들을 선언하고 초기화해준다.
        # 파일과 폴더 경로이름을 지정해주는 부분
        path_csv_folder = path_csv_folder+name
        path_field_info = path_field_info+name+ '/fieldmatch.txt'
        path_csv_folder = self.check_slash(path_csv_folder)
        files_csv = glob.glob(path_csv_folder + '*.csv')
        path_to_save = path_to_save + name
        path_to_save = self.check_slash(path_to_save)
        for f in files_csv:
            f = f.replace('\\', '/')

        players = self.read_csv_files(players, files_csv, path_csv_folder, path_field_info)
        time_table = self.find_time_table(time_table, players)
        time_table = self.check_number_playing_in_time_table(time_table, players)
        time_list = self.detect_start_end_time(time_table, time_list)
        sub_list = self.find_sub_list(players, sub_list, time_list)
        self.write_log_file(sub_list, path_to_save, time_list)

if __name__ == "__main__":
    csv_path = 'data/3. data_csv_second_average/'
    field = 'data/8. data_field_find/'
    path_to_save = 'data/9. data_log_csv/'
    name_of_dir = '드래곤즈'

    Write_log()
    writeObject = Write_log()
    writeObject.detect_playing(csv_path, field, name_of_dir, path_to_save)
