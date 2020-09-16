import sys
import os
import requests
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QFileDialog
from PyQt5 import QtGui
from MainWindow import Ui_MainWindow

from gen_albums import Tree, Update


class MainForm(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainForm, self).__init__()
        self.setupUi(self)

        # 连接槽函数
        self.pushButton_source.clicked.connect(self.setSourcePath)
        self.pushButton_albums.clicked.connect(self.setAlbumsPath)

        self.pushButton_gen.clicked.connect(lambda: self.gen_BOM(self.albums_path))  # 生成BOM
        self.pushButton_import.clicked.connect(self.import_albums)  # 导入相册
        self.pushButton_output.clicked.connect(lambda: self.update_albums(self.albums_path, self.source_path))  # 更新相册md

    def setSourcePath(self):
        self.source_path = QFileDialog.getExistingDirectory(self, "选取博客albums目录", "$FileDir$")
        self.lineEdit_source.setText(self.source_path)
        self.outputWritten("博客albums路径: {}\n".format(self.source_path))

    def setAlbumsPath(self):
        self.albums_path = QFileDialog.getExistingDirectory(self, "选取相册图片主目录", "$FileDir$")
        self.lineEdit_albums.setText(self.albums_path)
        self.outputWritten("相册路径: {}\n".format(self.albums_path))

    def outputWritten(self, text):  # 控制台输出
        cursor = self.console.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(str(time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime()) + text))
        self.console.setTextCursor(cursor)
        self.console.ensureCursorVisible()

    def checkParameter(self, text):  # 检查参数是否正确
        if not self.cdnUrl:
            raise ValueError("请先填写cdnUrl!\n")
        cdn_type = text.split("/")[-3]
        if cdn_type == "gh":
            user = text.split("/")[-2]
            repo = text.split("/")[-1].split("@")[0]
            github_url = "/".join(["https://github.com", user, repo])
            try:
                assert str(requests.get(github_url)) == '<Response [200]>'
            except:
                raise ValueError("github仓库 {} 不存在.".format(repo))
            else:
                if repo in self.albums_path.split("/"):
                    self.outputWritten("cdnUrl验证通过!\n")
                else:
                    raise ValueError("albums与cdnUrl不匹配!")

    def gen_BOM(self, albums_path):
        self.cdnUrl = self.lineEdit_cdnUrl.text()
        try:
            self.checkParameter(self.cdnUrl)
        except Exception as e:
            self.outputWritten("配置有误!,{}\n".format(e))
        else:
            self.outputWritten("开始生成BOM...\n")  # 正常生成
            """
            这里是文件树生成器的主程序
            """
            Tree(albums_path, self.cdnUrl)
            self.outputWritten("Done.\n")  # 完成

    def update_albums(self, albums, source):
        self.outputWritten("开始更新md...\n")
        try:
            Update(albums, source)
        except Exception as e:
            self.outputWritten(e)
        self.outputWritten("Done!")

    def import_albums(self):
        txt = QFileDialog.getOpenFileName(self, "选取相册配置文件", './', "*.txt")
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainForm()
    win.show()
    sys.exit(app.exec_())
