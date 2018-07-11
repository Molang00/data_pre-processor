import glob
import os
import time
import openpyxl


class Inspect_data:
    Players = []

    def creat_dir(self, directory):
        # directory dir명이 포함도니 path가 string으로 저장
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except:
            print('Error: Creating directory. '+directory)

    def check_slash(self, path_string):
        # path_string 원하는 경로를 string으로 저장

        # path의 마지막 경로에 /혹은 \가 없다면 /를 추가하여 return
        if path_string[len(path_string)-1] != '/' and path_string[len(path_string)-1] != '\\':
            path_string = path_string+'/'
        return path_string

    def find_file_name(self, name_string, place):
        # name_string 폴더의 이름을 string형태로 저장
        # place home이라면 H, away라면 A를 저장

        # serial 번호와 등번호가 적힌 .csv file의 이름을 찾음
        name_list = name_string.split('-')
        value_list = name_list[1].split('_')

        new_name = name_list[0] + '-' + str(value_list[0])
        if value_list[1] == 'U17':
            new_name = new_name + '_U17'
        new_name = new_name+'_'+place+'_'+value_list[2]
        new_name = new_name.replace('/', '.xlsx')
        return new_name

    def time_calculate(self, time_string, term_min_int, type_list):
        time_list = time_string.split(':')
        time_list[1] = int(time_list[1]) + term_min_int
        time_list[0] = int(time_list[0])
        while int(time_list[1]) >= 60:
            time_list[0] = int(time_list[0]) + 1
            time_list[1] = int(time_list[1]) - 60
        if type_list: return time_list
        else:
            time_str = str(time_list[0])+':'+str(time_list[1])
            return time_str

    def time_comparision(self, time_log, time_xl, term):
        # target_list 비교하고자 하는 목적의 시간을 string으로 저장
        # comparision_target_smaller 비교할 범위 중 작은 시간을 string으로 저장
        # comparision_target_larger 비교할 범위 중 큰 시간을 string으로 저장

        # term이 -1인 경우는 본 에러를 확인하지 않겠다는 뜻이므로 다음에러로 넘어가는 1을 return
        if term == -1:
            return 1

        list_value = self.time_calculate(time_log, term, True)
        comparision_value_smaller = self.time_calculate(time_xl, 0, True)
        comparision_value_larger = self.time_calculate(time_xl, term * 2, True)

        if list_value[0]-comparision_value_larger[0] > 9 and list_value[0]-comparision_value_smaller[0] > 9:
            comparision_value_smaller[0] += 12
            comparision_value_larger[0] += 12

        # 비교할 범위보다 작은 쪽으로 벗어나면 -1, 큰쪽으로 벗어나면 1, 범위에 포함되면 0을 return
        if comparision_value_smaller[0]>list_value[0]:
            return -1
        if comparision_value_larger[0]<list_value[0]:
            return 1
        if comparision_value_smaller[1]>list_value[1]:
            return -1
        if comparision_value_larger[1]<list_value[1]:
            return 1
        return 0

    def list_compare(self, info_list, log_list, error_list, error_code, ck_time = True):
        info_list.sort()
        log_list.sort()

        info_id = 0
        log_id = 0

        while info_id < len(info_list) and log_id < len(log_list):
            if int(info_list[info_id][0]) < int(log_list[log_id][0]):
                error_list.append(error_code[0][0]+str(info_list[info_id][0])+error_code[0][1])
                info_id += 1
                continue
            if int(info_list[info_id][0]) > int(log_list[log_id][0]):
                error_list.append(error_code[1][0]+str(log_list[log_id][0])+error_code[1][1])
                log_id += 1
                continue
            if ck_time and self.time_comparision(log_list[log_id][1], info_list[info_id][1], 3) != 0:
                error_list.append(error_code[2][0]+str(info_list[info_id][0])+error_code[2][1])
            elif not ck_time:
                self.Players.append([info_list[info_id][0], '', ''])
            log_id += 1
            info_id += 1

        while info_id < len(info_list):
            error_list.append(error_code[0][0]+str(info_list[info_id][0])+error_code[0][1])
            info_id += 1
        while log_id < len(log_list):
            error_list.append(error_code[1][0]+str(log_list[log_id][0])+error_code[1][1])
            log_id += 1

        return error_list

    def set_players_runtime(self, in_list, out_list):
        in_player = []
        in_time = []
        out_player = []
        out_time = []
        for in_val in in_list:
            in_player.append(in_val[0])
            in_time.append(in_val[1])
        for out_val in out_list:
            out_player.append(out_val[0])
            out_time.append(out_val[1])

        for i in range(len(self.Players)):
            try:
                num = in_player.index(self.Players[i][0])
                self.Players[i][1] = in_time[num]
            except ValueError:
                self.Players[i][1] = self.START1
            try:
                num = out_player.index(self.Players[i][0])
                self.Players[i][2] = out_time[num]
            except ValueError:
                self.Players[i][2] = self.END2

    def write_error(self, path_write_folder, file_name, write_order, error_list):
        self.creat_dir(path_write_folder)
        file_to_write = open(path_write_folder + file_name, 'w', encoding="utf-8")
        file_to_write.write(write_order)
        for error_str in error_list:
            file_to_write.write(error_str + '\n')
        file_to_write.close()

    def find_diff_log(self, path_read_xl_folder, path_read_log_folder, path_write_folder, name_of_dir):
        # path_read_folder 읽을 파일이 저장된 path를 string으로 저장
        # path_write_folder 파일을 쓰고자 하는 path를 string으로 저장
        # name_of_dir 읽을 파일과 쓰고자 하는 파일의 dir name을 string으로 저장

        path_read_xl_folder = self.check_slash(path_read_xl_folder)
        path_read_log_folder = self.check_slash(path_read_log_folder)
        path_write_folder = self.check_slash(path_write_folder)
        name_of_dir = self.check_slash(name_of_dir)
        path_write_folder = path_write_folder+name_of_dir

        file_to_read_log = open(path_read_log_folder+name_of_dir+'log.csv')
        log_info_lists = file_to_read_log.readlines()

        try:
            file_to_read_xl = openpyxl.load_workbook(path_read_xl_folder+self.find_file_name(name_of_dir,'H'))
        except:
            file_to_read_xl = openpyxl.load_workbook(path_read_xl_folder+self.find_file_name(name_of_dir, 'A'))

        active_sheet = file_to_read_xl.active
        player_sub = active_sheet['A11':'C17']
        start_time1 = active_sheet['A7'].value
        end_time1 = active_sheet['B7'].value
        start_time2 = active_sheet['D7'].value
        end_time2 = active_sheet['E7'].value

        start1 = log_info_lists[1].split(',')[1]
        self.START1 = start1
        error = self.time_comparision(start1, start_time1, 3)

        error_list = []
        if error != 0:
            error_list.append('TimeDiff,START1')

        sub_in_list = []
        sub_out_list = []
        for row in player_sub:
            if row[0].value != row[1].value:
                time_list = row[0].value.split('+')

                time_int = 0
                for time_val in time_list:
                    time_int += int(time_val)

                if int(time_list[0]) <= 45:
                    time_str = self.time_calculate(start_time1, time_int, False)
                else:
                    time_str = self.time_calculate(start_time2, time_int, False)
                sub_in_list.append([int(row[1].value), time_str])
                sub_out_list.append([int(row[2].value), time_str])

        sub_log_in_list = []
        sub_log_out_list = []
        for log_info in log_info_lists[2:]:
            log_list = log_info.split(',')
            if log_list[0] == 'END1':
                self.END1 = log_list[1]
                if self.time_comparision(log_list[1], end_time1, 3) != 0:
                    error_list.append('TimeDiff,END1,incorrect')
            if log_list[0] == 'START2':
                self.START2 = log_list[1]
                if self.time_comparision(log_list[1], start_time2, 3) != 0:
                    error_list.append('TimeDiff,START2,incorrect')
            if log_list[0] == 'END2':
                self.END2 = log_list[1]
                if self.time_comparision(log_list[1], end_time2, 3) != 0:
                    error_list.append('TimeDiff,END2,incorrect')
            if log_list[0] == 'SUB':
                sub_log_in_list.append([int(log_list[3]), log_list[1]])
                sub_log_out_list.append([int(log_list[2]), log_list[1]])

        self.set_players_runtime(sub_log_in_list, sub_log_out_list)

        error_code = [["SubPlayerDiff,", ",Can't find at log"], ["SubPlayerDiff,", "Can't find at info"],
                      ["TimeDiff,", ",incorrect"]]
        error_list = self.list_compare(sub_in_list, sub_log_in_list, error_list, error_code)
        error_list = self.list_compare(sub_out_list, sub_log_out_list, error_list, error_code)
        write_order = 'ErrorCode,ErrorValue,Detail\n'
        self.write_error(path_write_folder, 'data_difference.txt', write_order, error_list)

    def look_up_files_stable(self, path_raw_data, path_write, name_of_dir):
        path_raw_data = self.check_slash(path_raw_data)
        path_write = self.check_slash(path_write)
        name_of_dir = self.check_slash(name_of_dir)
        path_raw_data = path_raw_data + name_of_dir
        path_write = path_write + name_of_dir

        error_list = []
        for player in self.Players:
            file = open(path_raw_data+str(player[0])+'.csv', 'r')
            read_values = file.readlines()

            valid_count = 0.0
            total_count = 0.0
            for i in range(1, len(read_values), 300):
                time_str = read_values[i].split(',')[3:5]
                time_str = time_str[0]+':'+time_str[1]
                if (self.time_comparision(time_str, player[1], 3) >= 0) and (
                        self.time_comparision(time_str, player[2], 3) <= 0):
                    valid_count += 1.0
                total_count += 1.0

            if valid_count/total_count <= 0.6:
                error_list.append("Unstable,"+str(player[0])+",Input value lost")
            elif valid_count/total_count <= 0.9:
                error_list.append("Unstable,"+str(player[0])+",Some input value lost")
        write_order = "ErrorCode,ErrorValue,Detail\n"
        self.write_error(path_write, "device_stability.txt", write_order, error_list)

    def look_up_player(self, path_read_xl, path_raw_data, path_write, name_of_dir):
        path_read_xl = self.check_slash(path_read_xl)
        path_raw_data = self.check_slash(path_raw_data)
        path_write = self.check_slash(path_write)
        name_of_dir = self.check_slash(name_of_dir)
        path_raw_data = path_raw_data+name_of_dir
        path_write = path_write+name_of_dir

        files_raw = glob.glob(path_raw_data+'*.csv')
        player_raw = []
        error_list = []
        for player in files_raw:
            player_num = player[len(path_raw_data):len(player)-4]
            if len(player_num.split('_')) > 1:
                error_list.append("NoMatch,"+str(player_num)+",There is no player_num")
            else:
                player_raw.append([int(player_num),0])

        try:
            file_to_read_xl = openpyxl.load_workbook(path_read_xl+self.find_file_name(name_of_dir,'H'))
        except:
            file_to_read_xl = openpyxl.load_workbook(path_read_xl+self.find_file_name(name_of_dir, 'A'))
        active_sheet = file_to_read_xl.active
        player_info = active_sheet['F11':'F28']
        player_num = []
        for player in player_info:
            if player[0].value:
                player_num.append([int(player[0].value),0])

        error_code = [["NoData,", ",Can't find data"], ["NoPlayer,", ",Can't find Player"]]

        error_list = self.list_compare(player_num, player_raw, error_list, error_code, False)
        write_order = "ErrorCode,ErrorValue,Detail\n"
        self.write_error(path_write, 'player_difference.txt', write_order, error_list)

    def do_inspection(self, path_read_xl, path_read_log, path_raw_data, path_write, name_of_dir):
        self.look_up_player(path_read_xl, path_raw_data, path_write, name_of_dir)
        self.find_diff_log(path_read_xl, path_read_log, path_write, name_of_dir)
        self.look_up_files_stable(path_raw_data, path_write, name_of_dir)


root_read_xl = 'data/9. data_log_xl/'
root_read_log = 'data/0. data_gp_format/'
root_raw_data = 'data/2. data_csv_format/'
root_write = 'data/31. data_inspection/'
name_of_dir = 'A-04_U18_수원F/'

InspectDataObject = Inspect_data()
InspectDataObject.do_inspection(root_read_xl, root_read_log, root_raw_data, root_write, name_of_dir)
