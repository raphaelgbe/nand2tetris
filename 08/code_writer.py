import os

class CodeWriter:
    _UNARY_ARITHMERIC_OPS = {"neg": "-", "not": "!"}
    _BINARY_ARITHMERIC_OPS = {"add": "+", "sub": "-", "eq": "EQ", "gt": "GT", "lt": "LT", "and": "&", "or": "|"}
    _MEMORY_SEGMENT_WITH_PROGRAMMATIC_POINTER = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}

    def __init__(self, input_filepath):
        self._input_filename = os.path.split(input_filepath)[-1].replace(".vm", "")
        self._current_function_name = ""
        self._num_calls_within = {}
        self._existing_static_vars = {}
        self._label_counter = 0

    @property
    def input_filename(self):
        return self._input_filename

    @input_filename.setter
    def input_filename(self, new_input_filepath):
        self._input_filename = os.path.split(new_input_filepath)[-1].replace(".vm", "")

    def write_init(self):
        outs = [
            "@256",
            "D=A",
            "@SP",
            "M=D"
        ]
        outs.extend(self.write_call("Sys.init", 0))
        return outs

    def write_label(self, label):
        label = self._current_function_name + f"${label}" if self._current_function_name else label
        return [f"({label})"]

    def write_goto(self, label):
        label = self._current_function_name + f"${label}" if self._current_function_name else label
        return [f"@{label}", "0;JMP"]

    def write_if(self, label):
        label = self._current_function_name + f"${label}" if self._current_function_name else label
        return ["@SP", "AM=M-1", "D=M", f"@{label}", "D;JNE"]

    def _make_function_name(self, function_name):
        return function_name #self.input_filename + '.' + function_name  # NO USE!! THAT's the user RESPONSIBILITY TO WRITE IT CLASS.METHOD!!!

    def write_call(self, function_name, num_args):
        outs = []
        if not (self._current_function_name in self._num_calls_within.keys()):
            self._num_calls_within[self._current_function_name] = 1
        else:
            self._num_calls_within[self._current_function_name] += 1
        return_label = self._current_function_name + f"$ret.{self._num_calls_within[self._current_function_name]}"
        for label in [return_label, "LCL", "ARG", "THIS", "THAT"]:
            outs += [
                f"@{label}",
                "D=A" if (label == return_label) else "D=M",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1"
            ]
        outs += ["@5", "D=A", f"@{num_args}", "D=D+A", "@SP", "D=M-D", "@ARG", "M=D"]  # ARG = SP - 5 - num-args
        outs += ["@SP", "D=M", "@LCL", "M=D"]  # LCL = SP
        outs += [f"@{function_name}", "0;JMP"]
        outs += [f"({return_label})"]
        return outs

    def write_function(self, function_name, num_locals):
        self._current_function_name = function_name  # self._make_function_name(function_name)
        outs = [f"({self._current_function_name})"]
        for i in range(num_locals):
            # since call has set LCL at SP, pushing constant 0 num_locals times will fill LCL mem seg w/ zeros and keep SP on top of it:
            outs += ["@0", "D=A"] + self.write_push_pop("C_PUSH", "constant", 0)
        return outs

    def write_return(self):
        outs = ["@LCL", "D=M", "@R14", "M=D"]  # endframe = LCL
        outs += ["@5", "D=A", "@R14", "A=M-D", "D=M", "@R15", "M=D"]  # retAddr = *(endFrame-5)
        outs += self.write_push_pop("C_POP", "argument", 0)  # *ARG=pop()
        outs += ["@ARG", "D=M+1", "@SP", "M=D"]  # SP=ARG+1
        outs += ["@R14", "A=M-1", "D=M", "@THAT", "M=D"]  # THAT=*(endFrame-1)
        outs += ["@2", "D=A", "@R14", "A=M-D", "D=M", "@THIS", "M=D"]  # THIS=*(endFrame-2)
        outs += ["@3", "D=A", "@R14", "A=M-D", "D=M", "@ARG", "M=D"]  # ARG=*(endFrame-3)
        outs += ["@4", "D=A", "@R14", "A=M-D", "D=M", "@LCL", "M=D"]  # LCL=*(endFrame-4)
        outs += ["@R15", "A=M", "0;JMP"]  # goto retAddr
        #self._current_function_name = compute_from(return_label)
        return outs

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
            "@R13",  # first general-purpose address after temp memory segments
            "M=D",
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
            "@R13",
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
            class_name = self._current_function_name.split(".")[0]
            if not (class_name in self._existing_static_vars.keys()):
                self._existing_static_vars[class_name] = {}
            if not (var_num in self._existing_static_vars[class_name].keys()):
                self._existing_static_vars[class_name][var_num] = class_name + f".{var_num}"
            base_address = self._existing_static_vars[class_name][var_num]
        elif mem_seg == "pointer":
            base_address = str(3)  # THIS address
        elif mem_seg == "constant":
            pass
        else:
            raise ValueError(f"{mem_seg} is not a memory segment!!")
        if mem_seg != "constant":
            outs.extend([
                f"@{base_address}",
                "D=M" if not (mem_seg in ["static", "temp", "pointer"]) else "D=A",
                f"@{var_num}" if (mem_seg != "static") else "@0", # rather useless in static case but keeps code more compact
            ])
        if cmd_type == "C_POP":
            outs.extend(self._write_pop())
        if cmd_type == "C_PUSH":
            outs.extend(self._write_push(mem_seg, var_num)) # no else bc filtered before calling fn
        return outs
