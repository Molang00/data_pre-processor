import glob
import os
import locale
class extract_data:

    # noinspection PyMethodMayBeStatic
    def create_dir(self, directory):
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except OSError:
            print('Error: Creating directory.'+directory)

    # noinspection PyMethodMayBeStatic
    def summarize_csv(self, path_csv, path_summarized):
        files_csv = glob.glob(path_csv)
        write_order = 'year,month,day,hour,minute,second,longitude,latitude,speed'

        for file_csv in files_csv:
            file_summarized = path_summarized + file_csv[len(path_csv)-5:]
            file_summarized = file_summarized[:len(file_summarized)-3]+'csv'

            file_to_read = open(file_csv,'r')
            file_to_write = open(file_summarized,'w')
            file_to_write.writelines(write_order+'\n')

            read_values = file_to_read.readlines()
            data = read_values[1].split(',')
            check_time_temp = data[0:6]
            value_temp = data[7:10]
            value_temp[0]=float(value_temp[0])
            value_temp[1] = float(value_temp[1])
            value_temp[2] = float(value_temp[2])
            count = 1
            for read_value in read_values[2:]:
                data = read_value.split(',')
                check_time = data[0:6]
                value = data[7:10]
                value[0] = float(value[0])
                value[1] = float(value[1])
                value[2] = float(value[2])
                if check_time == check_time_temp:
                    for i, v in enumerate(value):
                        value_temp[i] = value_temp[i] + v
                    count = count + 1
                else:
                    for time_idx, time_string in enumerate(check_time_temp[:6]):
                        if time_idx == 0:
                            file_to_write.write(time_string)
                        else:
                            file_to_write.write(','+time_string)
                    value_temp[0] = value_temp[0] / count
                    value_temp[1] = value_temp[1] / count
                    value_temp[2] = value_temp[2] / count
                    value_temp[0] = str(value_temp[0])
                    value_temp[1] = str(value_temp[1])
                    value_temp[2] = str(value_temp[2])

                    for value_string in value_temp:
                        file_to_write.write(',' + value_string)
                    check_time_temp = check_time
                    value_temp = value
                    count = 1
                    file_to_write.write('\n')

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

            for value_string in value_temp:
                file_to_write.write(',' + value_string)
            file_to_write.write('\n')
            file_to_read.close()

if __name__ == "__main__":
    root_csv = 'data/2. data_csv_format/'
    root_summarized = 'data/3. data_csv_second_average/'
    name_of_dir = '드래곤즈 0617/'

    extractObject = extract_data()
    extractObject.create_dir(root_summarized+name_of_dir)
    print("A")
    extractObject.summarize_csv(root_csv + name_of_dir+'*.csv', root_summarized + name_of_dir)
    print("B")
    '''
        
    
    '''
