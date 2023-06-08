import os

class CodeWriter:
    _UNARY_ARITHMERIC_OPS = {"neg": "-", "not": "!"}
    _BINARY_ARITHMERIC_OPS = {"add": "+", "sub": "-", "eq": "EQ", "gt": "GT", "lt": "LT", "and": "&", "or": "|"}
    _MEMORY_SEGMENT_WITH_PROGRAMMATIC_POINTER = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}

    def __init__(self, input_filepath):
        self.input_filename = os.path.split(input_filepath)[-1]
        self._existing_static_vars = {}
        self._label_counter = 0

    def write_arithmetic(self, cmd_name):
        outs = []
        cmd_name = cmd_name.strip()
        if cmd_name in self._UNARY_ARITHMERIC_OPS.keys():
            outs.extend([
                "@SP",
                "M=M-1",
                "A=M",
                f"D={self._UNARY_ARITHMERIC_OPS[cmd_name]}M"
            ])
        elif cmd_name in self._BINARY_ARITHMERIC_OPS.keys():
            outs.extend([
                "@SP",
                "M=M-1",
                "A=M",
                "D=M",
                "@SP",
                "M=M-1",
                "A=M",
            ])
            arithmetic_operator = self._BINARY_ARITHMERIC_OPS[cmd_name]
            if not arithmetic_operator.isalpha():
                outs.append(f"D=D{arithmetic_operator}M" if arithmetic_operator != "-" else f"D=M{arithmetic_operator}D")  # apart from 'sub', all options here are symmetric (and Hack spec doesn't explicitly allow 'M+D')
            else:
                outs.extend([
                    "D=M-D",
                    f"@REGTRUE{self._label_counter}",
                    f"D;J{arithmetic_operator}",
                    "D=0", # if we don't jump put False in D and jumpt to after "D=True"
                    f"@AFTERTRUEFALSE{self._label_counter + 1}",
                    "0;JMP",
                    f"(REGTRUE{self._label_counter})",
                    "D=-1", # put "True" in D, i.e. -1 since it's binary written 1111111111111111
                    f"(AFTERTRUEFALSE{self._label_counter + 1})",
                ])
                self._label_counter += 2
        else:
            raise ValueError(f"Could not recognize command name {cmd_name}!!!")
        outs.extend([
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
        ])
        return outs

    def _write_push(self, mem_seg, var_num):
        common_instructions = [
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1"
        ]
        if mem_seg == "constant":
            return [
                f"@{var_num}",
                "D=A",
            ] + common_instructions
        else:
            return [
                "A=D+A",
                "D=M",
            ] + common_instructions

    def _write_pop(self):
        return [
            "D=D+A",
            "@13",  # first general-purpose address after temp memory segments
            "M=D",
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
            "@13",
            "A=M",
            "M=D"
        ]

    def write_push_pop(self, cmd_type, mem_seg, var_num):
        # raise ValueError(f"Unexpected push / pop value: {cmd_type}")  # >> useless if we test before
        outs = []
        var_num = str(var_num)
        if mem_seg in self._MEMORY_SEGMENT_WITH_PROGRAMMATIC_POINTER.keys():
            base_address = str(self._MEMORY_SEGMENT_WITH_PROGRAMMATIC_POINTER[mem_seg])
        elif mem_seg == "temp":
            base_address = str(5)  # first address in temp memory segment
        elif mem_seg == "static":
            if not (var_num in self._existing_static_vars.keys()):
                self._existing_static_vars[var_num] = self.input_filename + f".{var_num}"
            base_address = self._existing_static_vars[var_num]
        elif mem_seg == "pointer":
            base_address = str(3)  # THIS address
        elif mem_seg == "constant":
            pass
        else:
            raise ValueError(f"{mem_seg} is not a memory segment!!")
        if mem_seg != "constant":
            outs.extend([
                f"@{base_address}",
                "D=M" if not (mem_seg in ["temp", "pointer"]) else "D=A",
                f"@{var_num}",
            ])
        if cmd_type == "C_POP":
            outs.extend(self._write_pop())
        if cmd_type == "C_PUSH":
            outs.extend(self._write_push(mem_seg, var_num)) # no else bc filtered before calling fn
        return outs
