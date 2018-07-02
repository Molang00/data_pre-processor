import os
import glob
import time
import shutil


class Rename_file:

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

    def find_file_name(self, name_string, place):
        # name_string 폴더의 이름을 string형태로 저장
        # place home이라면 H, away라면 A를 저장

        # serial 번호와 등번호가 적힌 .csv file의 이름을 찾음
        name_list = name_string.split('-')
        value_list = name_list[1].split('_')

        new_name = name_list[0] + '-' + str(int(value_list[0]))
        if value_list[1] == 'U17':
            new_name = new_name + '_U17'
        new_name = new_name+'_'+place+'_'+value_list[2]
        new_name = new_name.replace('/', '.csv')
        return new_name

    def rename_csv_file(self, path_target_folder, path_read_info_folder, name_of_dir):
        # path_target_folder 이름을 변경하고자하는 target이 있는 folder path를 string으로 저장
        # path_read_info_folder serial_num,back_num으로 이루어진 .csv file이 있는 path를 string으로 저장
        # name_of_dir 파일을 읽고 쓸 dir name을 string으로 저장

        path_target_folder = self.check_slash(path_target_folder)
        path_read_info_folder = self.check_slash(path_read_info_folder)
        name_of_dir = self.check_slash(name_of_dir)
        path_target_folder = path_target_folder+name_of_dir

        self.create_dir(path_target_folder+'noneed/')

        # 현재 target인 팀이 home인지 away인지 모르기 때문에 두가지 경우 모두 시도
        try:
            file_read_info = open(path_read_info_folder+self.find_file_name(name_of_dir, 'H'), 'r')
        except FileNotFoundError:
            file_read_info = open(path_read_info_folder+self.find_file_name(name_of_dir, 'A'), 'r')

        info_values = file_read_info.readlines()
        info_values.sort()
        index = -1
        serial_num = -1
        last = -1
        count = 0

        files_target = glob.glob(path_target_folder+'*.csv')
        for file_target in files_target:
            try:
                file_target = file_target.replace('\\', '/')
                name_list = file_target.split('/')
                target_num = int(name_list[len(name_list)-1].split('_')[0])
            except:
                # filename이 변환되어 있는 경우 continue
                continue

            try:
                # target_num과 serial_num이 모두 정렬되어 있기 때문에 단순비교가 가능
                while target_num > serial_num:
                    index = index+1
                    serial_num = int(info_values[index].split(',')[0])
                    back_num = info_values[index].split(',')[1]
                    back_num = back_num[:len(back_num)-1]
                # 정렬된 상황에서 target_num < serial_num은 같은 번호를 가진 serial_num이 없다는 뜻이므로 noneed로 이동
                if target_num < serial_num:
                    shutil.move(file_target, path_target_folder+'noneed/'+name_list[len(name_list)-1])
                    continue
            except IndexError:
                shutil.move(file_target, path_target_folder+'noneed/'+name_list[len(name_list)-1])
                continue

            # 같은 serial number를 가진 파일이 여러개일 경우 (count)의 형식으로 이름에 추가
            if last == target_num:
                count = count+1
                back_num = back_num+'('+str(count)+')'
            else:
                count = 0
                last = target_num

            name_list[len(name_list)-1] = back_num+'.csv'
            new_name = path_target_folder+name_list[len(name_list)-1]
            os.rename(file_target, new_name)


start_time = time.time()

RenameFileObject = Rename_file()
root_target = 'data/2. data_csv_format/'
root_info = 'helper/1. number_info/'
need_to_compute_dir = 'A-01_U18_서울/'

RenameFileObject.rename_csv_file(root_target, root_info, need_to_compute_dir)

end_time = time.time() - start_time
print('file_rename : ' + str(format(end_time, '.6f')) + 'sec\n')