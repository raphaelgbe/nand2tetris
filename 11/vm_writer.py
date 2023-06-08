class VMWriter:
    def __init__(self):
        self.code = []

    def write_comment(self, comment):
        self.code.append(f"// {comment}")

    def write_push(self, segment, index):
        if segment == "field":
            segment = "this"
        self.code.append(f"push {segment} {index}")

    def write_pop(self, segment, index):
        if segment == "field":
            segment = "this"
        self.code.append(f"pop {segment} {index}")

    def write_arithmetic(self, command):
        self.code.append(f"{command}")

    def write_label(self, label):
        self.code.append(f"label {label}")

    def write_goto(self, label):
        self.code.append(f"goto {label}")

    def write_if(self, label):
        self.code.append(f"if-goto {label}")

    def write_call(self, name, n_args):
        self.code.append(f"call {name} {n_args}")

    def write_function(self, name, n_locals):
        self.code.append(f"function {name} {n_locals}")

    def write_return(self):
        self.code.append(f"return")