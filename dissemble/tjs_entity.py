from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict

from .tjs_const import TJSContextType

@dataclass
class SourcePos:
    """源代码位置信息"""
    code_pos: int
    source_pos: int


# 修改TJSInterCodeContext以支持属性
@dataclass
class TJSInterCodeContext:
    type Data = List[None | int | float | str | bytes]
    """TJS中间代码上下文"""
    name: str
    context_type: TJSContextType
    code: List[int]
    data: Data
    max_variable_count: int
    variable_reserve_count: int
    max_frame_count: int
    func_decl_arg_count: int
    func_decl_unnamed_arg_array_base: int
    func_decl_collapse_base: int
    source_positions: List[SourcePos]
    super_class_getters: List[int]
    parent: Optional['TJSInterCodeContext'] = None
    prop_setter: Optional['TJSInterCodeContext'] = None
    prop_getter: Optional['TJSInterCodeContext'] = None
    super_class_getter_obj: Optional['TJSInterCodeContext'] = None
    properties: Dict[str, Any] = field(default_factory=dict)  # 属性字典


@dataclass
class VariantReplace:
    """变体替换工作项"""
    work: TJSInterCodeContext.Data  # 变体列表
    index: int       # 在变体列表中的索引
    obj_index: int   # 对象索引

@dataclass
class CodeBlock:
    """表示代码块，包含源代码信息"""
    def __init__(self):
        self.lines = {}
    
    def src_pos_to_line(self, src_pos: int) -> int:
        """将源文件位置转换为行号（简化实现）"""
        return src_pos // 80  # 假设每行80个字符
    
    def get_line(self, line: int) -> str:
        """获取指定行的源代码（简化实现）"""
        return f"Source line {line}"

@dataclass
class TJSDataArea:
    """存储TJS字节码的数据区域"""
    byte_array: List[int] = field(default_factory=list)
    short_array: List[int] = field(default_factory=list)
    long_array: List[int] = field(default_factory=list)
    long_long_array: List[int] = field(default_factory=list)
    double_array: List[float] = field(default_factory=list)
    string_array: List[str] = field(default_factory=list)
    octet_array: List[bytes] = field(default_factory=list)

@dataclass
class DisassembledInstruction:
    address: int
    opcode: str
    size: int
    operands: str = ''
    comment: str = ''
