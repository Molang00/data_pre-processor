import math
import glob
import os
import time


class NoiseFinder:

    def create_dir(self, directory):
        # directory dir명이 포함된 path가 string으로 저장
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except OSError:
            print('Error: Creating directory. '+directory)

    def check_slash(self, path_string):
        # path_string 원하는 경로를 string으로 저장

        # path의 마지막 경로에 /혹은 \가 없다면 /를 추가하여 return
        if path_string[len(path_string)-1] != '/' and path_string[len(path_string)-1] != '\\':
            path_string = path_string+'/'
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
            updown = (pointP[1] - pointB[1]) * (pointA[0] - pointB[0]) - (
                    pointP[0] - pointB[0]) * (pointA[1] - pointB[1])
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

    def expand_field(self, pointA, pointB, pointC, pointD, expansion_rate):

        def expansion(point, center, rate):
            x = center[0] + (point[0]-center[0])*rate
            y = center[1] + (point[1]-center[1])*rate
            return (x, y)
        center = ((pointA[0]+pointB[0]+pointC[0]+pointD[0])/4,(pointA[1]+pointB[1]+pointC[1]+pointD[1])/4)
        new_A = expansion(pointA, center, expansion_rate)
        new_B = expansion(pointB, center, expansion_rate)
        new_C = expansion(pointC, center, expansion_rate)
        new_D = expansion(pointD, center, expansion_rate)
        return new_A, new_B, new_C, new_D

    def time_to_second(self, time_str):
        time_list = time_str.split('.')
        second = int(time_list[3])*3600+int(time_list[4])*60+int(time_list[5])
        return second

    def find_noise_in_data(self, path_read_folder, path_read_field_folder, path_write_folder, name_of_dir):
        # path_read_folder 읽을 파일이 저장된 path를 string으로 저장
        # path_write_folder 파일을 쓰고자 하는 path를 string으로 저장
        # nmae_of_dir 읽을 파일과 쓰고자 하는 파일의 dir name을 string으로 저장

        path_read_folder = self.check_slash(path_read_folder)
        path_read_field_folder = self.check_slash(path_read_field_folder)
        path_write_folder = self.check_slash(path_write_folder)
        name_of_dir = self.check_slash(name_of_dir)
        path_read_folder = path_read_folder+name_of_dir
        path_read_field_folder = path_read_field_folder+name_of_dir
        path_write_folder = path_write_folder+name_of_dir

        file_to_read_field = open(path_read_field_folder+'fieldmatch.txt', 'r', encoding="utf-8")
        read_field = file_to_read_field.readline()

        self.create_dir(path_write_folder)
        file_to_write = open(path_write_folder+'error.csv', 'w')
        write_order = 'path,filename,start_time,end_time,error_code\n'
        file_to_write.write(write_order)

        file_to_write_info = open(path_write_folder+'notice_device_info.txt', 'w', encoding="utf-8")
        write_order_info = 'player,state\n'
        file_to_write_info.write(write_order_info)
        info_lists = []
        sum_slow_time = 0.0

        files_read = glob.glob(path_read_folder+'*.csv')
        for file_read in files_read:
            file_read = file_read.replace('\\','/')
            file_to_read = open(file_read, 'r')

            read_values = file_to_read.readlines()

            start_time_file = 'Empty'
            slow_run_sum = 0.0

            error_list = []
            last_speed = 0
            id_speed = -1
            last_dist = 0
            id_dist = -1
            last_field = 0
            id_field = -1
            try:
                read_field = file_to_read_field.readline()
                read_field_list = read_field.split(',')
                lonA, latA, lonB, latB, lonC, latC, lonD, latD = read_field_list[4:]
                pointA = (float(lonA[1:]), float(latA[1:]))
                pointB = (float(lonB[1:]), float(latB[1:]))
                pointC = (float(lonC[1:]), float(latC[1:]))
                pointD = (float(lonD[1:]), float(latD[1:len(latD)-2]))
                pointA, pointB, pointC, pointD = self.expand_field(pointA, pointB, pointC, pointD, 1.2)
            except:
                pointA = (0, 0)
                pointB = (0, 0)
                pointC = (0, 0)
                pointD = (0, 0)
            for value_list in read_values[1:]:
                value_csv_list = value_list.split(',')

                time_str = value_csv_list[0]
                for time_csv_string in value_csv_list[1:6]:
                    time_str = time_str + '.' + time_csv_string
                if start_time_file == 'Empty':
                    start_time_file = time_str

                speed_float = float(value_csv_list[8])
                # speed가 38보다 크게 변경된 순간에는 순간에는 list 형태로 start_time append
                # speed가 38보다 작게 변경된 순간에는 start_time을 append한 위치에 end_time과 error_code 작성
                if speed_float >= 38.0 and value_list != read_values[len(read_values)-1]:
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

                if (not self.checkPointInRectangle(pointP, pointA, pointB, pointC, pointD)) \
                        and value_list != read_values[len(read_values) - 1]:
                    if last_field == 0:
                        last_field = 1
                        error_list.append(time_str)
                        id_field = len(error_list)-1
                else:
                    if last_field == 1:
                        last_field = 0
                        error_list[id_field] = error_list[id_field] + ',' + time_str + ',OutOfField'

                if (not last_speed) and (not last_dist) and (not last_field):
                    if speed_float < 7:
                        slow_run_sum = slow_run_sum+dist_float/speed_float

            file_list = file_read.split('/')
            file_name = file_list[len(file_list)-1]
            used_second = self.time_to_second(time_str)-self.time_to_second(start_time_file)
            sum_slow_time = sum_slow_time + slow_run_sum/used_second
            info_lists.append([int(file_name[:len(file_name)-4]), slow_run_sum/used_second])

            # file에서 읽어온 정보를 이용해 speed_error를 찾고 error.csv에 쓰기
            for error_str in error_list:
                file_to_write.write(path_read_folder+file_name+','+error_str+'\n')
            file_to_read.close()

        avg_slow_time = sum_slow_time/len(info_lists)
        info_lists.sort()
        file_to_write_info.write(' '+str(avg_slow_time*1.7)+' '+str(avg_slow_time*1.5)+'\n')
        for info_list in info_lists:
            file_to_write_info.write(str(info_list[0]))
            file_to_write_info.write(' ' + str(info_list[1]))
            if avg_slow_time*1.6 < info_list[1]:
                file_to_write_info.write(', Abnormal\n')
            elif avg_slow_time*1.5 < info_list[1]:
                file_to_write_info.write(', Doubt\n')
            else:
                file_to_write_info.write(', Normal\n')

        file_to_read_field.close()
        file_to_write.close()
        file_to_write_info.close()


start_time = time.time()

if __name__ == "__main__":
    # argv를 이용해 필요한 dir명을 전달받아 이용하면 유용할 것
    need_to_compute_dir = '드래곤즈 0626 경기'
    noisefinderObject = NoiseFinder()

    root_for_read = 'data/3. data_csv_second_average/'
    root_for_read_field = 'data/8. data_field_find/'
    root_for_write = 'data/30. data_noise/'
    noisefinderObject.find_noise_in_data(root_for_read, root_for_read_field, root_for_write, need_to_compute_dir)
    end_time = time.time()-start_time
    print('noise_finder : '+str(format(end_time, '.6f'))+'sec\n')
