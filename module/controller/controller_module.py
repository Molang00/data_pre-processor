
from module.converter.converter_module import Converter
from module.editdata.editdata_module import EditData
from module.extract_data.extract_data_module import Extract_data
from module.findnoise.findnoise_module import NoiseFinder
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
        return



    def extract_process(self, path_root_folder_input, path_root_folder_output, name_folder):
        '''
        :param path_root_folder_input:
        :param path_root_folder_output:
        :param name_folder:
        :return:
        '''
        object_extract = Extract_data()
        path_csv_folder = os.path.join(path_root_folder_input,name_folder).replace("\\", "/")
        path_output_folder = os.path.join(path_root_folder_output,name_folder).replace("\\", "/")
        object_extract.summarize_csv(path_csv_folder, path_output_folder)

        pass

    def filter_process(self,path_root_folder_input, path_read_field_folder, path_root_folder_output1,
                       path_root_for_read_error, path_root_folder_output2, name_folder):
        '''
        :param path_root_folder_input:
        :param path_root_folder_output:
        :param name_folder:
        :return:
        '''
        object_noise = NoiseFinder()
        object_noise.find_noise_in_data(path_read_folder=path_root_folder_input, path_read_field_folder=path_read_field_folder, path_write_folder=path_root_folder_output1, name_of_dir=name_folder)

        object_edit = EditData()
        object_edit.cut_error(path_root_folder_input, path_root_for_read_error,path_root_folder_output2, name_folder)




    def manage_token(self, path_root_folder_output, name_folder, process_handled, process_type):
        '''
        :param path_root_folder_output:
        :param name_folder:
        :param process_handled:
        :param process_type:
        :return:
        '''

        pass











