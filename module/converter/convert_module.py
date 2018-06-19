import glob
import os


class Convert:

    # dir를 생성
    @staticmethod
    def create_dir(self, directory):
        # directory는 dir명이 포함된 path가 string으로 저장
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except OSError:
            print('Error: Creating directory. '+directory)

    @staticmethod
    def och_to_csv(self, path_och, path_csv):
        # path_och는 읽을 och파일이 저장된 path+'*.och'를 string으로 저장 (glob에 최적화)
        # path_csv는 csv파일을 쓰고자 하는 path를 string으로 저장
        files_och = glob.glob(path_och)
        # .csv의 경우 가장 첫번째 줄에 이후 정보들의 저장 순서를 저장함
        write_order = 'year,month,day,hour,minute,second,point_second,longitude,latitude,speed'

        for file_och in files_och:
            # .och파일과 같은 이름을 가진 .csv파일명 생성
            file_csv = path_csv+file_och[len(path_och)-5:]
            file_csv = file_csv[:len(file_csv)-3]+'csv'
            print('read from file_och: '+file_och)
            print('write at file_csv: '+file_csv)

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
                    for time_string in value_time_list:
                        data_to_write = data_to_write + ',' + time_string

                    # 이외의 정보는 ' '로 이어져 있는 것을 ','로 연결
                    for value_och_string in value_och_list[1:]:
                        data_to_write = data_to_write+','+value_och_string
                    file_to_write.write(data_to_write)

                except IndexError:
                    # .och 파일에 의미없는 정보가 저장된 줄은 pass
                    print("Exist meaningless information\n")
                    pass

            file_to_write.close()
            file_to_read.close()

    @staticmethod
    def csv_to_och(self, path_csv, path_och):
        # path_csv 읽을 csv파일이 저장된 path+'*.csv'를 string으로 저장 (glob에 최적화)
        # path_och och파일을 쓰고자 하는 path를 string으로 저장
        files_csv = glob.glob(path_csv)

        for file_csv in files_csv:
            # .csv파일과 같은 이름을 가진 .och파일명 생성
            file_och = path_och+file_csv[len(path_csv)-5:]
            file_och = file_och[:len(file_och)-3]+'och'
            print('read from file_csv: '+file_csv)
            print('write at file_och: '+file_och)

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


# argv를 이용해 필요한 dir명을 전달받아 이용하면 유용할 것
name_of_dir = '드래곤즈 0617/'
convertObject = Convert()

# .och에서 .csv로의 변환을 원하는 경우
root_och_to_read = 'data/1. data_och_format/'
root_csv_to_write = 'data/2. data_csv_format/'
convertObject.create_dir(convertObject, root_csv_to_write+name_of_dir)
convertObject.och_to_csv(convertObject, root_och_to_read+name_of_dir+'*.och', root_csv_to_write+name_of_dir)

# .csv에서 .och로의 변환을 원하는 경우
# 현재 기능 구현 확인을 위한 임의 path이고, 추후 필요에 따른 경로 변경 필요
root_csv_to_read = 'data/3. data_csv_second_average/'
root_och_to_write = 'data/4. data_och_second_average/'
convertObject.create_dir(convertObject, root_och_to_write+name_of_dir)
convertObject.csv_to_och(convertObject, root_csv_to_read+name_of_dir+'*csv', root_och_to_write+name_of_dir)

