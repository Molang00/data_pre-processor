
from module.converter.converter_module import Converter
from module.editdata.edit_data_module import EditData
from module.extract_data.extract_data_module import Extract_data
from module.findnoise.find_noise_module import NoiseFinder
from helper.find_field_csv import Find_field_csv
from module.write_log.write_log_module import Write_log
from module.fetch_files.fetch_files_module import Fetch_files
from module.inspectdata.inspect_data_module import Inspect_data
from module.rename_file.rename_file_module import Rename_file

import os
import sys
import time

from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import ctypes

##############################
#massage box 띄우는 건 model에 들어갈 예정
###############################
def Mbox(title="알림", text="", style=0):
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)

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

    def __init__(self):
        super().__init__()
        self.setupUi(self) #버튼이름을 가져옴

        self.get_ui()   # 리스트 멤버 변수에 위젯 할당 (관리하기 편하라고)

        self.connect_function_and_widget() #버튼 담당
        self.set_listview("data/0. data_gp_format")  # 리스트 뷰 담당

    #멤버 변수 리스트에 정리해두기
    def get_ui(self):
        self.activity_widget = [self.activity_listview]
        self.button_widget_list = [self.convert_button, self.extract_button, self.filter_button, self.output_button, self.inspect_button,
                                   self.all_process_button, self.refresh_listview_button]
        self.checkbox_list = [
            [self.gp_to_och_checkBox, self.och_to_csv_checkBox],
            [self.min_average_checkBox, self.field_checkBox],
            [self.find_noise_checkBox, self.edit_data_checkBox],
            [self.och__checkBox, self.log_checkBox]
        ]

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

        root_gp =  "data/0. data_gp_format"
        root_och = 'data/1. data_och_format/'
        root_csv = 'data/2. data_csv_format/'
        root_summarized = 'data/3. data_csv_second_average/'
        root_for_editted_file = 'data/5. data_csv_cut_error/'
        root_for_log_excel = 'data/7. data_log_excel/'
        root_for_field = 'data/8. data_field_find/'
        root_for_log = 'data/9. data_log_csv/'
        root_for_noise = 'data/30. data_noise/'
        root_for_inspect = 'data/31. data_inspect/'
        path_statu_player= 'data/40. data_statu_player/'
        root_for_result_och = 'data/100. data_result'
        path_player_num_info = 'helper/1. number_info/'
        path_all_field_info = 'helper/output.csv'

        root_gp = "data/0. data_gp_format"
        root_och = 'data/1. data_och_format/'
        root_csv = 'data/2. data_csv_format/'
        root_summarized = 'data/3. data_csv_second_average/'
        root_for_editted_file = 'data/5. data_csv_cut_error/'
        root_for_log_excel = 'data/7. data_log_excel/'
        root_for_field = 'data/8. data_field_find/'
        root_for_log = 'data/9. data_log_csv/'
        root_for_noise = 'data/30. data_noise/'
        root_for_inspect = 'data/31. data_inspect/'
        path_statu_player = 'data/40. data_statu_player/'
        root_for_result_och = 'data/100. data_result'
        path_player_num_info = 'data/7. data_log_excel/'  # 'helper/1. number_info/'
        path_all_field_info = 'helper/output.csv'

        address_ftp_list = [("175.207.29.99", 50021, "kleaguejunior2018", "junior2018")]
        access_date = 0

        self.button_widget_list[0].clicked.connect(lambda : self.convert_process(root_gp, root_och, root_csv,
                                                                                 path_player_num_info, root_for_log_excel,
                                                                                 self.process_clicked_list,
                                                                                 self.checkbox_list[0][0].isChecked(),self.checkbox_list[0][1].isChecked()
                                                                                 ))
        self.button_widget_list[1].clicked.connect(lambda : self.extract_process(root_csv, root_summarized, path_all_field_info, root_for_field,
                                                                                 self.process_clicked_list,
                                                                                 self.checkbox_list[1][0].isChecked(),self.checkbox_list[1][1].isChecked()
                                                                                 ))
        self.button_widget_list[2].clicked.connect(lambda : self.filter_process(root_summarized, root_for_field, root_for_noise,
                                                                                root_csv, root_for_editted_file,
                                                                                self.process_clicked_list,
                                                                                self.checkbox_list[2][0].isChecked(),self.checkbox_list[2][1].isChecked()
                                                                                ))
        self.button_widget_list[3].clicked.connect(lambda: self.output_process(root_for_result_och, root_for_editted_file,     #och 만드는데 필요한 변수
                                                                               root_summarized, root_for_field, root_for_log,   #로그 만드는데 필요한 변수
                                                                               path_statu_player,
                                                                               self.process_clicked_list,
                                                                               self.checkbox_list[3][0].isChecked(), self.checkbox_list[3][1].isChecked()
                                                                                ))
        self.button_widget_list[4].clicked.connect(lambda: self.inspect_process(root_csv, root_for_log_excel, root_for_log, root_for_inspect,
                                                                                self.process_clicked_list
                                                                                ))
        self.button_widget_list[5].clicked.connect(lambda: self.all_process())

        self.button_widget_list[6].clicked.connect(lambda: self.fetch_process(root_gp, address_ftp_list, access_date))

    def convert_process(self, path_root_folder_gp, path_root_folder_och, path_root_folder_csv, path_root_num_info,
                        root_for_log, name_folder_list, is_gp_to_och=True, is_och_to_csv=True):

        try:
            for name_folder in name_folder_list:
                print(name_folder)
                if is_gp_to_och:
                    print("Gp_to_och_START")
                    object_converter = Converter()
                    object_converter.convert_gp_to_och(path_root_folder_gp, path_root_folder_och,
                                                       name_of_dir=name_folder)
                    print("Gp_to_och_END")
                if is_och_to_csv:
                    print("Och_to_csv_START")
                    object_converter = Converter()
                    object_converter.convert_och_to_csv(path_root_folder_och, path_root_folder_csv,
                                                        name_of_dir=name_folder)
                    object_rename = Rename_file()
                    object_rename.rename_csv_file(path_root_folder_csv, path_root_num_info, root_for_log, name_of_dir=name_folder)
                    print("Och_to_csv_END")
        except Exception as e:
            print(e)

    def extract_process(self, path_root_folder_input, path_root_folder_for_min_average, path_field_info, path_root_folder_for_field,
                        name_folder_list,
                        is_min_average=True, is_field=True):

        try:
            for name_folder in name_folder_list:
                print(name_folder)
                path_csv_folder = os.path.join(path_root_folder_input,name_folder).replace("\\", "/")
                path_output_folder_for_second_average = os.path.join(path_root_folder_for_min_average, name_folder).replace("\\", "/")
                path_output_folder_for_field = os.path.join(path_root_folder_for_field, name_folder).replace("\\", "/")

                if is_min_average:
                    print("Min_average_START")
                    object_extract = Extract_data()
                    object_extract.summarize_csv(path_csv_folder+"/", path_output_folder_for_second_average+"/")
                    print("Min_average_END")

                if is_field:
                    print("Field_find_START")
                    object_find_field = Find_field_csv()
                    object_find_field.find_field_csv_folder(path_csv_folder, path_field_info, path_output_folder_for_field)
                    print("Field_find_END")
        except Exception as e:
            print(e)

    def filter_process(self, path_root_folder_summarized_data, path_read_field_folder, path_root_folder_noise,
                       path_root_folder_to_cut, path_root_folder_for_eddited_files,
                       name_folder_list,
                       is_find_noise = True, is_edit_data = True):


        for name_folder in name_folder_list:
            if is_find_noise:
                print("FIND_NOISE_START")
                object_noise = NoiseFinder()
                object_noise.find_noise_in_data(path_root_folder_summarized_data, path_read_field_folder, path_root_folder_noise, name_folder)
                print("FIND_NOISE_END")

            if is_edit_data:
                print("Edit_Data_START")
                object_edit = EditData()
                object_edit.cut_error(path_root_folder_to_cut, path_root_folder_noise, path_root_folder_for_eddited_files, name_folder)
                print("Edit_Data_END")

    def output_process(self, path_root_folder_processed_och, path_root_folder_processed_csv,                    #och 만드는데 필요한 변수
                       path_root_folder_for_min_average, path_root_folder_for_field, path_root_folder_for_log,       #로그 만드는데 필요한 변수
                       path_write_statu_player,
                       name_folder_list,
                       is_och =True, is_log = True
                       ):
        try:
            for name_folder in name_folder_list:
                if is_och:
                    print("OUTPUT_OCH_START")
                    object_converter = Converter()
                    object_converter.convert_csv_to_och(path_root_folder_processed_csv,path_root_folder_processed_och,name_folder)
                    print("OUTPUT_OCH_END")

                if is_log:
                    print("OUTPUT_LOG_START")
                    Write_log()
                    Object_write_log = Write_log()
                    Object_write_log.detect_playing(path_root_folder_for_min_average, path_root_folder_for_field,
                                                    path_root_folder_for_log, path_write_statu_player, name_folder)
                    print("OUTPUT_LOG_END")
        except Exception as e:
            print(e)

    def inspect_process(self, root_csv, root_for_log_excel, root_for_log, root_for_inspect,
                       name_folder_list
                       ):
        try:
            for name_folder in name_folder_list:
                print("Inspect_data_START")
                object_inspect = Inspect_data()
                object_inspect.do_inspection(root_for_log_excel, root_for_log, root_csv, root_for_inspect, name_folder)
                print("Inspect_data_END")
        except Exception as e:
            print(e)

    def fetch_process(self, path_destination_folder = "data/0. data_gp_format", address_ftp_list = [("175.207.29.99", 50021, "kleaguejunior2018", "junior2018")], access_date=0):

        object_fetch_files = Fetch_files()
        object_fetch_files.download_recent_file(path_destination_folder=path_destination_folder,address_ftp_list=address_ftp_list,access_date=access_date)

        self.set_listview(path_destination_folder)  # 리스트 뷰 담당
  
        Mbox("fetch", "다운로드 완료", 0)

    def all_process(self):
        print("all process start")
        # 시작시간 (프로세스 시간 측정용)
        start_time = time.time()

        root_gp = "data/0. data_gp_format"
        root_och = 'data/1. data_och_format/'
        root_csv = 'data/2. data_csv_format/'
        root_summarized = 'data/3. data_csv_second_average/'
        root_for_editted_file = 'data/5. data_csv_cut_error/'
        root_for_log_excel = 'data/7. data_log_excel/'
        root_for_field = 'data/8. data_field_find/'
        root_for_log = 'data/9. data_log_csv/'
        root_for_noise = 'data/30. data_noise/'
        root_for_inspect = 'data/31. data_inspect/'
        path_statu_player= 'data/40. data_statu_player/'
        root_for_result_och = 'data/100. data_result'
        path_player_num_info = 'data/7. data_log_excel/' #'helper/1. number_info/'
        path_all_field_info = 'helper/output.csv'

        self.convert_process(root_gp, root_och, root_csv,
                             path_player_num_info, root_for_log_excel,
                             self.process_clicked_list,
                             self.checkbox_list[0][0].isChecked(),
                             self.checkbox_list[0][1].isChecked()
                             )
        self.extract_process(root_csv, root_summarized, path_all_field_info, root_for_field,
                                         self.process_clicked_list,
                                         self.checkbox_list[1][0].isChecked(), self.checkbox_list[1][1].isChecked()
                                         )
        self.filter_process(root_summarized, root_for_field, root_for_noise,
                                        root_csv, root_for_editted_file,
                                        self.process_clicked_list,
                                        self.checkbox_list[2][0].isChecked(), self.checkbox_list[2][1].isChecked()
                                        )
        self.output_process(root_for_result_och, root_for_editted_file,  # och 만드는데 필요한 변수
                            root_summarized, root_for_field, root_for_log,  # 로그 만드는데 필요한 변수
                            path_statu_player,
                            self.process_clicked_list,
                            self.checkbox_list[3][0].isChecked(), self.checkbox_list[3][1].isChecked()
                            )
        self. inspect_process(root_csv, root_for_log_excel, root_for_log, root_for_inspect,
                              self.process_clicked_list
                              )

        print("all process end\n")
        print("--- %s seconds ---" % (time.time() - start_time))
        Mbox("All Process", "처리 완료", 0)

    def manage_token(self, path_root_folder_output, name_folder, process_handled, process_type):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = Controller()
    myWindow.show()
    app.exec_()











