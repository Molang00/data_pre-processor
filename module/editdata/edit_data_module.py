import glob
import os
import time


class EditData:

    def create_dir(self, directory):
        # directory dir명이 포함된 path가 string으로 저장
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except OSError:
            print('Error: Creating directory. ' + directory)

    def check_slash(self, path_string):
        # path_string 원하는 경로를 string으로 저장

        # path의 마지막 경로에 /혹은 \가 없다면 /를 추가하여 return
        if path_string[len(path_string) - 1] != '/' and path_string[len(path_string) - 1] != '\\':
            path_string = path_string + '/'
        return path_string

    def time_calculate(self, time_string, term_second_int):
        time_list = time_string.split('.')
        time_list.reverse()
        time_list[0] = str(int(time_list[0]) + term_second_int)
        if int(time_list[0]) >= 60:
            time_list[1] = str(int(time_list[1]) + 1)
            time_list[0] = str(int(time_list[0]) - 60)
            if int(time_list[1]) >= 60:
                time_list[2] = str(int(time_list[2]) + 1)
                time_list[1] = str(int(time_list[1]) - 60)
        time_list.reverse()
        return time_list

    def time_comparision(self, target_list, comparision_target_smaller, comparision_target_larger, term):
        # target_list 비교하고자 하는 목적의 시간을 string으로 저장
        # comparision_target_smaller 비교할 범위 중 작은 시간을 string으로 저장
        # comparision_target_larger 비교할 범위 중 큰 시간을 string으로 저장

        # term이 -1인 경우는 본 에러를 확인하지 않겠다는 뜻이므로 다음에러로 넘어가는 1을 return
        if term == -1:
            return 1

        list_value = self.time_calculate(target_list, term)
        comparision_value_smaller = self.time_calculate(comparision_target_smaller, 0)
        comparision_value_larger = self.time_calculate(comparision_target_larger, term * 2)

        # 비교할 범위보다 작은 쪽으로 벗어나면 -1, 큰쪽으로 벗어나면 1, 범위에 포함되면 0을 return
        is_small = 1
        is_large = 1
        for index, value in enumerate(list_value):
            if int(value) < int(comparision_value_smaller[index]) and is_small:
                return -1
            if int(value) > int(comparision_value_smaller[index]) and is_small:
                is_small = 0
            if int(value) > int(comparision_value_larger[index]) and is_large:
                return 1
            if int(value) < int(comparision_value_larger[index]) and is_large:
                is_large = 0
        return 0

    def cut_error(self, path_read_csv_folder, path_read_error_folder, path_write_folder, name_of_dir, ck_field=True, ck_dist=True, ck_speed=True):
        # path_read_csv_folder 읽을 .csv파일이 저장된 폴더 경로를 string으로 저장
        # path_read_error_folder 읽을 error.csv파일이 저장된 폴더 경로를 string으로 저장
        # path_write_folder error범위를 제외한 부분을 .csv로 저장할 폴더 경로를 string으로 저장
        # name_of_dir 파일을 읽고 쓸 dir name을 string으로 저장

        # 경로의 예외처리와 최종 경로 지정
        path_read_csv_folder = self.check_slash(path_read_csv_folder)
        path_read_error_folder = self.check_slash(path_read_error_folder)
        path_write_folder = self.check_slash(path_write_folder)
        name_of_dir = self.check_slash(name_of_dir)
        path_read_csv_folder = path_read_csv_folder + name_of_dir + '*.csv'
        path_read_error_folder = path_read_error_folder + name_of_dir + 'error.csv'
        path_write_folder = path_write_folder + name_of_dir

        # 파일을 쓸 위치에 폴더를 만들고 error.csv 열기
        self.create_dir(path_write_folder)
        file_to_error_read = open(path_read_error_folder, 'r')
        read_error_values = file_to_error_read.readlines()
        index_error = 1
        read_error_value = read_error_values[index_error].split(',')

        files_read_csv = glob.glob(path_read_csv_folder)

        for file_read_csv in files_read_csv:
            file_name = file_read_csv[len(path_read_csv_folder) - 5:]
            file_write_csv = path_write_folder + file_name

            file_to_csv_read = open(file_read_csv, 'r')
            file_to_write = open(file_write_csv, 'w')

            read_csv_values = file_to_csv_read.readlines()
            file_to_write.write(read_csv_values[0])

            index_csv = 1
            while index_csv < len(read_csv_values):
                if read_error_value[1] == file_name and index_error < len(read_error_values):
                    csv_value_list = read_csv_values[index_csv].split(',')

                    time_str = csv_value_list[0]
                    for time_value in csv_value_list[1:6]:
                        time_str = time_str + '.' + time_value

                    term_int = -1
                    if read_error_value[4] == 'OverSpeed\n' and ck_speed:
                        term_int = 1
                    if read_error_value[4] == 'OverDist\n' and ck_dist:
                        term_int = 1
                    if read_error_value[4] == 'OutOfField\n' and ck_field:
                        term_int = 2

                    comp_result = self.time_comparision(time_str, read_error_value[2], read_error_value[3], term_int)
                    # 현재 읽은 줄의 시간이 error의 범위보다 큰쪽으로 벗어났다면 다음 error line에 대해 현재 읽은 줄을 확인
                    if comp_result == 1:
                        try:
                            index_csv = index_csv - 1
                            index_error = index_error + 1
                            read_error_value = read_error_values[index_error].split(',')
                        except IndexError:
                            # 마지막 error의 범위를 벗어났을 경우 .csv 파일의 나머지를 모두 출력
                            file_to_write.write(read_csv_values[index_csv])
                    if comp_result == -1:
                        file_to_write.write(read_csv_values[index_csv])

                # error의 정보가 현재 읽는 중인 file_name보다 작다면 error의 index를 증가시킨다.
                elif read_error_value[1] < file_name and index_error < len(read_error_values):
                    try:
                        index_csv = index_csv - 1
                        index_error = index_error + 1
                        read_error_value = read_error_values[index_error].split(',')
                    except IndexError:
                            # 마지막 error의 범위를 벗어났을 경우 .csv 파일의 나머지를 모두 출력
                        file_to_write.write(read_csv_values[index_csv])

                else:
                    file_to_write.write(read_csv_values[index_csv])

                index_csv = index_csv + 1

            file_to_csv_read.close()
            file_to_write.close()
        file_to_error_read.close()
