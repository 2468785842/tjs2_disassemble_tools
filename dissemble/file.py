import struct
from io import BytesIO

class BinaryStream:
    """二进制流读取器，封装字节操作"""
    
    def __init__(self, data: bytes):
        self.stream = BytesIO(data)
        self.length = len(data)
    
    def read_uint32(self) -> int:
        """读取4字节无符号整数"""
        return struct.unpack('<I', self.stream.read(4))[0]
    
    def read_int32(self) -> int:
        """读取4字节有符号整数"""
        return struct.unpack('<i', self.stream.read(4))[0]
    
    def read_uint16(self) -> int:
        """读取2字节无符号整数"""
        return struct.unpack('<H', self.stream.read(2))[0]
    
    def read_uint64(self) -> int:
        """读取8字节无符号整数"""
        return struct.unpack('<Q', self.stream.read(8))[0]
    
    def read_double(self) -> float:
        """读取8字节双精度浮点数"""
        return struct.unpack('<d', self.stream.read(8))[0]
    
    def read_bytes(self, length: int) -> bytes:
        """读取指定长度的字节"""
        return self.stream.read(length)
    
    def skip(self, length: int):
        """跳过指定长度的字节"""
        self.stream.seek(self.stream.tell() + length)
    
    def tell(self) -> int:
        """获取当前读取位置"""
        return self.stream.tell()
    
    def seek(self, position: int):
        """设置读取位置"""
        self.stream.seek(position)
