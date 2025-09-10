from typing import List, Optional, Tuple

from .tjs_const import *
from .file import *
from .tjs_entity import *

class TJSByteCodeLoader:
    """TJS字节码加载器"""
    
    shortArray: List[int]
    longArray: List[int]
    longLongArray: List[int]
    doubleArray: List[float]
    stringArray: List[str]
    octetArray: List[bytes]

    @staticmethod
    def load_objs_area(stream: BinaryStream, data_area: TJSDataArea) -> Tuple[Optional[TJSInterCodeContext], List[TJSInterCodeContext]]:
        """读取对象（代码上下文）信息"""

        tag = stream.read_int32()
        stream.skip(4) # size

        if tag != OBJ_TAG_LE: None

        # 读取顶层对象索引和对象数量
        top_level = stream.read_int32()
        obj_count = stream.read_int32()
        
        objects: List[TJSInterCodeContext | None] = [None] * obj_count  # 存储所有对象
        work: List[VariantReplace] = []  # 变体替换工作列表
        parents: List[int] = [0] * obj_count  # 父对象索引
        prop_setters: List[int] = [0] * obj_count  # 属性设置器索引
        prop_getters: List[int] = [0] * obj_count  # 属性获取器索引
        super_class_getters: List[int] = [0] * obj_count  # 超类获取器索引
        properties: List[List[int]] = [[] for _ in range(obj_count)]  # 属性列表
        
        # 读取每个对象
        for o in range(obj_count):
            # 检查对象标签
            tag = stream.read_int32()
            if tag != FILE_TAG_LE:
                raise ValueError("ByteCode broken: invalid object tag")
            
            stream.skip(4) # objsize
            
            # 读取对象属性
            parents[o] = stream.read_int32()
            name_idx = stream.read_int32()
            context_type_val = stream.read_int32()
            max_variable_count = stream.read_int32()
            variable_reserve_count = stream.read_int32()
            max_frame_count = stream.read_int32()
            func_decl_arg_count = stream.read_int32()
            func_decl_unnamed_arg_array_base = stream.read_int32()
            func_decl_collapse_base = stream.read_int32()
            prop_setters[o] = stream.read_int32()
            prop_getters[o] = stream.read_int32()
            super_class_getters[o] = stream.read_int32()
            
            # 读取源代码位置信息
            count: int = stream.read_int32()
            source_positions: List[SourcePos] | None = None
            if count > 0:
                # 读取代码位置
                code_positions = [stream.read_int32() for _ in range(count)]
                # 读取源代码位置
                source_positions = [
                    SourcePos(code_positions[i], stream.read_int32()) for i in range(count)
                ]
            else:
                stream.skip(count * 8)  # 跳过源代码位置数据
            
            # 读取代码
            code_size = stream.read_int32()
            code: List[int] = [
                stream.read_uint16() for _ in range(code_size)
            ]
            
            # 对齐到4字节
            if code_size & 1:
                stream.skip(2)
            
            # 读取数据变体
            count = stream.read_int32()
            vcount = count * 2
            data_list = [stream.read_int16() for _ in range(vcount)]
            
            # 创建变体数据
            vdata = [None] * count
            for i in range(count):
                pos = i * 2
                type_val = data_list[pos]
                index = data_list[pos + 1]
                
                if type_val == TYPE_VOID:
                    vdata[i] = None
                elif type_val == TYPE_OBJECT:
                    vdata[i] = None  # 空对象
                elif type_val == TYPE_INTER_OBJECT:
                    work.append(VariantReplace(vdata, i, index))
                elif type_val == TYPE_INTER_GENERATOR:
                    work.append(VariantReplace(vdata, i, index))
                elif type_val == TYPE_STRING:
                    vdata[i] = data_area.string_array[index]
                elif type_val == TYPE_OCTET:
                    vdata[i] = data_area.octet_array[index]
                elif type_val == TYPE_REAL:
                    vdata[i] = data_area.double_array[index]
                elif type_val == TYPE_BYTE:
                    vdata[i] = data_area.byte_array[index]
                elif type_val == TYPE_SHORT:
                    vdata[i] = data_area.short_array[index]
                elif type_val == TYPE_INTEGER:
                    vdata[i] = data_area.long_array[index]
                elif type_val == TYPE_LONG:
                    vdata[i] = data_area.long_long_array[index]
                else:  # TYPE_UNKNOWN or default
                    vdata[i] = None
            
            # 读取超类获取器
            count = stream.read_int32()
            scgetterps = [stream.read_int32() for _ in range(count)]
            
            # 读取属性
            count = stream.read_int32()
            if count > 0:
                pcount = count * 2
                props = [stream.read_int32() for _ in range(pcount)]
                properties[o] = props
            
            # 创建代码上下文对象
            name = data_area.string_array[name_idx] if name_idx < len(data_area.string_array) else f"obj_{o}"
            context_type = TJSContextType(context_type_val)
            
            obj = TJSInterCodeContext(
                name=name,
                context_type=context_type,
                code=code,
                data=vdata,
                max_variable_count=max_variable_count,
                variable_reserve_count=variable_reserve_count,
                max_frame_count=max_frame_count,
                func_decl_arg_count=func_decl_arg_count,
                func_decl_unnamed_arg_array_base=func_decl_unnamed_arg_array_base,
                func_decl_collapse_base=func_decl_collapse_base,
                source_positions=source_positions,
                super_class_getters=scgetterps
            )
            
            objects[o] = obj
        
        # 设置对象之间的引用关系
        for o in range(obj_count):
            obj = objects[o]
            
            # 设置父对象
            if parents[o] >= 0:
                obj.parent = objects[parents[o]]
            
            # 设置属性设置器
            if prop_setters[o] >= 0:
                obj.prop_setter = objects[prop_setters[o]]
            
            # 设置属性获取器
            if prop_getters[o] >= 0:
                obj.prop_getter = objects[prop_getters[o]]
            
            # 设置超类获取器
            if super_class_getters[o] >= 0:
                obj.super_class_getter_obj = objects[super_class_getters[o]]
            
            # 设置属性
            if properties[o]:
                props = properties[o]
                length = len(props) // 2
                for i in range(length):
                    pos = i * 2
                    pname_idx = props[pos]
                    pobj_idx = props[pos + 1]
                    
                    pname = data_area.string_array[pname_idx] if pname_idx < len(data_area.string_array) else f"prop_{i}"
                    pobj = objects[pobj_idx] if pobj_idx < len(objects) else None
                    
                    # 在Python中，我们可能需要以不同的方式处理属性设置
                    # 这里只是简单地将属性添加到对象的属性字典中
                    if not hasattr(obj, 'properties'):
                        obj.properties = {}
                    obj.properties[pname] = pobj
        
        # 处理变体替换工作
        for w in work:
            if w.index < len(objects):
                w.work[w.index] = objects[w.index]
        
        # 返回顶层对象和所有对象
        top_obj = objects[top_level] if top_level >= 0 and top_level < len(objects) else None
        return top_obj, objects

    @staticmethod
    def load_data_area(stream: BinaryStream) -> Optional[TJSDataArea]:
        """使用流式读取加载数据区域"""
        data_area = TJSDataArea()
        
        tag = stream.read_int32()
        size = stream.read_int32() # we need read but not need use

        if tag != DATA_TAG_LE: None
        
        # 1. 读取字节数组
        count = stream.read_int32()
        if count > 0:
            # 读取字节数据
            data_area.byte_array = stream.read_bytes(count)
            # 对齐到4字节
            stride = (count + 3) >> 2
            stream.skip(stride * 4 - count)
        
        # 2. 读取短整型数组
        count = stream.read_int32()
        if count > 0:
            data_area.short_array = [stream.read_uint16() for _ in range(count)]
            # 对齐到4字节
            if count & 1:
                stream.skip(2)
        
        # 3. 读取整型数组
        count = stream.read_int32()
        if count > 0:
            data_area.long_array = [stream.read_int32() for _ in range(count)]
        
        # 4. 读取长整型数组
        count = stream.read_int32()
        if count > 0:
            data_area.long_long_array = [stream.read_uint64() for _ in range(count)]
        
        # 5. 读取双精度浮点数组
        count = stream.read_int32()
        if count > 0:
            data_area.double_array = [stream.read_double() for _ in range(count)]
        
        # 6. 读取字符串数组
        count = stream.read_int32()
        if count > 0:
            for _ in range(count):
                # 读取字符串长度
                length = stream.read_int32()
                
                # 读取UTF-16字符串
                utf16_data = stream.read_bytes(length * 2)
                try:
                    # 尝试解码为UTF-16
                    string_value = utf16_data.decode('utf-16-le')
                except UnicodeDecodeError:
                    # 如果解码失败，使用原始字节的十六进制表示
                    string_value = f"hex:{utf16_data.hex()}"
                
                data_area.string_array.append(string_value)
                
                # 对齐到4字节
                if length & 1:
                    stream.skip(2)
        
        # 7. 读取八位字节数组
        count = stream.read_int32()
        if count > 0:
            for _ in range(count):
                # 读取八位字节长度
                length = stream.read_int32()
                
                # 读取八位字节数据
                octet_data = stream.read_bytes(length)
                data_area.octet_array.append(octet_data)
                
                # 对齐到4字节
                stride = (length + 3) >> 2
                stream.skip(stride * 4 - length)
        
        return data_area


    @staticmethod
    def is_tjs2_bytecode(stream: BinaryStream) -> bool:
        """检查是否为TJS2字节码"""
        if stream.length < 8:
            return False
            
        # 读取文件标签和版本
        tag = stream.read_uint32()
        ver = stream.read_uint32()
        
        return tag == FILE_TAG_LE and ver == VER_TAG_LE
    
    @staticmethod
    def load_bytecode(file_path: str) -> Optional[Tuple[Optional[TJSInterCodeContext], List[TJSInterCodeContext], TJSDataArea]]:
        """加载TJS字节码文件"""
        try:
            with open(file_path, 'rb') as f:
                stream = BinaryStream(f.read())
                
            if not TJSByteCodeLoader.is_tjs2_bytecode(stream):
                return None
                
            exceptFilesize = stream.read_int32()
            if exceptFilesize != stream.length: raise Exception("文件损坏")

            data_area = TJSByteCodeLoader.load_data_area(stream)
            if not data_area: raise Exception("读取Data Area失败")
            # 加载对象区域
            top_obj, objects = TJSByteCodeLoader.load_objs_area(stream, data_area)
            
            return top_obj, objects, data_area
            
        except Exception as e:
            print(f"Error loading bytecode: {e}")
            return None
