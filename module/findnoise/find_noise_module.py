import math
import glob
import numpy
from helper import common_os_helper
from helper.find_field_csv import Find_field_csv

class NoiseFinder:

    def str_to_time(self, time_str_csv):
        time_str = time_str_csv[0]
        for time_csv_string in time_str_csv[1:6]:
            time_str = time_str + '.' + time_csv_string
        return time_str

    def time_to_second(self, time_str):
        time_list = time_str.split('.')
        second = int(time_list[3])*3600+int(time_list[4])*60+int(time_list[5])
        return second

    def check_gps_error(self, read_values_list, max_time, min_time):
        player_num = len(read_values_list)
        time_term = max_time-min_time+1
        time_table = numpy.zeros((player_num, time_term), float)
        player_dist_sum = numpy.zeros(time_term, float)

        for player_id in range(player_num):
            for read_value in read_values_list[player_id]:
                value_csv_list = read_value.split(',')
                time_id = self.time_to_second(self.str_to_time(value_csv_list[:6]))

                time_table[player_id][time_id-min_time] = float(value_csv_list[9])
                player_dist_sum[time_id-min_time] = player_dist_sum[time_id-min_time]+float(value_csv_list[9])

        state_list = [0]*player_num
        for time_id in range(time_term):
            count = numpy.zeros(player_num, float)
            for player_a in range(player_num):
                dist_a = time_table[player_a][time_id]
                for player_b in range(player_a, player_num):
                    dist_b = time_table[player_b][time_id]

                    if max(dist_a, dist_b) - min(dist_a, dist_b) < 20:
                        count[player_a] = count[player_a]+1
                        count[player_b] = count[player_b]+1

                if count[player_a] < player_num*0.7:
                    state_list[player_a] = state_list[player_a]+1

        return state_list

    def find_noise_in_data(self, path_read_folder, path_read_field_folder, path_write_folder, name_of_dir):
        # path_read_folder 읽을 파일이 저장된 path를 string으로 저장
        # path_write_folder 파일을 쓰고자 하는 path를 string으로 저장
        # nmae_of_dir 읽을 파일과 쓰고자 하는 파일의 dir name을 string으로 저장

        path_read_folder = common_os_helper.check_slash(path_read_folder)
        path_read_field_folder = common_os_helper.check_slash(path_read_field_folder)
        path_write_folder = common_os_helper.check_slash(path_write_folder)
        name_of_dir = common_os_helper.check_slash(name_of_dir)
        path_read_folder = path_read_folder+name_of_dir
        path_read_field_folder = path_read_field_folder+name_of_dir
        path_write_folder = path_write_folder+name_of_dir

        file_to_read_field = open(path_read_field_folder+'fieldmatch.txt', 'r', encoding="utf-8")
        read_field = file_to_read_field.readline()

        common_os_helper.create_dir(path_write_folder)
        file_to_write = open(path_write_folder+'error.csv', 'w')
        write_order = 'path,filename,start_time,end_time,error_code\n'
        file_to_write.write(write_order)

        read_values_list = []
        read_files_name = []
        min_time = math.inf
        max_time = 0
        files_read = glob.glob(path_read_folder+'*.csv')
        for file_read in files_read:
            file_read = file_read.replace('\\','/')
            file_to_read = open(file_read, 'r')

            read_values = file_to_read.readlines()
            read_values_list.append(read_values[1:])

            error_list = []
            last_speed = 0
            id_speed = -1
            last_dist = 0
            id_dist = -1
            last_field = 0
            id_field = -1
            ck_field = 1
            try:
                read_field = file_to_read_field.readline()
                read_field_list = read_field.split(',')
                lonA, latA, lonB, latB, lonC, latC, lonD, latD = read_field_list[4:]
                pointA = (float(lonA[1:]), float(latA[1:]))
                pointB = (float(lonB[1:]), float(latB[1:]))
                pointC = (float(lonC[1:]), float(latC[1:]))
                pointD = (float(lonD[1:]), float(latD[1:len(latD)-2]))
                find_object = Find_field_csv()
                pointA, pointB, pointC, pointD = find_object.expand_field(pointA, pointB, pointC, pointD, 1.2)
            except:
                ck_field = 0

            value_csv_list = read_values[1].split(',')
            time_str = self.str_to_time(value_csv_list[:6])
            if self.time_to_second(time_str) < min_time:
                min_time = self.time_to_second(time_str)

            for value_list in read_values[1:]:
                value_csv_list = value_list.split(',')

                time_str = self.str_to_time(value_csv_list[:6])

                if self.time_to_second(time_str) < min_time:
                    min_time = self.time_to_second(time_str)

                speed_float = float(value_csv_list[8])
                # speed가 35보다 크게 변경된 순간에는 순간에는 list 형태로 start_time append
                # speed가 35보다 작게 변경된 순간에는 start_time을 append한 위치에 end_time과 error_code 작성
                if speed_float >= 35.0 and value_list != read_values[len(read_values)-1]:
                    if last_speed == 0:
                        last_speed = 1
                        error_list.append(time_str)
                        id_speed = len(error_list)-1
                else:
                    if last_speed == 1:
                        last_speed = 0
                        error_list[id_speed] = error_list[id_speed] + ',' + time_str + ',OverSpeed'

                dist_float = float(value_csv_list[9])
                # 1초에 이동한 dist가 15m보다 크게 변경된 순간에는 list 형태로 start_time append
                # 1초에 이동한 dist가 15m보다 작게 변경된 순간에는 start_time을 append한 위치에 end_time과 error_code 작성
                if dist_float >= 15 and value_list != read_values[len(read_values)-1]:
                    if last_dist == 0:
                        last_dist = 1
                        error_list.append(time_str)
                        id_dist = len(error_list)-1
                else:
                    if last_dist == 1:
                        last_dist = 0
                        error_list[id_dist] = error_list[id_dist] + ',' + time_str + ',OverDist'

                # field의 1.2배 크기 밖으로 나간 순간에는 list 형태로 start_time append
                # field의 1.2배 크기 안으로 들어간 순간에는 start_time을 append한 위치에 end_time과 error_code 작성
                longitude_float = float(value_csv_list[6])
                latitude_float = float(value_csv_list[7])
                pointP = (longitude_float, latitude_float)

                if (ck_field and find_object.checkPointInRectangle(pointP, pointA, pointB, pointC, pointD)) \
                        and value_list != read_values[len(read_values) - 1]:
                    if last_field == 0:
                        last_field = 1
                        error_list.append(time_str)
                        id_field = len(error_list)-1
                else:
                    if last_field == 1:
                        last_field = 0
                        error_list[id_field] = error_list[id_field] + ',' + time_str + ',OutOfField'

            if self.time_to_second(time_str) > max_time:
                max_time = self.time_to_second(time_str)

            file_list = file_read.split('/')
            file_name = file_list[len(file_list)-1]
            read_files_name.append(file_name[:len(file_name)-4])

            # file에서 읽어온 정보를 이용해 speed_error를 찾고 error.csv에 쓰기
            for error_str in error_list:
                file_to_write.write(path_read_folder+','+file_name+','+error_str+'\n')
            file_to_read.close()

        file_to_read_field.close()
        file_to_write.close()


        file_to_write_info = open(path_write_folder+'notice_device_info.txt', 'w', encoding="utf-8")
        write_order_info = 'player,state\n'
        file_to_write_info.write(write_order_info)

        state_list = self.check_gps_error(read_values_list, max_time, min_time)
        for id in range(len(read_files_name)):
            if state_list[id] == 0:
                state = ', Normal\n'
            elif state_list[id] <= 3:
                state = ', Doubt\n'
            else:
                state = ', Abnormal\n'
            file_to_write_info.write(read_files_name[id]+state)
        file_to_write_info.close()
