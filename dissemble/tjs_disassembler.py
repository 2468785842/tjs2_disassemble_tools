
from typing import List, Optional, Any

from .tjs_const import FuncArgType, TJSVMOpcode
from .tjs_entity import *

class TJSDisassembler:
    def __init__(self, top_obj: Optional[TJSInterCodeContext], 
                objects: List[TJSInterCodeContext], data_area: TJSDataArea):
        self.top_obj = top_obj
        self.objects = objects
        data_area = data_area
        
    @staticmethod
    def from_vm_reg_addr(addr: int) -> int:
        """从虚拟机寄存器地址转换为可读格式
        根据 C++ 宏定义: #define TJS_FROM_VM_REG_ADDR(x) ((tjs_int)(x) / (tjs_int)sizeof(tTJSVariant))
        tTJSVariant 的大小为 20 字节
        """
        # tjs_variant_size = 20
        return addr # // tjs_variant_size

    @staticmethod
    def from_vm_code_addr(addr: int) -> int:
        """从虚拟机代码地址转换为可读格式
        根据 C++ 宏定义: #define TJS_FROM_VM_CODE_ADDR(x) ((tjs_int)(x) / (tjs_int)sizeof(tjs_uint32))
        tjs_uint32 的大小为 4 字节
        """
        # tjs_uint32 的大小为 4 字节
        # tjs_uint32_size = 4
        return addr # // tjs_uint32_size
    
    @staticmethod
    def get_const_data(base: TJSInterCodeContext.Data, x: int) -> None | int | float | str | bytes:
        if len(base) <= x:
            raise Exception(f"get_const_data: {base}, {x}")
        return base[x]
    
    def get_value_comment(self, value: None | int | float | str | bytes) -> str:
        """获取值的注释表示"""
        if value is None:
            return "null"
        return str(value)

    def disassemble(self, obj_index: int = 0, start: int = 0, end: Optional[int] = None) -> List[DisassembledInstruction]:
        """反汇编指定对象的代码区域"""
        
        instructions: List[DisassembledInstruction] = []

        if obj_index >= len(self.objects):
            return []
            
        obj = self.objects[obj_index]
        data_area = obj.data
        code_area = obj.code
        
        if end is None:
            end = len(code_area)
        elif end > len(code_area):
            end = len(code_area)
            
        i = start
        
        while i < end:
            
            # 解码指令
            opcode_val = code_area[i]
            try:
                opcode = TJSVMOpcode(opcode_val)
            except ValueError:
                # 未知操作码
                instruction = DisassembledInstruction(
                    address=i,
                    opcode=f"unknown ({opcode_val})",
                    size=1,
                )
                instructions.append(instruction)
                i += 1
                continue
                
            # 根据操作码解码
            if opcode == TJSVMOpcode.VM_NOP:
                disasm = self._disassemble_nop(i)
            elif opcode == TJSVMOpcode.VM_NF:
                disasm = self._disassemble_nf(i)
            elif opcode == TJSVMOpcode.VM_CONST:
                disasm = self._disassemble_const(i, data_area, code_area)
            elif opcode == TJSVMOpcode.VM_CP:
                disasm = self._disassemble_cp(i, data_area, code_area)
            elif opcode == TJSVMOpcode.VM_CEQ:
                disasm = self._disassemble_ceq(i, data_area, code_area)
            elif opcode == TJSVMOpcode.VM_CDEQ:
                disasm = self._disassemble_cdeq(i, data_area, code_area)
            elif opcode == TJSVMOpcode.VM_CLT:
                disasm = self._disassemble_clt(i, data_area, code_area)
            elif opcode == TJSVMOpcode.VM_CGT:
                disasm = self._disassemble_cgt(i, data_area, code_area)
            elif opcode == TJSVMOpcode.VM_CHKINS:
                disasm = self._disassemble_chkins(i, data_area, code_area)
            elif opcode in [TJSVMOpcode.VM_LOR, TJSVMOpcode.VM_LOR + 1, TJSVMOpcode.VM_LOR + 2, TJSVMOpcode.VM_LOR + 3]:
                disasm = self._disassemble_lor(i, data_area, code_area, opcode)
            elif opcode in [TJSVMOpcode.VM_LAND, TJSVMOpcode.VM_LAND + 1, TJSVMOpcode.VM_LAND + 2, TJSVMOpcode.VM_LAND + 3]:
                disasm = self._disassemble_land(i, data_area, code_area, opcode)
            elif opcode in [TJSVMOpcode.VM_BOR, TJSVMOpcode.VM_BOR + 1, TJSVMOpcode.VM_BOR + 2, TJSVMOpcode.VM_BOR + 3]:
                disasm = self._disassemble_bor(i, data_area, code_area, opcode)
            elif opcode in [TJSVMOpcode.VM_BXOR, TJSVMOpcode.VM_BXOR + 1, TJSVMOpcode.VM_BXOR + 2, TJSVMOpcode.VM_BXOR + 3]:
                disasm = self._disassemble_bxor(i, data_area, code_area, opcode)
            elif opcode in [TJSVMOpcode.VM_BAND, TJSVMOpcode.VM_BAND + 1, TJSVMOpcode.VM_BAND + 2, TJSVMOpcode.VM_BAND + 3]:
                disasm = self._disassemble_band(i, data_area, code_area, opcode)
            elif opcode in [TJSVMOpcode.VM_SAR, TJSVMOpcode.VM_SAR + 1, TJSVMOpcode.VM_SAR + 2, TJSVMOpcode.VM_SAR + 3]:
                disasm = self._disassemble_sar(i, data_area, code_area, opcode)
            elif opcode in [TJSVMOpcode.VM_SAL, TJSVMOpcode.VM_SAL + 1, TJSVMOpcode.VM_SAL + 2, TJSVMOpcode.VM_SAL + 3]:
                disasm = self._disassemble_sal(i, data_area, code_area, opcode)
            elif opcode in [TJSVMOpcode.VM_SR, TJSVMOpcode.VM_SR + 1, TJSVMOpcode.VM_SR + 2, TJSVMOpcode.VM_SR + 3]:
                disasm = self._disassemble_sr(i, data_area, code_area, opcode)
            elif opcode in [TJSVMOpcode.VM_ADD, TJSVMOpcode.VM_ADD + 1, TJSVMOpcode.VM_ADD + 2, TJSVMOpcode.VM_ADD + 3]:
                disasm = self._disassemble_add(i, data_area, code_area, opcode)
            elif opcode in [TJSVMOpcode.VM_SUB, TJSVMOpcode.VM_SUB + 1, TJSVMOpcode.VM_SUB + 2, TJSVMOpcode.VM_SUB + 3]:
                disasm = self._disassemble_sub(i, data_area, code_area, opcode)
            elif opcode in [TJSVMOpcode.VM_MOD, TJSVMOpcode.VM_MOD + 1, TJSVMOpcode.VM_MOD + 2, TJSVMOpcode.VM_MOD + 3]:
                disasm = self._disassemble_mod(i, data_area, code_area, opcode)
            elif opcode in [TJSVMOpcode.VM_DIV, TJSVMOpcode.VM_DIV + 1, TJSVMOpcode.VM_DIV + 2, TJSVMOpcode.VM_DIV + 3]:
                disasm = self._disassemble_div(i, data_area, code_area, opcode)
            elif opcode in [TJSVMOpcode.VM_IDIV, TJSVMOpcode.VM_IDIV + 1, TJSVMOpcode.VM_IDIV + 2, TJSVMOpcode.VM_IDIV + 3]:
                disasm = self._disassemble_idiv(i, data_area, code_area, opcode)
            elif opcode in [TJSVMOpcode.VM_MUL, TJSVMOpcode.VM_MUL + 1, TJSVMOpcode.VM_MUL + 2, TJSVMOpcode.VM_MUL + 3]:
                disasm = self._disassemble_mul(i, data_area, code_area, opcode)
            elif opcode == TJSVMOpcode.VM_TT:
                disasm = self._disassemble_tt(i, code_area)
            elif opcode == TJSVMOpcode.VM_TF:
                disasm = self._disassemble_tf(i, code_area)
            elif opcode == TJSVMOpcode.VM_SETF:
                disasm = self._disassemble_setf(i, code_area)
            elif opcode == TJSVMOpcode.VM_SETNF:
                disasm = self._disassemble_setnf(i, data_area, code_area)
            elif opcode == TJSVMOpcode.VM_LNOT:
                disasm = self._disassemble_lnot(i, data_area, code_area)
            elif opcode == TJSVMOpcode.VM_BNOT:
                disasm = self._disassemble_bnot(i, data_area, code_area)
            elif opcode == TJSVMOpcode.VM_ASC:
                disasm = self._disassemble_asc(i, data_area, code_area)
            elif opcode == TJSVMOpcode.VM_CHR:
                disasm = self._disassemble_chr(i, data_area, code_area)
            elif opcode == TJSVMOpcode.VM_NUM:
                disasm = self._disassemble_num(i, data_area, code_area)
            elif opcode == TJSVMOpcode.VM_CHS:
                disasm = self._disassemble_chs(i, data_area, code_area)
            elif opcode == TJSVMOpcode.VM_CL:
                disasm = self._disassemble_cl(i, data_area, code_area)
            elif opcode == TJSVMOpcode.VM_INV:
                disasm = self._disassemble_inv(i, data_area, code_area)
            elif opcode == TJSVMOpcode.VM_CHKINV:
                disasm = self._disassemble_chkinv(i, data_area, code_area)
            elif opcode == TJSVMOpcode.VM_TYPEOF:
                disasm = self._disassemble_typeof(i, data_area, code_area)
            elif opcode == TJSVMOpcode.VM_EVAL:
                disasm = self._disassemble_eval(i, data_area, code_area)
            elif opcode == TJSVMOpcode.VM_EEXP:
                disasm = self._disassemble_eexp(i, data_area, code_area)
            elif opcode == TJSVMOpcode.VM_INT:
                disasm = self._disassemble_int(i, data_area, code_area)
            elif opcode == TJSVMOpcode.VM_REAL:
                disasm = self._disassemble_real(i, data_area, code_area)
            elif opcode == TJSVMOpcode.VM_STR:
                disasm = self._disassemble_str(i, data_area, code_area)
            elif opcode == TJSVMOpcode.VM_OCTET:
                disasm = self._disassemble_octet(i, data_area, code_area)
            elif opcode == TJSVMOpcode.VM_CCL:
                disasm = self._disassemble_ccl(i, data_area, code_area)
            elif opcode in [TJSVMOpcode.VM_INC, TJSVMOpcode.VM_INC + 1, TJSVMOpcode.VM_INC + 2, TJSVMOpcode.VM_INC + 3]:
                disasm = self._disassemble_inc(i, data_area, code_area, opcode)
            elif opcode in [TJSVMOpcode.VM_DEC, TJSVMOpcode.VM_DEC + 1, TJSVMOpcode.VM_DEC + 2, TJSVMOpcode.VM_DEC + 3]:
                disasm = self._disassemble_dec(i, data_area, code_area, opcode)
            elif opcode == TJSVMOpcode.VM_JF:
                disasm = self._disassemble_jf(i, data_area, code_area)
            elif opcode == TJSVMOpcode.VM_JNF:
                disasm = self._disassemble_jnf(i, data_area, code_area)
            elif opcode == TJSVMOpcode.VM_JMP:
                disasm = self._disassemble_jmp(i, data_area, code_area)
            elif opcode in [TJSVMOpcode.VM_CALL, TJSVMOpcode.VM_CALLD, TJSVMOpcode.VM_CALLI, TJSVMOpcode.VM_NEW]:
                disasm = self._disassemble_call(i, data_area, code_area, opcode)
            elif opcode in [TJSVMOpcode.VM_GPD, TJSVMOpcode.VM_GPDS]:
                disasm = self._disassemble_gpd(i, data_area, code_area, opcode)
            elif opcode in [TJSVMOpcode.VM_SPD, TJSVMOpcode.VM_SPDE, TJSVMOpcode.VM_SPDEH, TJSVMOpcode.VM_SPDS]:
                disasm = self._disassemble_spd(i, data_area, code_area, opcode)
            elif opcode in [TJSVMOpcode.VM_GPI, TJSVMOpcode.VM_GPIS]:
                disasm = self._disassemble_gpi(i, data_area, code_area, opcode)
            elif opcode in [TJSVMOpcode.VM_SPI, TJSVMOpcode.VM_SPIE, TJSVMOpcode.VM_SPIS]:
                disasm = self._disassemble_spi(i, data_area, code_area, opcode)
            elif opcode == TJSVMOpcode.VM_SETP:
                disasm = self._disassemble_setp(i, data_area, code_area)
            elif opcode == TJSVMOpcode.VM_GETP:
                disasm = self._disassemble_getp(i, data_area, code_area)
            elif opcode in [TJSVMOpcode.VM_DELD, TJSVMOpcode.VM_TYPEOFD]:
                disasm = self._disassemble_deld(i, data_area, code_area, opcode)
            elif opcode in [TJSVMOpcode.VM_DELI, TJSVMOpcode.VM_TYPEOFI]:
                disasm = self._disassemble_deli(i, data_area, code_area, opcode)
            elif opcode == TJSVMOpcode.VM_SRV:
                disasm = self._disassemble_srv(i, data_area, code_area)
            elif opcode == TJSVMOpcode.VM_RET:
                disasm = self._disassemble_ret(i, data_area, code_area)
            elif opcode == TJSVMOpcode.VM_ENTRY:
                disasm = self._disassemble_entry(i, data_area, code_area)
            elif opcode == TJSVMOpcode.VM_EXTRY:
                disasm = self._disassemble_extry(i, data_area, code_area)
            elif opcode == TJSVMOpcode.VM_THROW:
                disasm = self._disassemble_throw(i, data_area, code_area)
            elif opcode == TJSVMOpcode.VM_CHGTHIS:
                disasm = self._disassemble_chgthis(i, data_area, code_area)
            elif opcode == TJSVMOpcode.VM_GLOBAL:
                disasm = self._disassemble_global(i, data_area, code_area)
            elif opcode == TJSVMOpcode.VM_ADDCI:
                disasm = self._disassemble_addci(i, data_area, code_area)
            elif opcode == TJSVMOpcode.VM_REGMEMBER:
                disasm = self._disassemble_regmember(i, data_area, code_area)
            elif opcode == TJSVMOpcode.VM_DEBUGGER:
                disasm = self._disassemble_debugger(i, data_area, code_area)
            else:
                # 默认处理未知操作码
                disasm = DisassembledInstruction(
                    address=i,
                    opcode=opcode.name,
                    operands="",
                    comment=f"Not implemented yet",
                    size=1,
                )
            
            instructions.append(disasm)
            i += disasm.size
            
        return instructions
    
    def _disassemble_lor(self, i, data_area, code_area, opcode):
        return self._disassemble_op2(TJSVMOpcode.VM_LOR, "lor", i, data_area, code_area, opcode)

    def _disassemble_land(self, i, data_area, code_area, opcode):
        return self._disassemble_op2(TJSVMOpcode.VM_LAND, "land", i, data_area, code_area, opcode)

    def _disassemble_bor(self, i, data_area, code_area, opcode):
        return self._disassemble_op2(TJSVMOpcode.VM_BOR, "bor", i, data_area, code_area, opcode)

    def _disassemble_bxor(self, i, data_area, code_area, opcode):
        return self._disassemble_op2(TJSVMOpcode.VM_BXOR, "bxor", i, data_area, code_area, opcode)

    def _disassemble_band(self, i, data_area, code_area, opcode):
        return self._disassemble_op2(TJSVMOpcode.VM_BAND, "band", i, data_area, code_area, opcode)

    def _disassemble_sar(self, i, data_area, code_area, opcode):
        return self._disassemble_op2(TJSVMOpcode.VM_SAR, "sar", i, data_area, code_area, opcode)

    def _disassemble_sal(self, i, data_area, code_area, opcode):
        return self._disassemble_op2(TJSVMOpcode.VM_SAL, "sal", i, data_area, code_area, opcode)

    def _disassemble_sr(self, i, data_area, code_area, opcode):
        return self._disassemble_op2(TJSVMOpcode.VM_SR, "sr", i, data_area, code_area, opcode)

    def _disassemble_add(self, i, data_area, code_area, opcode):
        return self._disassemble_op2(TJSVMOpcode.VM_ADD, "add", i, data_area, code_area, opcode)

    def _disassemble_sub(self, i, data_area, code_area, opcode):
        return self._disassemble_op2(TJSVMOpcode.VM_SUB, "sub", i, data_area, code_area, opcode)

    def _disassemble_mod(self, i, data_area, code_area, opcode):
        return self._disassemble_op2(TJSVMOpcode.VM_MOD, "mod", i, data_area, code_area, opcode)

    def _disassemble_div(self, i, data_area, code_area, opcode):
        return self._disassemble_op2(TJSVMOpcode.VM_DIV, "div", i, data_area, code_area, opcode)

    def _disassemble_idiv(self, i, data_area, code_area, opcode):
        return self._disassemble_op2(TJSVMOpcode.VM_IDIV, "idiv", i, data_area, code_area, opcode)

    def _disassemble_mul(self, i, data_area, code_area, opcode):
        return self._disassemble_op2(TJSVMOpcode.VM_MUL, "mul", i, data_area, code_area, opcode)

    def _disassemble_op2(self, base_opcode, mnemonic, i, data_area, code_area, opcode):
        """通用的 2 操作数指令反汇编器 (带 pd/pi/p 变体)"""
        if opcode == base_opcode:
            reg1 = self.from_vm_reg_addr(code_area[i + 1])
            reg2 = self.from_vm_reg_addr(code_area[i + 2])
            return DisassembledInstruction(
                address=i,
                opcode=mnemonic,
                operands=f"%{reg1}, %{reg2}",
                comment="",
                size=3
            )
        elif opcode == base_opcode + 1:
            reg1 = self.from_vm_reg_addr(code_area[i + 1])
            reg2 = self.from_vm_reg_addr(code_area[i + 2])
            reg3 = self.from_vm_reg_addr(code_area[i + 3])
            reg4 = self.from_vm_reg_addr(code_area[i + 4])
            value = self.get_const_data(data_area, code_area[i + 3])
            comment = f"*{reg3} = {self.get_value_comment(value)}"
            return DisassembledInstruction(
                address=i,
                opcode=f"{mnemonic}pd",
                operands=f"%{reg1}, %{reg2}.*{reg3}, %{reg4}",
                comment=comment,
                size=5
            )
        elif opcode == base_opcode + 2:
            reg1 = self.from_vm_reg_addr(code_area[i + 1])
            reg2 = self.from_vm_reg_addr(code_area[i + 2])
            reg3 = self.from_vm_reg_addr(code_area[i + 3])
            reg4 = self.from_vm_reg_addr(code_area[i + 4])
            return DisassembledInstruction(
                address=i,
                opcode=f"{mnemonic}pi",
                operands=f"%{reg1}, %{reg2}.%{reg3}, %{reg4}",
                comment="",
                size=5
            )
        elif opcode == base_opcode + 3:
            reg1 = self.from_vm_reg_addr(code_area[i + 1])
            reg2 = self.from_vm_reg_addr(code_area[i + 2])
            reg3 = self.from_vm_reg_addr(code_area[i + 3])
            return DisassembledInstruction(
                address=i,
                opcode=f"{mnemonic}p",
                operands=f"%{reg1}, %{reg2}, %{reg3}",
                comment="",
                size=4
            )

    def _disassemble_cp(self, i, data_area, code_area):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        reg2 = self.from_vm_reg_addr(code_area[i + 2])
        
        return DisassembledInstruction(
            address=i,
            opcode="cp",
            operands=f"%{reg1}, %{reg2}",
            comment="",
            size=3
        )
    
    def _disassemble_ceq(self, i, data_area, code_area):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        reg2 = self.from_vm_reg_addr(code_area[i + 2])
        
        return DisassembledInstruction(
            address=i,
            opcode="ceq",
            operands=f"%{reg1}, %{reg2}",
            comment="",
            size=3
        )
    
    def _disassemble_cdeq(self, i, data_area, code_area):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        reg2 = self.from_vm_reg_addr(code_area[i + 2])
        
        return DisassembledInstruction(
            address=i,
            opcode="cdeq",
            operands=f"%{reg1}, %{reg2}",
            comment="",
            size=3
        )
    
    def _disassemble_clt(self, i, data_area, code_area):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        reg2 = self.from_vm_reg_addr(code_area[i + 2])
        
        return DisassembledInstruction(
            address=i,
            opcode="clt",
            operands=f"%{reg1}, %{reg2}",
            comment="",
            size=3
        )
    
    def _disassemble_cgt(self, i, data_area, code_area):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        reg2 = self.from_vm_reg_addr(code_area[i + 2])
        
        return DisassembledInstruction(
            address=i,
            opcode="cgt",
            operands=f"%{reg1}, %{reg2}",
            comment="",
            size=3
        )
    
    def _disassemble_chkins(self, i, data_area, code_area):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        reg2 = self.from_vm_reg_addr(code_area[i + 2])
        
        return DisassembledInstruction(
            address=i,
            opcode="chkins",
            operands=f"%{reg1}, %{reg2}",
            comment="",
            size=3
        )
    
    def _disassemble_tt(self, i, code_area):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        
        return DisassembledInstruction(
            address=i,
            opcode="tt",
            operands=f"%{reg1}",
            comment="",
            size=2
        )
    
    def _disassemble_tf(self, i, code_area):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        
        return DisassembledInstruction(
            address=i,
            opcode="tf",
            operands=f"%{reg1}",
            comment="",
            size=2
        )
    
    def _disassemble_setf(self, i, code_area):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        
        return DisassembledInstruction(
            address=i,
            opcode="setf",
            operands=f"%{reg1}",
            comment="",
            size=2
        )
    
    def _disassemble_setnf(self, i, data_area, code_area):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        
        return DisassembledInstruction(
            address=i,
            opcode="setnf",
            operands=f"%{reg1}",
            comment="",
            size=2
        )
    
    def _disassemble_lnot(self, i, data_area, code_area):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        
        return DisassembledInstruction(
            address=i,
            opcode="lnot",
            operands=f"%{reg1}",
            comment="",
            size=2
        )
    
    def _disassemble_bnot(self, i, data_area, code_area):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        
        return DisassembledInstruction(
            address=i,
            opcode="bnot",
            operands=f"%{reg1}",
            comment="",
            size=2
        )
    
    def _disassemble_asc(self, i, data_area, code_area):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        
        return DisassembledInstruction(
            address=i,
            opcode="asc",
            operands=f"%{reg1}",
            comment="",
            size=2
        )
    
    def _disassemble_chr(self, i, data_area, code_area):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        
        return DisassembledInstruction(
            address=i,
            opcode="chr",
            operands=f"%{reg1}",
            comment="",
            size=2
        )
    
    def _disassemble_num(self, i, data_area, code_area):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        
        return DisassembledInstruction(
            address=i,
            opcode="num",
            operands=f"%{reg1}",
            comment="",
            size=2
        )
    
    def _disassemble_chs(self, i, data_area, code_area):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        
        return DisassembledInstruction(
            address=i,
            opcode="chs",
            operands=f"%{reg1}",
            comment="",
            size=2
        )
    
    def _disassemble_cl(self, i, data_area, code_area):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        
        return DisassembledInstruction(
            address=i,
            opcode="cl",
            operands=f"%{reg1}",
            comment="",
            size=2
        )
    
    def _disassemble_inv(self, i, data_area, code_area):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        
        return DisassembledInstruction(
            address=i,
            opcode="inv",
            operands=f"%{reg1}",
            comment="",
            size=2
        )
    
    def _disassemble_chkinv(self, i, data_area, code_area):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        
        return DisassembledInstruction(
            address=i,
            opcode="chkinv",
            operands=f"%{reg1}",
            comment="",
            size=2
        )
    
    def _disassemble_typeof(self, i, data_area, code_area):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        
        return DisassembledInstruction(
            address=i,
            opcode="typeof",
            operands=f"%{reg1}",
            comment="",
            size=2
        )
    
    def _disassemble_eval(self, i, data_area, code_area):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        
        return DisassembledInstruction(
            address=i,
            opcode="eval",
            operands=f"%{reg1}",
            comment="",
            size=2
        )
    
    def _disassemble_eexp(self, i, data_area, code_area):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        
        return DisassembledInstruction(
            address=i,
            opcode="eexp",
            operands=f"%{reg1}",
            comment="",
            size=2
        )
    
    def _disassemble_int(self, i, data_area, code_area):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        
        return DisassembledInstruction(
            address=i,
            opcode="int",
            operands=f"%{reg1}",
            comment="",
            size=2
        )
    
    def _disassemble_real(self, i, data_area, code_area):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        
        return DisassembledInstruction(
            address=i,
            opcode="real",
            operands=f"%{reg1}",
            comment="",
            size=2
        )
    
    def _disassemble_str(self, i, data_area, code_area):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        
        return DisassembledInstruction(
            address=i,
            opcode="str",
            operands=f"%{reg1}",
            comment="",
            size=2
        )
    
    def _disassemble_octet(self, i, data_area, code_area):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        
        return DisassembledInstruction(
            address=i,
            opcode="octet",
            operands=f"%{reg1}",
            comment="",
            size=2
        )
    
    def _disassemble_ccl(self, i, data_area, code_area):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        count = code_area[i + 2]
        reg_end = reg1 + count - 1
        
        return DisassembledInstruction(
            address=i,
            opcode="ccl",
            operands=f"%{reg1}-%{reg_end}",
            comment="",
            size=3
        )
    
    def _disassemble_inc(self, i, data_area, code_area, opcode):
        if opcode == TJSVMOpcode.VM_INC:
            reg1 = self.from_vm_reg_addr(code_area[i + 1])
            return DisassembledInstruction(
                address=i,
                opcode="inc",
                operands=f"%{reg1}",
                comment="",
                size=2
            )
        elif opcode == TJSVMOpcode.VM_INC + 1:
            reg1 = self.from_vm_reg_addr(code_area[i + 1])
            reg2 = self.from_vm_reg_addr(code_area[i + 2])
            reg3 = self.from_vm_reg_addr(code_area[i + 3])
            
            value = self.get_const_data(data_area, code_area[i + 3])
            comment = f"*{reg3} = {self.get_value_comment(value)}"
                
            return DisassembledInstruction(
                address=i,
                opcode="incpd",
                operands=f"%{reg1}, %{reg2}.*{reg3}",
                comment=comment,
                size=4
            )
        elif opcode == TJSVMOpcode.VM_INC + 2:
            reg1 = self.from_vm_reg_addr(code_area[i + 1])
            reg2 = self.from_vm_reg_addr(code_area[i + 2])
            reg3 = self.from_vm_reg_addr(code_area[i + 3])
            
            return DisassembledInstruction(
                address=i,
                opcode="incpi",
                operands=f"%{reg1}, %{reg2}.%{reg3}",
                comment="",
                size=4
            )
        elif opcode == TJSVMOpcode.VM_INC + 3:
            reg1 = self.from_vm_reg_addr(code_area[i + 1])
            reg2 = self.from_vm_reg_addr(code_area[i + 2])
            
            return DisassembledInstruction(
                address=i,
                opcode="incp",
                operands=f"%{reg1}, %{reg2}",
                comment="",
                size=3
            )
    
    def _disassemble_dec(self, i, data_area, code_area, opcode):
        if opcode == TJSVMOpcode.VM_DEC:
            reg1 = self.from_vm_reg_addr(code_area[i + 1])
            return DisassembledInstruction(
                address=i,
                opcode="dec",
                operands=f"%{reg1}",
                comment="",
                size=2
            )
        elif opcode == TJSVMOpcode.VM_DEC + 1:
            reg1 = self.from_vm_reg_addr(code_area[i + 1])
            reg2 = self.from_vm_reg_addr(code_area[i + 2])
            reg3 = self.from_vm_reg_addr(code_area[i + 3])
            
            value = self.get_const_data(data_area, code_area[i + 3])
            comment = f"*{reg3} = {self.get_value_comment(value)}"
                
            return DisassembledInstruction(
                address=i,
                opcode="decpd",
                operands=f"%{reg1}, %{reg2}.*{reg3}",
                comment=comment,
                size=4
            )
        elif opcode == TJSVMOpcode.VM_DEC + 2:
            reg1 = self.from_vm_reg_addr(code_area[i + 1])
            reg2 = self.from_vm_reg_addr(code_area[i + 2])
            reg3 = self.from_vm_reg_addr(code_area[i + 3])
            
            return DisassembledInstruction(
                address=i,
                opcode="decpi",
                operands=f"%{reg1}, %{reg2}.%{reg3}",
                comment="",
                size=4
            )
        elif opcode == TJSVMOpcode.VM_DEC + 3:
            reg1 = self.from_vm_reg_addr(code_area[i + 1])
            reg2 = self.from_vm_reg_addr(code_area[i + 2])
            
            return DisassembledInstruction(
                address=i,
                opcode="decp",
                operands=f"%{reg1}, %{reg2}",
                comment="",
                size=3
            )
    
    def _disassemble_jf(self, i, data_area, code_area):
        addr = self.from_vm_code_addr(code_area[i + 1]) + i
        
        return DisassembledInstruction(
            address=i,
            opcode="jf",
            operands=f"0x{addr:09X}",
            comment="",
            size=2
        )
    
    def _disassemble_jnf(self, i, data_area, code_area):
        addr = self.from_vm_code_addr(code_area[i + 1]) + i
        
        return DisassembledInstruction(
            address=i,
            opcode="jnf",
            operands=f"0x{addr:09X}",
            comment="",
            size=2
        )
    
    def _disassemble_jmp(self, i, data_area, code_area):
        addr = self.from_vm_code_addr(code_area[i + 1]) + i
        
        return DisassembledInstruction(
            address=i,
            opcode="jmp",
            operands=f"0x{addr:09X}",
            comment="",
            size=2
        )
    
    def _disassemble_call(self, i, data_area, code_area, opcode):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        reg2 = self.from_vm_reg_addr(code_area[i + 2])
        
        if opcode == TJSVMOpcode.VM_CALL:
            operands = f"%{reg1}, %{reg2}("
            st = 4
        elif opcode == TJSVMOpcode.VM_CALLD:
            reg3 = self.from_vm_reg_addr(code_area[i + 3])
            operands = f"%{reg1}, %{reg2}.*{reg3}("
            st = 5
        elif opcode == TJSVMOpcode.VM_CALLI:
            reg3 = self.from_vm_reg_addr(code_area[i + 3])
            operands = f"%{reg1}, %{reg2}.%{reg3}("
            st = 5
        elif opcode == TJSVMOpcode.VM_NEW:
            operands = f"%{reg1}, %{reg2}("
            st = 4
        
        num = code_area[i + st - 1]
        c = 0
        
        if num == -1:
            # omit arg
            size = st
            operands += "..."
        elif num == -2:
            # expand arg
            st += 1
            num = code_area[i + st - 1]
            size = st + num * 2
            first = True
            for j in range(num):
                if not first:
                    operands += ", "
                first = False
                
                arg_type = code_area[i + st + j * 2]
                arg_reg = self.from_vm_reg_addr(code_area[i + st + j * 2 + 1])
                
                if arg_type == FuncArgType.fatNormal.value:
                    operands += f"%{arg_reg}"
                elif arg_type == FuncArgType.fatExpand.value:
                    operands += f"%{arg_reg}*"
                elif arg_type == FuncArgType.fatUnnamedExpand.value:
                    operands += "*"
        else:
            # normal operation
            size = st + num
            first = True
            while num > 0:
                if not first:
                    operands += ", "
                first = False
                
                arg_reg = self.from_vm_reg_addr(code_area[i + c + st])
                operands += f"%{arg_reg}"
                c += 1
                num -= 1
        
        operands += ")"
        
        comment = ""
        if opcode == TJSVMOpcode.VM_CALLD and data_area:
            reg3 = self.from_vm_reg_addr(code_area[i + 3])
            value = self.get_const_data(data_area, code_area[i + 3])
            comment = f"*{reg3} = {self.get_value_comment(value)}"
        
        opcode_name = "call"
        if opcode == TJSVMOpcode.VM_CALLD:
            opcode_name = "calld"
        elif opcode == TJSVMOpcode.VM_CALLI:
            opcode_name = "calli"
        elif opcode == TJSVMOpcode.VM_NEW:
            opcode_name = "new"
        
        return DisassembledInstruction(
            address=i,
            opcode=opcode_name,
            operands=operands,
            comment=comment,
            size=size
        )
    
    def _disassemble_gpd(self, i, data_area, code_area, opcode):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        reg2 = self.from_vm_reg_addr(code_area[i + 2])
        reg3 = self.from_vm_reg_addr(code_area[i + 3])
        
        value = self.get_const_data(data_area, code_area[i + 3])
        comment = f"*{reg3} = {self.get_value_comment(value)}"
        
        opcode_name = "gpd" if opcode == TJSVMOpcode.VM_GPD else "gpds"
        
        return DisassembledInstruction(
            address=i,
            opcode=opcode_name,
            operands=f"%{reg1}, %{reg2}.*{reg3}",
            comment=comment,
            size=4
        )
    
    def _disassemble_spd(self, i, data_area, code_area, opcode):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        reg2 = self.from_vm_reg_addr(code_area[i + 2])
        reg3 = self.from_vm_reg_addr(code_area[i + 3])

        value = self.get_const_data(data_area, code_area[i + 2])
        comment = f"*{reg2} = {self.get_value_comment(value)}"
        
        if opcode == TJSVMOpcode.VM_SPD:
            opcode_name = "spd"
        elif opcode == TJSVMOpcode.VM_SPDE:
            opcode_name = "spde"
        elif opcode == TJSVMOpcode.VM_SPDEH:
            opcode_name = "spdeh"
        elif opcode == TJSVMOpcode.VM_SPDS:
            opcode_name = "spds"
        
        return DisassembledInstruction(
            address=i,
            opcode=opcode_name,
            operands=f"%{reg1}.*{reg2}, %{reg3}",
            comment=comment,
            size=4
        )
    
    def _disassemble_gpi(self, i, data_area, code_area, opcode):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        reg2 = self.from_vm_reg_addr(code_area[i + 2])
        reg3 = self.from_vm_reg_addr(code_area[i + 3])
        
        opcode_name = "gpi" if opcode == TJSVMOpcode.VM_GPI else "gpis"
        
        return DisassembledInstruction(
            address=i,
            opcode=opcode_name,
            operands=f"%{reg1}, %{reg2}.%{reg3}",
            comment="",
            size=4
        )
    
    def _disassemble_spi(self, i, data_area, code_area, opcode):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        reg2 = self.from_vm_reg_addr(code_area[i + 2])
        reg3 = self.from_vm_reg_addr(code_area[i + 3])
        
        if opcode == TJSVMOpcode.VM_SPI:
            opcode_name = "spi"
        elif opcode == TJSVMOpcode.VM_SPIE:
            opcode_name = "spie"
        elif opcode == TJSVMOpcode.VM_SPIS:
            opcode_name = "spis"
        
        return DisassembledInstruction(
            address=i,
            opcode=opcode_name,
            operands=f"%{reg1}.%{reg2}, %{reg3}",
            comment="",
            size=4
        )
    
    def _disassemble_setp(self, i, data_area, code_area):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        reg2 = self.from_vm_reg_addr(code_area[i + 2])
        
        return DisassembledInstruction(
            address=i,
            opcode="setp",
            operands=f"%{reg1}, %{reg2}",
            comment="",
            size=3
        )
    
    def _disassemble_getp(self, i, data_area, code_area):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        reg2 = self.from_vm_reg_addr(code_area[i + 2])
        
        return DisassembledInstruction(
            address=i,
            opcode="getp",
            operands=f"%{reg1}, %{reg2}",
            comment="",
            size=3
        )
    
    def _disassemble_deld(self, i, data_area, code_area, opcode):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        reg2 = self.from_vm_reg_addr(code_area[i + 2])
        reg3 = self.from_vm_reg_addr(code_area[i + 3])
    
        value = self.get_const_data(data_area, code_area[i + 3])
        comment = f"*{reg3} = {self.get_value_comment(value)}"
        
        opcode_name = "deld" if opcode == TJSVMOpcode.VM_DELD else "typeofd"
        
        return DisassembledInstruction(
            address=i,
            opcode=opcode_name,
            operands=f"%{reg1}, %{reg2}.*{reg3}",
            comment=comment,
            size=4
        )
    
    def _disassemble_deli(self, i, data_area, code_area, opcode):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        reg2 = self.from_vm_reg_addr(code_area[i + 2])
        reg3 = self.from_vm_reg_addr(code_area[i + 3])
        
        opcode_name = "deli" if opcode == TJSVMOpcode.VM_DELI else "typeofi"
        
        return DisassembledInstruction(
            address=i,
            opcode=opcode_name,
            operands=f"%{reg1}, %{reg2}.%{reg3}",
            comment="",
            size=4
        )
    
    def _disassemble_srv(self, i, data_area, code_area):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        
        return DisassembledInstruction(
            address=i,
            opcode="srv",
            operands=f"%{reg1}",
            comment="",
            size=2
        )
    
    def _disassemble_ret(self, i, data_area, code_area):
        return DisassembledInstruction(
            address=i,
            opcode="ret",
            operands="",
            comment="",
            size=1
        )
    
    def _disassemble_entry(self, i, data_area, code_area):
        addr = self.from_vm_code_addr(code_area[i + 1]) + i
        reg1 = self.from_vm_reg_addr(code_area[i + 2])
        
        return DisassembledInstruction(
            address=i,
            opcode="entry",
            operands=f"{addr:09d}, %{reg1}",
            comment="",
            size=3
        )
    
    def _disassemble_extry(self, i, data_area, code_area):
        return DisassembledInstruction(
            address=i,
            opcode="extry",
            operands="",
            comment="",
            size=1
        )
    
    def _disassemble_throw(self, i, data_area, code_area):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        
        return DisassembledInstruction(
            address=i,
            opcode="throw",
            operands=f"%{reg1}",
            comment="",
            size=2
        )
    
    def _disassemble_chgthis(self, i, data_area, code_area):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        reg2 = self.from_vm_reg_addr(code_area[i + 2])
        
        return DisassembledInstruction(
            address=i,
            opcode="chgthis",
            operands=f"%{reg1}, %{reg2}",
            comment="",
            size=3
        )
    
    def _disassemble_global(self, i, data_area, code_area):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        
        return DisassembledInstruction(
            address=i,
            opcode="global",
            operands=f"%{reg1}",
            comment="",
            size=2
        )
    
    def _disassemble_addci(self, i, data_area, code_area):
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        reg2 = self.from_vm_reg_addr(code_area[i + 2])
        
        return DisassembledInstruction(
            address=i,
            opcode="addci",
            operands=f"%{reg1}, %{reg2}",
            comment="",
            size=3
        )
    
    def _disassemble_regmember(self, i, data_area, code_area):
        return DisassembledInstruction(
            address=i,
            opcode="regmember",
            operands="",
            comment="",
            size=1
        )
    
    def _disassemble_debugger(self, i, data_area, code_area):
        return DisassembledInstruction(
            address=i,
            opcode="debugger",
            operands="",
            comment="",
            size=1
        )
    
    def _disassemble_nop(self, i: int) -> DisassembledInstruction:
        return DisassembledInstruction(
            address=i,
            opcode="nop",
            size=1
        )
    
    def _disassemble_nf(self, i: int) -> DisassembledInstruction:
        return DisassembledInstruction(
            address=i,
            opcode="nf",
            comment="!",
            size=1
        )
  
    def _disassemble_const(self, i: int, data_area: TJSInterCodeContext.Data, code_area: List[int]) -> DisassembledInstruction:
        reg1 = self.from_vm_reg_addr(code_area[i + 1])
        reg2 = self.from_vm_reg_addr(code_area[i + 2])
        
        comment = f"*{self.from_vm_reg_addr(reg2)} = {self.get_value_comment(self.get_const_data(data_area, code_area[i + 2]))}"
            
        return DisassembledInstruction(
            address=i,
            opcode="const",
            operands=f"%{reg1}, *{reg2}",
            comment=comment,
            size=3
        )
