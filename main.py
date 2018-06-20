import module.extract_data.extract_data_module as extractModule

root_csv = 'data/2. data_csv_format/'
root_summarized = 'data/3. data_csv_second_average/'
name_of_dir = '드래곤즈 0617/'

extractObject = extractModule.extract_data()
extractObject.create_dir(root_summarized+name_of_dir)
print("A")
extractObject.summarize_csv(root_csv + name_of_dir+'*.csv', root_summarized + name_of_dir)
print("B")