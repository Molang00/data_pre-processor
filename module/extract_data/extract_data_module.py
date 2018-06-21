import glob
import os
import math

class Extract_data:

    # gps좌표를 meter scale의 distance로 바꾸어준다
    def measure(self, lat1, lon1, lat2, lon2):
        R = 6378.137
        dLat = (lat1 - lat2) * math.pi / 180
        dLon = (lon1 - lon2) * math.pi / 180
        a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(lat1 * math.pi / 180) * math.cos(lat2 * math.pi / 180) * math.sin(dLon / 2) * math.sin(dLon / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d = R * c
        return d * 1000

    # csv파일의 시간 기록단위를 1hz로 변경해주는 method
    def summarize_csv(self, path_csv_folder, path_output_folder):
        try:
            if not os.path.exists(path_output_folder):
                os.makedirs(path_output_folder)
        except OSError:
            print('Error: Creating directory.'+ path_output_folder)

        files_csv = glob.glob(path_csv_folder + '*.csv')
        write_order = 'year,month,day,hour,minute,second,longitude,latitude,speed,distance'

        for file_csv in files_csv:

            file_summarized = path_output_folder + file_csv[len(path_csv_folder):]
            file_summarized = file_summarized[:len(file_summarized)-3]+'csv'
            file_to_read = open(file_csv,'r')
            file_to_write = open(file_summarized,'w')
            file_to_write.writelines(write_order+'\n')

            read_values = file_to_read.readlines()
            data = read_values[1].split(',')
            check_time_temp = data[0:6]
            value_temp = data[7:10]
            value_temp.append(0)
            value_temp[0]=float(value_temp[0]) #longitude
            value_temp[1] = float(value_temp[1]) #latitude
            value_temp[2] = float(value_temp[2])

            count = 1
            longitude = value_temp[0]
            latitude = value_temp[1]

            for read_value in read_values[2:]:
                data = read_value.split(',')
                check_time = data[0:6]
                value = data[7:10]
                value.append(0)
                value[0] = float(value[0]) #longitude
                value[1] = float(value[1]) #latitude
                value[2] = float(value[2])

                if check_time == check_time_temp:
                    for i, v in enumerate(value):
                        value_temp[i] = value_temp[i] + v
                    count = count + 1
                    value_temp[3] = self.measure(latitude, longitude, value_temp[1]/count, value_temp[0]/count)
                    longitude = value_temp[0]/count
                    latitude = value_temp[1]/count
                else:
                    for time_idx, time_string in enumerate(check_time_temp[:6]):
                        if time_idx == 0:
                            file_to_write.write(time_string)
                        else:
                            file_to_write.write(','+time_string)
                    value_temp[0] = str(value_temp[0])
                    value_temp[1] = str(value_temp[1])
                    value_temp[2] = str(value_temp[2])
                    value_temp[3] = str(value_temp[3])

                    for value_string in value_temp:
                        file_to_write.write(',' + value_string)
                    file_to_write.write('\n')

                    value_temp[0] = float(value_temp[0]) / count #longitude
                    value_temp[1] = float(value_temp[1]) / count #latitude
                    value_temp[2] = float(value_temp[2]) / count
                    value_temp[3] = self.measure(latitude,longitude,value_temp[1],value_temp[0])

                    check_time_temp = check_time
                    value_temp = value
                    count = 1
                    longitude = value_temp[0]
                    latitude =  value_temp[1]

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


root_csv = 'data/2. data_csv_format/'
root_summarized = 'data/3. data_csv_second_average/'
name_of_dir = '드래곤즈 0617/'
Extract_data()
extractObject = Extract_data()
extractObject.summarize_csv(root_csv + name_of_dir, root_summarized + name_of_dir)
