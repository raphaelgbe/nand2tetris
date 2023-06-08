class Parser:

    _COMMAND_TYPES = {
        v: k for k, vs in {
            "C_ARITHMETIC": ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"],
            "C_PUSH": ["push"],
            "C_POP": ["pop"],
            "C_LABEL": ["label"],
            "C_GOTO": ["goto"],
            "C_IF": ["if-goto"],
            "C_CALL": ["call"],
            "C_FUNCTION": ["function"],
            "C_RETURN": ["return"],
            }.items() for v in vs
    }

    def __init__(self, vm_lines):
        self.vm_lines = self._preprocess(vm_lines)
        self.current_line_id = -1

    def _preprocess(self, lines):
        lines =  [
            line[:line.find("//")].strip() if "//" in line else line. replace("\r", "").replace("\n", "")
            for line in lines if not line.startswith("//")
        ]
        return [line.strip() for line in lines if line]

    def has_more_commands(self):
        return (self.current_line_id < len(self.vm_lines) - 1)

    def advance(self):
        self.current_line_id += 1

    def command_type(self):
        return self._COMMAND_TYPES[self.vm_lines[self.current_line_id].split()[0]]

    def arg1(self):
        if self.command_type() == "C_ARITHMETIC":
            return self.vm_lines[self.current_line_id].split()[0]
        elif self.command_type() in ["C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_CALL", "C_FUNCTION"]:
            return self.vm_lines[self.current_line_id].split()[1]
        else:
            raise NotImplementedError(f"Arg 1 not implemented for other functions! Input line was {self.vm_lines[self.current_line_id]}")

    def arg2(self):
        if self.command_type() == "C_ARITHMETIC":
            raise ValueError("No arg 2 for arithmetic commands!!")
        elif self.command_type() in ["C_PUSH", "C_POP", "C_CALL", "C_FUNCTION"]:
            return int(self.vm_lines[self.current_line_id].split()[2])
        else:
            raise NotImplementedError(f"Arg 2 not implemented for other functions! Input line was {self.vm_lines[self.current_line_id]}")
