import os

# dir를 생성
def create_dir(self, directory):
    # directory dir명이 포함된 path가 string으로 저장
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print('Error: Creating directory. ' + directory)


def check_slash(self, path_string):
    # path_string 원하는 경로를 string으로 저장

    # path의 마지막 경로에 /혹은 \가 없다면 /를 추가하여 return
    if path_string[len(path_string) - 1] != '/' and path_string[len(path_string) - 1] != '\\':
        path_string = path_string + '/'
    return path_string
