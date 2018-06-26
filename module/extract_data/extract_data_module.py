import glob
import os
import math

class Extract_data:

    # gps좌표를 meter scale의 distance로 바꾸어준다
    def measure_position(self, lat1, lon1, lat2, lon2):
        R = 6378.137
        dLat = (lat1 - lat2) * math.pi / 180
        dLon = (lon1 - lon2) * math.pi / 180
        a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(lat1 * math.pi / 180) * math.cos(lat2 * math.pi / 180) * math.sin(dLon / 2) * math.sin(dLon / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d = R * c
        return d * 1000

    # csv파일의 시간 기록단위를 1hz로 변경해주는 method
    def summarize_csv(self, path_csv_folder, path_output_folder):
        #디렉토리가 없으면은 생성해준다.
        try:
            if not os.path.exists(path_output_folder):
                os.makedirs(path_output_folder)
        except OSError:
            print('Error: Creating directory.'+ path_output_folder)
        #glob.glob로 해당경로상에 존재하는 .csv파일의 경로를 읽어들여 list로 정리
        files_csv = glob.glob(path_csv_folder + '*.csv')
        print(files_csv)
        # csv파일의 첫줄에 들어갈 정보들을 순서대로 입력해주는 write_order
        write_order = 'year,month,day,hour,minute,second,longitude,latitude,speed,distance'
        #csv파일들을 하나하나 생성한 후 해당 값들을 적어주는 부분이다.
        for file_csv in files_csv:

            file_summarized = path_output_folder + file_csv[len(path_csv_folder):]
            file_summarized = file_summarized[:len(file_summarized)-3]+'csv'
            file_to_read = open(file_csv,'r')
            file_to_write = open(file_summarized,'w')
            file_to_write.writelines(write_order+'\n')

            read_values = file_to_read.readlines()
            data = read_values[1].split(',')
            #checktime은 초까지의 시간이 동일한 경우를 check하기 위해 0.1초단위는 버리고 초단위의 시간만 기록한다.
            check_time_temp = data[0:6]
            value_temp = data[7:10]
            value_temp.append(0)
            value_temp[0]=float(value_temp[0]) #longitude
            value_temp[1] = float(value_temp[1]) #latitude
            value_temp[2] = float(value_temp[2])

            count = 1
            # distance를 계산해주기 위한 좌표의 초기값 설정
            last_longi = value_temp[0]
            last_lati = value_temp[1]
            # csv파일을 읽어들이는 부분이다.
            for read_value in read_values[2:]:
                data = read_value.split(',')
                check_time = data[0:6]
                value = data[7:10]
                value.append(0)
                value[0] = float(value[0]) #longitude
                value[1] = float(value[1]) #latitude
                value[2] = float(value[2])

                if check_time == check_time_temp:#만약 초단위까지의 시간이 같다면 그 값을 저장하고 계속해서 더해나간다.
                    for i, v in enumerate(value):
                        value_temp[i] = value_temp[i] + v
                    count = count + 1
                    #이 부분은 마지막 정보, 즉 최하단의 줄을 읽어드린 후의 값을 안적고 fileclose하는 것을 방지하기 위해 distance값을 보유하게 하는 것
                    value_temp[3] = self.measure_position(last_lati, last_longi, value_temp[1]/count, value_temp[0]/count)
                else:#초단위까지의시간이 같지 않은경우, 즉 초가 바뀌었을때 연산 후 파일에다가 기록해준다.
                    value_temp[0] = float(value_temp[0]) / count  # longitude
                    value_temp[1] = float(value_temp[1]) / count  # latitude
                    value_temp[2] = float(value_temp[2]) / count
                    value_temp[3] = self.measure_position(last_lati, last_longi, value_temp[1], value_temp[0])
                    last_longi = value_temp[0]
                    last_lati = value_temp[1]
                    # last,즉 이전 위도 경도 값을 남김으로서 다음에 들어온 값을 가지고 연산을 실행한다.
                    #현재의 시간정보를 기록
                    for time_idx, time_string in enumerate(check_time_temp[:6]):
                        if time_idx == 0:
                            file_to_write.write(time_string)
                        else:
                            file_to_write.write(','+time_string)
                    # write함수를 쓰기위해 value값들을 string으로 다시 형변환해준다.
                    value_temp[0] = str(value_temp[0])
                    value_temp[1] = str(value_temp[1])
                    value_temp[2] = str(value_temp[2])
                    value_temp[3] = str(value_temp[3])
                    # 이 후 value값들을 기록하고 temp들을 초기화 해준다.
                    for value_string in value_temp:
                        file_to_write.write(',' + value_string)
                    file_to_write.write('\n')

                    check_time_temp = check_time
                    value_temp = value
                    count = 1
            # 이부분은 반복문 안과 같지만 마지막 줄을 적어주기 위해 한줄을 추가하여 마지막줄의 연산까지 하는 것이다.
            for time_idx, time_string in enumerate(check_time_temp[:6]):
                if time_idx == 0:
                    file_to_write.write(time_string)
                else:
                    file_to_write.write(',' + time_string)
            value_temp[0] = value_temp[0] / count
            value_temp[1] = value_temp[1] / count
            value_temp[2] = value_temp[2] / count

            value_temp[0] = str(value_temp[0])
            value_temp[1] = str(value_temp[1])
            value_temp[2] = str(value_temp[2])
            value_temp[3] = str(value_temp[3])
            for value_string in value_temp:
                file_to_write.write(',' + value_string)
            file_to_write.write('\n')

            file_to_read.close()


if __name__ == "__main__":

    root_csv = 'data/2. data_csv_format/'
    root_summarized = 'data/3. data_csv_second_average/'
    # 현재는 디렉토리가 드래곤즈지만 나중에 변수로 둘 수 있을 듯하다.
    name_of_dir = '드래곤즈 0617/'

    Extract_data()
    extractObject = Extract_data()
    extractObject.summarize_csv(root_csv + name_of_dir, root_summarized +name_of_dir)
