from model.fetch_files.ftp_model import Ftp_model


class Fetch_files:

    def download_recent_file(self, path_destination_folder = "data/0. data_gp_format", address_ftp_list = [("fitogether.co", 50021, "kleaguejunior2018", "junior2018")], access_date=0):


        object_ftp_model = Ftp_model()
        object_ftp_model.make_ftp_list(address_ftp_list)
        for i in range(len(object_ftp_model.ftp_list)):
            ftp = object_ftp_model.ftp_list[i]
            category = address_ftp_list[i][3]
            object_ftp_model.download_new_Files(ftp, access_date=access_date, category=category,
                                                path_destination_folder=path_destination_folder)

        object_ftp_model.remove_ftp_list()





