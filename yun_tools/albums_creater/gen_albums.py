import glob
import time
import random
from pathlib import Path

exclude_dir = ['.git', '.idea', '.txt']
exclude_file = ['txt', 'py', 'gitignore']  # 以"."开头的文件先去掉"."


class Tree(object):
    def __init__(self, albums_path, cdnUrl):
        self.albums = albums_path
        self.cdn = cdnUrl

        self.tree(albums_path)  # 生成文件树

    def is_not_txt(self, file):
        sp = file.split(".")
        if sp[-1] not in exclude_file:
            return 1

    def write(self, file_list, path):
        name = '&'.join(str(file_list[0]).split('\\')[-3:-1])
        repo = self.cdn.split("/")[-1].split("@")[0]
        t = str(path).replace('\\', '/').split("/")
        print(name)
        with open('{}/{}.txt'.format(self.albums, name), mode='w') as f:
            for img in file_list:
                caption = str(img).split("\\")[-1]
                src = "/".join([self.cdn] + t[t.index(repo) + 1:] + [caption])
                f.writelines("  - caption: " + caption + '\n')
                f.writelines("    src: " + src + '\n')

    def tree(self, dir_name):
        path = Path(dir_name)

        path_list = [dir for dir in path.iterdir() if dir.is_dir()]  # 一个文件夹为一个相册
        file_list = [dir for dir in path.iterdir() if dir.is_file() and self.is_not_txt(str(dir))]

        if file_list:
            self.write(file_list, path)

        if path_list:
            for path in path_list:
                if path.name not in exclude_dir:
                    self.tree(path)


class Update(object):
    def __init__(self, albums_path, source_path):
        self.source_path = source_path
        try:
            self.albums_dict = self.read_txt(albums_path)  # 先读取配置
        except Exception:
            raise IOError("未找到BOM，请先生成!")

        self.update_albums(self.albums_dict, self.source_path)

    def read_txt(self, albums_path):  # 从txt读取文件配置
        albums_dict = {}
        txt_list = glob.glob(albums_path + "/" + "*.txt")
        albums_txt = [txt for txt in txt_list if txt.split("\\")[-1].split("&")[0] == "albums"]
        for file in albums_txt:
            with open(file, 'r') as f:
                albums_dict[file.split("&")[-1].split(".")[0]] = f.readlines()
        return albums_dict

    def create_albums(self, albums_dict, album, title=None, passwd=None,
                      cover="https://cdn.jsdelivr.net/gh/Sknp1006/cdn/img/avatar/none.jpg", desc=None):  # 创建新相册
        """
        创建相册流程:
          1) 新建[album_name].md文件
          2) 查看并保存index.md文件
          3) 更新index.md文件
        :param albums_dict:  相册字典
        :param album:  相册名(默认文件名)
        :param title:  标题(默认文件名)
        :param passwd:  密码
        :param cover:  封面(默认阿卡林)
        :param desc:  相册描述
        :return:
        """
        print("creating {}".format(album))
        md = "/".join([self.source_path, "{}.md".format(album)])  # 新建的md文件路径
        with open(md, 'w+', encoding='utf-8') as f:
            f.write('---\n')
            if title:
                f.write('title: {}\n'.format(title))  # title默认文件夹名
            else:
                f.write('title: {}\n'.format(album))
            f.write('date: {}\n'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))  # date会覆盖原来开的时间
            f.write('layout: gallery\n')
            if passwd:
                f.write('password: {}\n'.format(passwd))  # 设置密码
            f.write('photos:\n')
            f.writelines(albums_dict[album])
            f.write('---\n')
        with open("/".join([self.source_path, 'index.md']), 'r', encoding='utf-8') as f:  # 读取原来的index.md
            txt = f.readlines()[:-1]
        with open("/".join([self.source_path, 'index.md']), 'w', encoding='utf-8') as f:  # 在index.md添加新album
            f.writelines(txt)
            f.write('  - caption: {}\n'.format(title))
            f.write('    url: /albums/{}.html\n'.format(album))
            f.write('    cover: {}\n'.format(cover))
            f.write('    desc: {}\n'.format(desc))
            f.write('---\n')


    def update_albums(self, albums_dict, source_path):  # 更新相册
        for album in albums_dict:
            md = "\\".join([source_path, "{}.md".format(album)])  # 对应album的md文件
            if not Path(md).is_file():  # 找不到，则新建一个相册
                cover = random.choice(albums_dict[album][1::2]).strip()[5:]  # 随机选取封面
                self.create_albums(albums_dict, album, cover=cover)
            with open(md, 'w+', encoding='utf-8') as f:  # 追加
                f.write('---\n')
                f.write('title: {}\n'.format(album))
                f.write('date: {}\n'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))
                f.write('layout: gallery\n')
                f.write('photos:\n')
                f.writelines(albums_dict[album])
                f.write('---\n')
            # print("{} updated done!".format(album))

if __name__ == '__main__':
    p = Update(r"C:\Users\SKNP\Documents\GitHub\cdn\img\albums")

