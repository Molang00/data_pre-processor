
import module.converter.converter_module as convertModule

# argv를 이용해 필요한 dir명을 전달받아 이용하면 유용할 것
need_to_convert_dir = '드래곤즈 0617'
convertObject = convertModule.Converter()

# .och에서 .csv로의 변환을 원하는 경우
root_och_to_read = 'data/1. data_och_format/'
root_csv_to_write = 'data/2. data_csv_format/'
convertObject.convert_och_to_csv(convertObject, root_och_to_read, root_csv_to_write, need_to_convert_dir)


import module.extract_data.extract_data_module as extractModule

root_csv = 'data/2. data_csv_format/'
root_summarized = 'data/3. data_csv_second_average/'
name_of_dir = '드래곤즈 0617/'

extractObject = extractModule.extract_data()
extractObject.create_dir(root_summarized+name_of_dir)
print("A")
extractObject.summarize_csv(root_csv + name_of_dir+'*.csv', root_summarized + name_of_dir)
print("B")

