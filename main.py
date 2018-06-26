from module.controller.controller_module import Controller

root_och = 'data/1. data_och_format/'
root_csv = 'data/2. data_csv_format/'
root_summarized = 'data/3. data_csv_second_average/'
root_for_editted_file = 'data/5. data_csv_cut_error/'
root_for_read_field = 'data/8. data_field_find/'
root_for_noise_removed = 'data/30. data_noise/'
root_for_result_och = 'data/100. data_result'


need_to_convert_dir = '드래곤즈 0617'



object_controller = Controller()
object_controller.convert_process(root_och, root_csv, need_to_convert_dir)
object_controller.extract_process(root_csv, root_summarized, need_to_convert_dir)
object_controller.filter_process(root_csv, root_for_read_field, root_summarized,
                                 root_for_editted_file, root_for_noise_removed, need_to_convert_dir)
object_controller.convert_process(root_for_noise_removed, root_for_result_och, need_to_convert_dir,
                                  process_type="csv_to_och")

root_for_read_field = 'data/8. data_field_find/'
root_for_write = 'data/30. data_noise/'


