import glob
import os
from helper import common_os_helper
from helper.gp_convert.gp2ochconverter import *


class Converter:

    def convert_gp_to_och(self, path_gp, path_och, name_of_dir):
        # path_gp 읽을 gp파일이 저장된 path를 string으로 저장
        # path_och och파일을 쓰고자 하는 path를 string으로 저장
        # name_of_dir 읽을 csv파일과 och파일을 쓰고자 하는 dir name을 string으로 저장

        path_gp = common_os_helper.check_slash(path_gp)
        path_och = common_os_helper.check_slash(path_och)
        name_of_dir = common_os_helper.check_slash(name_of_dir)
        path_gp = path_gp + name_of_dir + '*.gp'
        path_och = path_och + name_of_dir
        common_os_helper.create_dir(path_och)
        files_gp = glob.glob(path_gp)

        for file_gp in files_gp:
            file_och = path_och+file_gp[len(path_gp)-4:]
            file_och = file_och[:len(file_och)-2]+'och'
            # 각 파일 마다 initialize 하여 GpToOchConvert Object를 생성 후 convert 실행
            GpToOchConverterObject = GpToOchConverter()
            GpToOchConverterObject.convertToOchFile(file_gp, file_och)
            # .och파일에 내용이 없으면 제거
            if os.path.getsize(file_och) < 1000:
                os.remove(file_och)

    def convert_och_to_csv(self, path_och, path_csv, name_of_dir):
        # path_och 읽을 och파일이 저장된 path를 string으로 저장
        # path_csv csv파일을 쓰고자 하는 path를 string으로 저장
        # name_of_dir 읽을 csv파일과 och파일을 쓰고자 하는 dir name을 string으로 저장

        path_och = common_os_helper.check_slash(path_och)
        path_csv = common_os_helper.check_slash(path_csv)
        name_of_dir = common_os_helper.check_slash(name_of_dir)
        path_och = path_och + name_of_dir + '*.och'
        path_csv = path_csv + name_of_dir
        
        common_os_helper.create_dir(path_csv)

        files_och = glob.glob(path_och)
        # .csv의 경우 가장 첫번째 줄에 이후 정보들의 저장 순서를 저장함
        write_order = 'year,month,day,hour,minute,second,point_second,longitude,latitude,speed'

        for file_och in files_och:
            # .och파일과 같은 이름을 가진 .csv파일명 생성
            file_csv = path_csv+file_och[len(path_och)-5:]
            file_csv = file_csv[:len(file_csv)-3]+'csv'

            file_to_read = open(file_och, 'r')
            file_to_write = open(file_csv, 'w')

            file_to_write.writelines(write_order+'\n')

            # 한 줄씩 .och파일을 읽으며 .csv파일에 적절히 변환하여 저장
            read_values = file_to_read.readlines()
            for read_value in read_values:
                try:
                    value_och_list = read_value.split(' ')
                    if len(value_och_list) < 4 :
                        raise IndexError
                    value_time_list = value_och_list[0].split('.')
                    if len(value_time_list) < 7:
                        raise IndexError

                    # 시간과 관련된 정보는 '.'으로 이어져 있는 것을 ','로 연결
                    data_to_write = value_time_list[0]
                    for time_string in value_time_list[1:]:
                        data_to_write = data_to_write + ',' + time_string

                    # 이외의 정보는 ' '로 이어져 있는 것을 ','로 연결
                    for value_och_string in value_och_list[1:]:
                        data_to_write = data_to_write+','+value_och_string
                    file_to_write.write(data_to_write)

                except IndexError:
                    # .och 파일에 의미없는 정보가 저장된 줄은 pass
                    pass

            file_to_write.close()
            file_to_read.close()

    def convert_csv_to_och(self, path_csv, path_och, name_of_dir):
        # path_csv 읽을 csv파일이 저장된 path를 string으로 저장
        # path_och och파일을 쓰고자 하는 path를 string으로 저장
        # name_of_dir 읽을 csv파일과 och파일을 쓰고자 하는 dir name을 string으로 저장

        path_och = common_os_helper.check_slash(path_och)
        path_csv = common_os_helper.check_slash(path_csv)
        name_of_dir = common_os_helper.check_slash(name_of_dir)
        path_och = path_och + name_of_dir
        path_csv = path_csv + name_of_dir+'*.csv'

        common_os_helper.create_dir(path_och)

        files_csv = glob.glob(path_csv)

        for file_csv in files_csv:
            # .csv파일과 같은 이름을 가진 .och파일명 생성
            file_och = path_och+file_csv[len(path_csv)-5:]
            file_och = file_och[:len(file_och)-3]+'och'

            file_to_read = open(file_csv, 'r')
            file_to_write = open(file_och, 'w')

            # 한 줄씩 .csv파일을 읽으며 .och파일에 적절히 변환하여 저장
            read_values = file_to_read.readlines()
            for read_value in read_values[1:]:
                value_csv_list = read_value.split(',')

                # 시간과 관련된 정보는 ','로 이어져 있는 것을 '.'로 연결
                data_to_write = value_csv_list[0]
                for time_csv_string in value_csv_list[1:7]:
                    data_to_write = data_to_write+'.'+time_csv_string

                # 이외의 정보는 ','로 이어져 있는 것을 ' '로 연결
                for value_csv_string in value_csv_list[7:]:
                    data_to_write = data_to_write+' '+value_csv_string
                file_to_write.write(data_to_write)

            file_to_write.close()
            file_to_read.close()

