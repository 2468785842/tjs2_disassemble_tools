from typing import List
import os
from PyQt5.QtWidgets import (QMainWindow, QTreeWidget, QTreeView,
                             QTreeWidgetItem, QSplitter, QVBoxLayout, QFileSystemModel,
                             QWidget, QHeaderView, QLineEdit,QGroupBox, QFormLayout, QComboBox,
                             QLabel, QHBoxLayout, QFileDialog, QMessageBox, QPushButton)
from PyQt5.QtCore import Qt, QDir, QModelIndex
from PyQt5.QtGui import QFont

from .tjs_entity import TJSInterCodeContext

from .tjs_disassembler import TJSDisassembler
from .tjs_bytecode_loader import TJSByteCodeLoader

class DisassemblyViewer(QMainWindow):
    disassembler: TJSDisassembler
    objects: List[TJSInterCodeContext]

    def __init__(self):
        super().__init__()
        self.current_file = None
        self.disassembler = None
        self.top_obj = None
        self.objects = []
        self.data_area = None
        self.current_obj_index = 0
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('TJS Bytecode Disassembler')
        self.setGeometry(100, 100, 1400, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # 左侧文件列表和搜索
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # 搜索框
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search files...")
        self.search_edit.textChanged.connect(self.filter_files)
        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_edit)
        left_layout.addLayout(search_layout)
        
        # 使用树状视图显示文件系统
        self.file_system_model = QFileSystemModel()
        self.file_system_model.setRootPath(QDir.currentPath())
        self.file_system_model.setNameFilterDisables(False)
        self.file_system_model.setFilter(QDir.Filter.AllDirs | QDir.Filter.Files | QDir.Filter.NoDotAndDotDot)
        
        self.file_tree = QTreeView()
        self.file_tree.setModel(self.file_system_model)
        self.file_tree.setRootIndex(self.file_system_model.index(QDir.currentPath()))
        self.file_tree.setColumnWidth(0, 250)  # 设置第一列宽度
        self.file_tree.doubleClicked.connect(self.on_file_double_clicked)
        self.file_tree.setSortingEnabled(True)
        
        # 隐藏不需要的列
        self.file_tree.hideColumn(1)  # 隐藏大小列
        self.file_tree.hideColumn(2)  # 隐藏类型列
        self.file_tree.hideColumn(3)  # 隐藏修改日期列
        
        left_layout.addWidget(self.file_tree)
        
        # 添加打开文件夹按钮
        open_button_layout = QHBoxLayout()
        self.open_folder_btn = QPushButton("Open Folder")
        self.open_folder_btn.clicked.connect(self.open_folder)
        open_button_layout.addWidget(self.open_folder_btn)
        left_layout.addLayout(open_button_layout)
        
        # 右侧反汇编显示
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # 文件信息标签
        self.file_info_label = QLabel("No file loaded")
        right_layout.addWidget(self.file_info_label)
        
        # 对象选择区域
        obj_group = QGroupBox("Object Selection")
        obj_layout = QFormLayout(obj_group)
        
        # 1️⃣ 添加搜索框
        self.obj_search_edit = QLineEdit()
        self.obj_search_edit.setPlaceholderText("Search String in objects...")
        self.obj_search_edit.textChanged.connect(self.filter_objects)  # 搜索回调
        obj_layout.addRow("Search String:", self.obj_search_edit)

        self.obj_combo = QComboBox()
        self.obj_combo.currentIndexChanged.connect(self.on_obj_selected)
        obj_layout.addRow("Select Object:", self.obj_combo)
        
        self.obj_info_label = QLabel("No object selected")
        obj_layout.addRow("Object Info:", self.obj_info_label)
        
        right_layout.addWidget(obj_group)
        
        # 反汇编树
        self.disassembly_tree = QTreeWidget()
        self.disassembly_tree.setHeaderLabels(['Address', 'Opcode', 'Operands', 'Comment'])
        self.disassembly_tree.header().setSectionResizeMode(QHeaderView.Interactive)
        right_layout.addWidget(self.disassembly_tree)
        
        # 添加分割器
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 1100])
        main_layout.addWidget(splitter)
        
        # 设置字体
        font = QFont("Courier New", 10)
        self.disassembly_tree.setFont(font)
  
    def set_current_directory(self, directory):
        """设置当前目录并更新文件树"""
        if os.path.isdir(directory):
            self.file_tree.setRootIndex(self.file_system_model.index(directory))
    
    def open_folder(self):
        """打开文件夹并更新文件树"""
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder", QDir.currentPath())
        if folder_path:
            self.set_current_directory(folder_path)
    
    def on_file_double_clicked(self, index: QModelIndex):
        """处理文件树中的双击事件"""
        file_path = self.file_system_model.filePath(index)
        if os.path.isfile(file_path):
            self.load_file(file_path)
    
    def filter_files(self):
        """根据搜索框内容过滤文件 - 这里简化处理，实际可能需要更复杂的过滤逻辑"""
        search_text = self.search_edit.text().lower()
        
        # 这里简化处理，实际可能需要实现更复杂的文件过滤逻辑
        # 可以通过设置文件名过滤器来实现更精确的过滤
        if search_text:
            self.file_system_model.setNameFilters([f"*{search_text}*"])
        else:
            self.file_system_model.setNameFilters([])
    
    def load_file(self, file_path):
        """加载选定的文件"""
        # 加载字节码
        result = TJSByteCodeLoader.load_bytecode(file_path)
        
        if result is None:
            QMessageBox.warning(self, "Invalid File", 
                               f"The file '{os.path.basename(file_path)}' is not a valid TJS2 bytecode file.")
            return
        
        self.top_obj, self.objects, self.data_area = result
        self.current_file = file_path
        
        # 更新文件信息
        file_name = os.path.basename(file_path)
        obj_count = len(self.objects) if self.objects else 0
        self.file_info_label.setText(f"File: {file_name} | Objects: {obj_count}")
        
        # 更新对象选择下拉框
        self.obj_combo.clear()
        for i, obj in enumerate(self.objects):
            obj_name = obj.name if hasattr(obj, 'name') and obj.name else f"Object_{i}"
            obj_type = obj.context_type.name if hasattr(obj, 'context_type') else "Unknown"
            self.obj_combo.addItem(f"{obj_name} ({obj_type})", i)
        
        # 创建反汇编器
        self.disassembler = TJSDisassembler(self.top_obj, self.objects, self.data_area)
        
        # 默认显示第一个对象
        if self.objects:
            self.obj_combo.setCurrentIndex(0)
            self.on_obj_selected(0)
    
    def on_obj_selected(self, index):
        """处理对象选择变化"""
        self.disassembly_tree.clear()
        obj_index = self.obj_combo.itemData(index)
        if obj_index is None or obj_index >= len(self.objects):
            return
            
        self.current_obj_index = obj_index
        obj = self.objects[obj_index]

        # 更新对象信息
        obj_info = f"Name: {obj.name if hasattr(obj, 'name') else 'Unknown'}\n"
        obj_info += f"Type: {obj.context_type.name if hasattr(obj, 'context_type') else 'Unknown'}\n"
        obj_info += f"Code Size: {len(obj.code) if hasattr(obj, 'code') else 0} instructions\n"
        obj_info += f"Data Count: {len(obj.data) if hasattr(obj, 'data') else 0} items\n"
        obj_info += f"Variables: Max {obj.max_variable_count if hasattr(obj, 'max_variable_count') else 0}, "
        obj_info += f"Reserved {obj.variable_reserve_count if hasattr(obj, 'variable_reserve_count') else 0}"
        
        self.obj_info_label.setText(obj_info)
        
        # 显示反汇编结果
        self.display_disassembly(obj_index)
    
    def display_disassembly(self, obj_index: int):
        """显示指定对象的反汇编结果"""
        if self.disassembler is None or obj_index >= len(self.objects):
            return
            
        instructions = self.disassembler.disassemble(obj_index)
        
        for instr in instructions:
            item = QTreeWidgetItem([
                f"0x{instr.address:04X}",
                instr.opcode,
                instr.operands,
                f"; {instr.comment}"
            ])
            self.disassembly_tree.addTopLevelItem(item)
            
        # 展开所有项
        self.disassembly_tree.expandAll()
        
        # 调整列宽以适应内容
        for i in range(self.disassembly_tree.columnCount()):
            self.disassembly_tree.resizeColumnToContents(i)
    
    def filter_objects(self):
        """根据搜索框内容过滤对象，下拉框只显示匹配的对象"""
        search_text = self.obj_search_edit.text().lower()

        if search_text == "":
            # 更新对象选择下拉框
            self.obj_combo.clear()
            for i, obj in enumerate(self.objects):
                obj_name = obj.name if hasattr(obj, 'name') and obj.name else f"Object_{i}"
                obj_type = obj.context_type.name if hasattr(obj, 'context_type') else "Unknown"
                self.obj_combo.addItem(f"{obj_name} ({obj_type})", i)
            return
        
        # 先清空下拉框
        self.obj_combo.clear()
        
        if not self.objects:
            return
        
        for i, obj in enumerate(self.objects):
            match = False
            for v in obj.data:
                if type(v) is str and v == search_text: # 目前只支持字符串
                    match = True
                    break
            
            if match:
                obj_name = getattr(obj, 'name', f"Object_{i}")
                obj_type = getattr(getattr(obj, 'context_type', None), 'name', 'Unknown')
                self.obj_combo.addItem(f"{obj_name} ({obj_type})", i)
        
        # 如果有匹配，默认选择第一个
        if self.obj_combo.count() > 0:
            self.obj_combo.setCurrentIndex(0)
            self.on_obj_selected(0)
        else:
            self.obj_info_label.setText("No object selected")
            self.disassembly_tree.clear()
