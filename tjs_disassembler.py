import argparse
import os
import sys
import PyQt5
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QCoreApplication
from dissemble.ui import DisassemblyViewer

def main():
    
    parser = argparse.ArgumentParser(description='反汇编二进制格式tjs脚本')
    parser.add_argument('path', help='文件夹路径', nargs='?', default=None)
    
    args = parser.parse_args()
    base = os.path.dirname(PyQt5.__file__)
    plugin_path = os.path.join(base, "Qt5", "plugins")

    QCoreApplication.addLibraryPath(plugin_path)

    # 创建GUI应用
    app = QApplication(sys.argv)
    viewer = DisassemblyViewer()
    viewer.show()
    
    # 设置默认目录为当前脚本运行目录
    curdir = None

    if args.path != None:
        curdir = os.path.abspath(args.path)
    else:
        curdir = os.path.dirname(os.path.abspath(__file__))

    viewer.set_current_directory(curdir)
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()