from module.controller.controller_module import Controller

root_och = 'data/1. data_och_format/'
root_csv = 'data/2. data_csv_format/'
root_summarized = 'data/3. data_csv_second_average/'
need_to_convert_dir = '드래곤즈 0617'

object_controller = Controller()
object_controller.convert_process(root_och, root_csv, need_to_convert_dir)




