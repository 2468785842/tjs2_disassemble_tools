from enum import Enum, IntEnum, auto

# TJS2 字节码文件标记 小端表示
FILE_TAG_LE = 0x32534A54  # 'TJS2
VER_TAG_LE = 0x00303031   # 版本 '100'\0
DATA_TAG_LE = 0x41544144   # 'DATA'
OBJ_TAG_LE = 0x534A424F   # 'OBJS'


TYPE_VOID = 0;
TYPE_OBJECT = 1;
TYPE_INTER_OBJECT = 2;
TYPE_STRING = 3;
TYPE_OCTET = 4;
TYPE_REAL = 5;
TYPE_BYTE = 6;
TYPE_SHORT = 7;
TYPE_INTEGER = 8;
TYPE_LONG = 9;
TYPE_INTER_GENERATOR = 10; # temporary
TYPE_UNKNOWN = -1;

class TJSContextType(Enum):
    """TJS上下文类型"""
    ctTopLevel = 0
    ctFunction = 1
    ctExprFunction = 2
    ctProperty = 3
    ctPropertySetter = 4
    ctPropertyGetter = 5
    ctClass = 6
    ctSuperClassGetter = 7

# 定义 TJS 虚拟机操作码
class TJSVMOpcode(IntEnum):
    
    VM_NOP = 0
    VM_CONST = auto()
    VM_CP = auto()
    VM_CL = auto()
    VM_CCL = auto()
    VM_TT = auto()
    VM_TF = auto()
    VM_CEQ = auto()
    VM_CDEQ = auto()
    VM_CLT = auto()
    VM_CGT = auto()
    VM_SETF = auto()
    VM_SETNF = auto()
    VM_LNOT = auto()
    VM_NF = auto()
    VM_JF = auto()
    VM_JNF = auto()
    VM_JMP = auto()

    VM_INC = auto()
    VM_INCPD = auto()
    VM_INCPI = auto()
    VM_INCP = auto()
    VM_DEC = auto()
    VM_DECPD = auto()
    VM_DECPI = auto()
    VM_DECP = auto()
    VM_LOR = auto()
    VM_LORPD = auto()
    VM_LORPI = auto()
    VM_LORP = auto()
    VM_LAND = auto()
    VM_LANDPD = auto()
    VM_LANDPI = auto()
    VM_LANDP = auto()
    VM_BOR = auto()
    VM_BORPD = auto()
    VM_BORPI = auto()
    VM_BORP = auto()
    VM_BXOR = auto()
    VM_BXORPD = auto()
    VM_BXORPI = auto()
    VM_BXORP = auto()
    VM_BAND = auto()
    VM_BANDPD = auto()
    VM_BANDPI = auto()
    VM_BANDP = auto()
    VM_SAR = auto()
    VM_SARPD = auto()
    VM_SARPI = auto()
    VM_SARP = auto()
    VM_SAL = auto()
    VM_SALPD = auto()
    VM_SALPI = auto()
    VM_SALP = auto()
    VM_SR = auto()
    VM_SRPD = auto()
    VM_SRPI = auto()
    VM_SRP = auto()
    VM_ADD = auto()
    VM_ADDPD = auto()
    VM_ADDPI = auto()
    VM_ADDP = auto()
    VM_SUB = auto()
    VM_SUBPD = auto()
    VM_SUBPI = auto()
    VM_SUBP = auto()
    VM_MOD = auto()
    VM_MODPD = auto()
    VM_MODPI = auto()
    VM_MODP = auto()
    VM_DIV = auto()
    VM_DIVPD = auto()
    VM_DIVPI = auto()
    VM_DIVP = auto()
    VM_IDIV = auto()
    VM_IDIVPD = auto()
    VM_IDIVPI = auto()
    VM_IDIVP = auto()
    VM_MUL = auto()
    VM_MULPD = auto()
    VM_MULPI = auto()
    VM_MULP = auto()

    VM_BNOT = auto()
    VM_TYPEOF = auto()
    VM_TYPEOFD = auto()
    VM_TYPEOFI = auto()
    VM_EVAL = auto()
    VM_EEXP = auto()
    VM_CHKINS = auto()
    VM_ASC = auto()
    VM_CHR = auto()
    VM_NUM = auto()
    VM_CHS = auto()
    VM_INV = auto()
    VM_CHKINV = auto()
    VM_INT = auto()
    VM_REAL = auto()
    VM_STR = auto()
    VM_OCTET = auto()
    VM_CALL = auto()
    VM_CALLD = auto()
    VM_CALLI = auto()
    VM_NEW = auto()
    VM_GPD = auto()
    VM_SPD = auto()
    VM_SPDE = auto()
    VM_SPDEH = auto()
    VM_GPI = auto()
    VM_SPI = auto()
    VM_SPIE = auto()
    VM_GPDS = auto()
    VM_SPDS = auto()
    VM_GPIS = auto()
    VM_SPIS = auto()
    VM_SETP = auto()
    VM_GETP = auto()
    VM_DELD =  auto()
    VM_DELI =  auto()
    VM_SRV =  auto()
    VM_RET =  auto()
    VM_ENTRY =  auto()
    VM_EXTRY =  auto()
    VM_THROW =  auto()
    VM_CHGTHIS =  auto()
    VM_GLOBAL =  auto()
    VM_ADDCI =  auto()
    VM_REGMEMBER =  auto()
    VM_DEBUGGER =  auto()

# 函数参数类型
class FuncArgType(Enum):
    fatNormal = 0
    fatExpand = 1
    fatUnnamedExpand = 2
