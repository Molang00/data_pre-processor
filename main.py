
import time
'''
from module.controller.controller_module import Controller
root_och = 'data/1. data_och_format/'
root_csv = 'data/2. data_csv_format/'
root_summarized = 'data/3. data_csv_second_average/'
root_for_editted_file = 'data/5. data_csv_cut_error/'
root_for_read_field = 'data/8. data_field_find/'
path_to_save_field = 'data/8. data_field_find/'
root_for_noise = 'data/30. data_noise/'
root_for_result_och = 'data/100. data_result'

path_all_field_info = 'helper/output.csv'


#need_to_convert_dir = 'och'
need_to_convert_dir = input("폴더명을 입력하십시오")

start_time = time.time()


object_controller = Controller()
object_controller.convert_process(root_och, root_csv, need_to_convert_dir)
print("--- %s seconds ---" % (time.time() - start_time))
object_controller.extract_process(root_csv, root_summarized, path_all_field_info, path_to_save_field, need_to_convert_dir)
print("--- %s seconds ---" % (time.time() - start_time))
object_controller.filter_process(root_summarized, root_for_read_field, root_for_noise,
                                 root_csv, root_for_editted_file, need_to_convert_dir)
print("--- %s seconds ---" % (time.time() - start_time))
object_controller.convert_process(root_for_editted_file, root_for_result_och, need_to_convert_dir,
                                  process_type="csv_to_och")
print("--- %s seconds ---" % (time.time() - start_time))
'''

from PyQt5.QtWidgets import *
from module.controller.controller_module import Controller
import sys

app = QApplication(sys.argv)
myWindow = Controller()
myWindow.show()
app.exec_()
