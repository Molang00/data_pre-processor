


import ftplib
import os


class Ftp_model:

    ftp_list = []

    def get_access_date(self):

        access_date = ""
        if not os.path.exists("data/date.txt"):
            if not os.path.exists("data"):
                os.mkdir("data")
            with open("data/date.txt", "w+", encoding='utf8') as f:
                f.write("20180703044456") # 20180710 13시 45분
        else:
            with open("data/date.txt", "r", encoding='utf8') as f:
                access_date = int(f.readline().rstrip())

        print("access_date: ", access_date)
        return access_date

    def update_access_date(self, time_diff = 9):
        from datetime import datetime, timedelta
        date = datetime
        # ftp에서 MTDT를 할경우 9시간 당겨져서 오기 때문에 updateDate를 맞춰줌
        updateDate = (date.now() - timedelta(hours=time_diff)).strftime("%Y%m%d%H%M%S")
        print("updateDate", updateDate)

        with open("data/date.txt", "w+", encoding='utf8') as f:
            f.write(updateDate)

    def make_ftp_list(self, address_ftp_list, start_directory = "data"):
        tmp_ftp_list = []
        for address_ftp in address_ftp_list:
            ftp = ftplib.FTP()
            ftp.connect(address_ftp[0],address_ftp[1])
            ftp.login(address_ftp[2],address_ftp[3])
            ftp.cwd(start_directory)
            tmp_ftp_list.append(ftp)
        self.ftp_list = tmp_ftp_list

    def remove_ftp_list(self):
        for ftp in self.ftp_list:
            ftp.close()
        self.ftp_list = []

    def download_new_Files(self, ftp, access_date = 0, category="junior", path_destination_folder="C:/Users/fitogether/Documents/AuFe/8. temp"):
        if access_date == 0:
            access_date = self.get_access_date()
            self.update_access_date()

        dirs = ftp.nlst() #디렉토리만 있어야함

        print(dirs)
        print("access_date {}".format(access_date))

        for dir in dirs:

            self.download_folder(ftp, name_folder=dir, category=category, path_destination_folder=path_destination_folder,
                                 isGP=True, access_date=access_date)

    def download_folder(self, ftp, name_folder, category="tester", path_destination_folder="", isGP=True, access_date=0):

        destination_directory = os.path.join(path_destination_folder, name_folder).replace("\\", "/")
        parsed_name = self.parse_name(name_folder)

        path_files = ftp.nlst(name_folder)

        if isGP:
            gp_files_path = [e for e in path_files if
                             e.endswith(".gp") and int(ftp.sendcmd("MDTM " + e).split(" ")[1]) >= access_date]
            path_files = gp_files_path

        if len(path_files) != 0:
            print(category + "\n" + name_folder + "에서 파일 다운을 합니다")
        else:
            # 새로운 파일을 받지 않는 경우 종료
            return

        for path_file in path_files:
            path_destination_file = os.path.join(path_destination_folder, path_file.replace(name_folder, parsed_name))
            root, filename = os.path.split(path_destination_file)

            if not os.path.exists(root):
                os.makedirs(root)

            with open(path_destination_file, 'wb') as f:
                try:
                    ftp.retrbinary("RETR " + path_file, f.write)
                except Exception as e:
                    print(e)

    def parse_name(self, name):

        team_name_list = ["강원", "경남", "광주", "대구", "대전", "부산", "부천", "상주", "서울", "서울E", "성남", "수원", "수원F", "아산", "안산",
                          "안양", "울산", "인천", "전남", "전북", "제주", "포항"]

        ftp_name_list = ['ê°\x95ì\x9b\x90', 'ê²½ë\x82¨', 'ê´\x91ì£¼', 'ë\x8c\x80êµ¬', 'ë\x8c\x80ì\xa0\x84', 'ë¶\x80ì\x82°', 'ë¶\x80ì²\x9c', 'ì\x83\x81ì£¼', 'ì\x84\x9cì\x9a¸', 'ì\x84\x9cì\x9a¸E', 'ì\x84±ë\x82¨', 'ì\x88\x98ì\x9b\x90', 'ì\x88\x98ì\x9b\x90F', 'ì\x95\x84ì\x82°', 'ì\x95\x88ì\x82°', 'ì\x95\x88ì\x96\x91', 'ì\x9a¸ì\x82°', 'ì\x9d¸ì²\x9c', 'ì\xa0\x84ë\x82¨', 'ì\xa0\x84ë¶\x81', 'ì\xa0\x9cì£¼', 'í\x8f¬í\x95\xad']

        tmp_len_name = len(name)
        for i in range(len(ftp_name_list)):
            name = name.replace(ftp_name_list[i], team_name_list[i])

            if not tmp_len_name == len(name):
                print("이름 변경", ftp_name_list[i], team_name_list[i])
                break

        return  name


if __name__=="__main__":
    object_ftp = Ftp_model()
    address_ftp_list = [("175.207.29.99", 50021, "kleaguejunior2018", "junior2018")]
    object_ftp = Ftp_model()
    object_ftp.make_ftp_list(address_ftp_list)
    object_ftp.download_new_Files(object_ftp.ftp_list[0], category="junior", path_destination_folder="C:/Users/fitogether/Documents/AuFe/8. temp")
    object_ftp.remove_ftp_list()




