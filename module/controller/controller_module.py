
from module.converter.converter_module import Converter
from module.editdata.editdata_module import EditData
from module.extract_data.extract_data_module import Extract_data
from module.findnoise.findnoise_module import NoiseFinder
from helper.find_field_csv import Find_field_csv
import os


class Controller:

    def convert_process(self, path_root_folder_input, path_root_folder_output, name_folder, process_type="och_to_csv"):
        '''
            :param path_root_folder_input:  string,     'data/2. data_csv_format’,     데이터를 처리할 폴더가 담겨있는 root 경로
            :param path_root_folder_output: string,     'data/5.data_error_removed’,   결과를 출력할 폴더가 담길 root 경로
            :param name_folder:             string,     '드래곤즈 0617’,               처리할 폴더 명
            :param process_type:            string,     'och_to_csv'    ,               처리 타입 default가 och to csv 변환
            :return: None
        '''

        object_converter= Converter()
        if process_type == "och_to_csv":
            object_converter.convert_och_to_csv(path_root_folder_input, path_root_folder_output,
                                                name_of_dir=name_folder)
        else:
            object_converter.convert_csv_to_och(path_root_folder_input, path_root_folder_output,
                                                name_of_dir=name_folder)


    def extract_process(self, path_root_folder_input, path_root_folder_output_for_min_average, path_field_info,path_root_folder_output_for_field, name_folder):
        '''
        :param path_root_folder_input:
        :param path_root_folder_output:
        :param name_folder:
        :return:
        '''




        object_extract = Extract_data()
        path_csv_folder = os.path.join(path_root_folder_input,name_folder).replace("\\", "/")
        path_output_folder_for_second_average = os.path.join(path_root_folder_output_for_min_average, name_folder).replace("\\", "/")
        path_output_folder_for_field = os.path.join(path_root_folder_output_for_field, name_folder).replace("\\", "/")


        #object_extract.summarize_csv(path_csv_folder+"/", path_output_folder_for_second_average+"/")

        object_find_field = Find_field_csv()

        object_find_field.find_field_csv_folder(path_csv_folder+"/", path_field_info, path_output_folder_for_field+"/")





    def filter_process(self, path_root_folder_summarized_data, path_read_field_folder, path_root_folder_noise,
                       path_root_folder_to_cut, path_root_folder_for_eddited_files,  name_folder):

        '''
        :param path_root_folder_summarized_data:
        :param path_root_folder_output:
        :param name_folder:
        :return:
        '''


        print("FIND NOISE")
        print(path_root_folder_summarized_data + "\n", path_read_field_folder + "\n", path_root_folder_noise + "\n", name_folder)
        object_noise = NoiseFinder()
        #object_noise.find_noise_in_data(path_root_folder_input, path_read_field_folder, path_root_folder_output1, name_folder)

        print("Edit Data")
        print(path_root_folder_to_cut + "\n",path_root_folder_noise+'\n' , path_root_folder_for_eddited_files + "\n", name_folder)

        #2 30 5
        object_edit = EditData()
        #object_edit.cut_error(path_root_folder_to_cut, path_root_folder_noise, path_root_folder_for_eddited_files, name_folder)




    def manage_token(self, path_root_folder_output, name_folder, process_handled, process_type):
        '''
        :param path_root_folder_output:
        :param name_folder:
        :param process_handled:
        :param process_type:
        :return:
        '''

        pass











