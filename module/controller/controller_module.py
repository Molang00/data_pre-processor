
from module.converter.converter_module import Converter
from module.editdata.edit_data_module import EditData
from module.extract_data.extract_data_module import Extract_data
from module.findnoise.findnoise_module import NoiseFinder
from helper.find_field_csv import Find_field_csv
import os
import sys

from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import ctypes

##############################
#massage box 띄우는 건 model에 들어갈 예정
###############################
def Mbox(title,text,style):
    return ctypes.windll.user32.MessageBoxW(0, text,title, style)

#리스트형태의 데이터를 comboBox에 넣을 수 있게 변형
class UserModel(QStandardItemModel):
    def __init__(self, data=None, parent=None):
        QStandardItemModel.__init__(self, parent)
        for i, d in enumerate(data):
            self.setItem(i, 0, QStandardItem(d))

    def data(self, QModelIndex, role=None):
        data = self.itemData(QModelIndex)
        if role == Qt.DisplayRole:
            return "%s" % (data[role])
        elif role == Qt.UserRole:
            print(data[role])
        return QVariant()


form_class = uic.loadUiType("module/controller/controller.ui")[0]
class Controller(QMainWindow, form_class):

    process_clicked_list = []
    need_to_convert_dir = "och"


    def __init__(self):
        super().__init__()
        self.setupUi(self) #버튼이름을 가져옴

        self.get_ui()
        
        self.connect_function_and_widget()
        self.set_listview('data/1. data_och_format/')

    #멤버 변수 리스트에 정리해두기
    def get_ui(self):
        self.activity_widget = [self.activity_listview]
        self.button_widget_list = [self.convert_button, self.extract_button, self.filter_button, self.output_button, self.all_process_button]

    def set_listview(self, path_activity_folder):
        activity_list =  os.listdir(path_activity_folder)
        self.item_model = QStandardItemModel(self.activity_widget[0])
        for activity in activity_list:
            item = QStandardItem(activity)
            item.setCheckable(True)
            self.item_model.appendRow(item)
        self.activity_widget[0].setModel(self.item_model)
        self.item_model.itemChanged.connect(self.on_listview_item_changed)


    def on_listview_item_changed(self, item):

        tmp_checked_list = []
        i = 0
        while self.item_model.item(i):
            if self.item_model.item(i).checkState(): #check 되어있으면 2를 리턴 아니면 0
                tmp_checked_list.append(self.item_model.item(i).text())
            i += 1
        self.process_clicked_list = tmp_checked_list

    def connect_function_and_widget(self):

        root_och = 'data/1. data_och_format/'
        root_csv = 'data/2. data_csv_format/'
        root_summarized = 'data/3. data_csv_second_average/'
        root_for_editted_file = 'data/5. data_csv_cut_error/'
        root_for_field = 'data/8. data_field_find/'
        root_for_noise = 'data/30. data_noise/'
        root_for_result_och = 'data/100. data_result'

        path_all_field_info = 'helper/output.csv'

        self.button_widget_list[0].clicked.connect(lambda : self.convert_process(root_och, root_csv, self.process_clicked_list))
        self.button_widget_list[1].clicked.connect(lambda : self.extract_process(root_csv, root_summarized, path_all_field_info, root_for_field,
                                                                        self.process_clicked_list))
        self.button_widget_list[2].clicked.connect(lambda : self.filter_process(root_summarized, root_for_field, root_for_noise,
                                         root_csv, root_for_editted_file, self.process_clicked_list))
        self.button_widget_list[3].clicked.connect(lambda : self.convert_process(root_for_editted_file, root_for_result_och, self.process_clicked_list,
                                          process_type="csv_to_och"))
        arg_list = [root_och, root_csv, self.process_clicked_list,root_csv, root_summarized, path_all_field_info, root_for_field,
                                                                        self.process_clicked_list,root_summarized, root_for_field, root_for_noise,
                                         root_csv, root_for_editted_file, self.process_clicked_list,root_for_editted_file, root_for_result_och, self.process_clicked_list,"csv_to_och"]
        self.button_widget_list[4].clicked.connect(lambda : self.all_process(arg_list))

    def convert_process(self, path_root_folder_input, path_root_folder_output, name_folder_list, process_type="och_to_csv"):
        '''
            :param path_root_folder_input:  string,     'data/2. data_csv_format’,     데이터를 처리할 폴더가 담겨있는 root 경로
            :param path_root_folder_output: string,     'data/5.data_error_removed’,   결과를 출력할 폴더가 담길 root 경로
            :param name_folder_list:             list,       ['드래곤즈 0617’,'och'],            처리할 폴더 명
            :param process_type:            string,     'och_to_csv'    ,               처리 타입 default가 och to csv 변환
            :return: None
        '''

        for name_folder in name_folder_list:
            object_converter= Converter()
            if process_type == "och_to_csv":
                object_converter.convert_och_to_csv(path_root_folder_input, path_root_folder_output,
                                                    name_of_dir=name_folder)
            else:
                object_converter.convert_csv_to_och(path_root_folder_input, path_root_folder_output,
                                                    name_of_dir=name_folder)


    def extract_process(self, path_root_folder_input, path_root_folder_output_for_min_average, path_field_info,path_root_folder_output_for_field, name_folder_list):
        '''
        :param path_root_folder_input:
        :param path_root_folder_output:
        :param name_folder_list:
        :return:
        '''
        for name_folder in name_folder_list:
            path_csv_folder = os.path.join(path_root_folder_input,name_folder).replace("\\", "/")
            path_output_folder_for_second_average = os.path.join(path_root_folder_output_for_min_average, name_folder).replace("\\", "/")
            path_output_folder_for_field = os.path.join(path_root_folder_output_for_field, name_folder).replace("\\", "/")


            object_extract = Extract_data()
            object_extract.summarize_csv(path_csv_folder+"/", path_output_folder_for_second_average+"/")

            object_find_field = Find_field_csv()
            object_find_field.find_field_csv_folder(path_csv_folder+"/", path_field_info, path_output_folder_for_field+"/")



    def filter_process(self, path_root_folder_summarized_data, path_read_field_folder, path_root_folder_noise,
                       path_root_folder_to_cut, path_root_folder_for_eddited_files,  name_folder_list):

        '''
        :param path_root_folder_summarized_data:
        :param path_root_folder_output:
        :param name_folder_list:
        :return:
        '''

        for name_folder in name_folder_list:
            print("FIND NOISE")
            print(path_root_folder_summarized_data + "\n", path_read_field_folder + "\n", path_root_folder_noise + "\n", name_folder)
            object_noise = NoiseFinder()
            object_noise.find_noise_in_data(path_root_folder_summarized_data, path_read_field_folder, path_root_folder_noise, name_folder)

            print("Edit Data")
            print(path_root_folder_to_cut + "\n",path_root_folder_noise+'\n' , path_root_folder_for_eddited_files + "\n", name_folder)

            object_edit = EditData()
            object_edit.cut_error(path_root_folder_to_cut, path_root_folder_noise, path_root_folder_for_eddited_files, name_folder)


    def all_process(self, arg_list):
        print("all process start")
        self.convert_process(arg_list[0],arg_list[1], self.process_clicked_list)
        self.extract_process(arg_list[3],arg_list[4],arg_list[5],arg_list[6], self.process_clicked_list)
        self.filter_process(arg_list[8],arg_list[9],arg_list[10],arg_list[11],arg_list[12], self.process_clicked_list)
        self.convert_process(arg_list[14],arg_list[15], self.process_clicked_list, arg_list[17])
        print("all process end")


    def manage_token(self, path_root_folder_output, name_folder, process_handled, process_type):
        '''
        :param path_root_folder_output:
        :param name_folder:
        :param process_handled:
        :param process_type:
        :return:
        '''

        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = Controller()
    myWindow.show()
    app.exec_()











