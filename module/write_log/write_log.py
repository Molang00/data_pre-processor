# fieldmatch.txt도 읽어들인다면은 경기장 정보도 있으니 확인가능
# 만약에 그게 아니라면은 output.csv를 읽어들여야 한다.
# 지금 읽어야 하는 파일의 경로는 2.csv인 것 같다.
# log.csv파일은 2.csv의 경로안에다가 생성해주는 것으로 하자.
#활동 중인 사항을 판별하는 것->속도를 기준으로 잡자
# 활동중이 아니다가 활동시작하는점을 start2
# start1은 모여있다가 흩어지는거 기점으로 잡으면 될 것 같다.
# 리스트로 받아들이는데 시간을 초단위로 끊자
#time이 지금은 string형태인데 이걸 받아서 임의로 지정할 것인지 그냥 놔둘 것인지 결정한다.
# 파일을 읽기->경기시간 정하기->log작성 이 순서가 맞나..
# time_bar를 하나생성해주고 여기에 맞춰서 소팅하는걸 목표로 한다.

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

    # 속도를 체크해서 해당 시간대에 선수가 움직이고 있는지를 판단하는 것이다.
    def check_activation(self,csv_file):
        statu = False
        if csv_file[8]>3:#속도정보
            statu = True
        return statu

    # 선수가 경기장 안에 있는지 바깥에 있는지를 판단해주는 함수이다.(교체확인시 사용)
    def check_in_field(self,csv_file,fieldtext):
        check_point=False
        # 만약에 경기장 정보안에 들어 있다면
        check_point =True
        return check_point

    # event1은 시작시간의 판단 근거 중 하나가 된다.
    # event1의발생조건=>활동이없다가 활동이 있어야하고 활동 지속시간이 3분
    def find_event1(self,csv_files,times):
        # 이거체크할때 그 단위가 1분이고 분단위가 달라질때체크
        event1=[]
        i=0
        player_in_game = self.check_in_field(csv_files[0])
        player_statu = self.check_activation(csv_files[0])
        times=event1

    # event2는 경기마침시간의 판단 근거 중 하나가 된다.
    # event2의발생조건=>활동이있다가 활동이 없어야하고 지속시간이 3분
    def find_event2(self,csv_files,times):
        event2=[]
        i=0
        player_in_game = self.check_in_field(csv_files[0])
        player_statu = self.check_activation(csv_files[0])
        times=event2

    # 선수교체여부를 판단하는 함수이다.
    # 그근처시간을 찾아서
    def notice_substitution(self,starters,benches):
        i=0
        player_in_game = self.check_in_field(starters[i])
        player_statu = self.check_activation(starters[i])

        player_in_game = self.check_in_field(benches[i])
        player_statu = self.check_activation(benches[i])

    # event1인 시간들 중에서 경기시간을 결정하는 함수이다.
    def assign_game_time(self,event1,event2):
        start_time=[]
        end_time=[]


    # csv파일들의 정보를 읽어들여서 list형태로 저장한다.
    def read_csv_files(self,csv_folder_path,fieldtext):
        startingmember=[]
        benchmember=[]

        outputList = []
        files_csv = glob.glob(csv_folder_path + '*.csv')
