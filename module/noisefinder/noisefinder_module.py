import glob
import os


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

    def find_speed_error(self, values_list):
        # value_list .csv file에서 읽어온 정보를 줄별로 담고있는 list를 저장

        error_list = []
        last = 0
        for value_list in values_list[1:]:
            value_csv_list = value_list.split(',')

            # .csv file의 정보에서 time에 관한 정보와 speed에 관한 정보 추출
            time_str = value_csv_list[0]
            for time_csv_string in value_csv_list[1:6]:
                time_str = time_str + '.' + time_csv_string
            speed_float = float(value_csv_list[8])

            # speed가 38보다 크게 변경된 순간에는 start_time을 reset
            # speed가 38보다 작게 변경된 순간에는 list에 string형태로 append
            if speed_float >= 38.0:
                if last == 0:
                    last = 1
                    start_time = time_str
            else:
                if last == 1:
                    last = 0
                    error_str = start_time+','+time_str+',OverSpeed'
                    error_list.append(error_str)
        return error_list

    def find_noise_in_data(self, path_read, path_write, name_of_dir):
        # path_read 읽을 파일이 저장된 path를 string으로 저장
        # path_write 파일을 쓰고자 하는 path를 string으로 저장
        # nmae_of_dir 읽을 파일과 쓰고자 하는 파일의 dir name을 string으로 저장

        path_read = self.check_slash(path_read)
        path_write = self.check_slash(path_write)
        name_of_dir = self.check_slash(name_of_dir)
        path_read = path_read+name_of_dir+'*.csv'
        path_write = path_write+name_of_dir

        self.create_dir(path_write)
        file_to_write = open(path_write+'error.csv', 'w')

        files_read = glob.glob(path_read)
        for file_read in files_read:
            file_to_read = open(file_read, 'r')

            read_values = file_to_read.readlines()

            # file에서 읽어온 정보를 이용해 speed_error를 찾고 error.csv에 쓰기
            speed_error_list = self.find_speed_error(read_values)
            for speed_error_str in speed_error_list:
                file_to_write.write(file_read+','+speed_error_str+'\n')

if __name__ == "__main__":

    # argv를 이용해 필요한 dir명을 전달받아 이용하면 유용할 것
    need_to_compute_dir = '드래곤즈 0617/'
    noisefinderObject = NoiseFinder()

    root_for_read = 'data/3. data_csv_second_average/'
    root_for_write = 'data/30. data_noise/'
    noisefinderObject.find_noise_in_data(root_for_read, root_for_write, need_to_compute_dir)
