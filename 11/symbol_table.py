class SymbolTable:
    def __init__(self):
        self.class_level = {}
        self.subroutine_level = {}

    def start_subroutine(self):
        self.subroutine_level = {}

    def define(self, name, type, kind):
        index = self.var_count(kind)
        if kind.lower() in ["static", "field"]:
            self.class_level[name] = (type, kind, index)
        elif kind.lower() in ["argument", "local"]:
            self.subroutine_level[name] = (type, kind, index)
        else:
            raise ValueError(f"Unexpected kind value: {kind}.")

    def var_count(self, kind):
        if kind.lower() in ["static", "field"]:
            return len([1 for n, (t, k, i) in self.class_level.items() if (k == kind)])
        elif kind.lower() in ["argument", "local"]:
            return len([1 for n, (t, k, i) in self.subroutine_level.items() if (k == kind)])
        else:
            raise ValueError(f"Unexpected kind value: {kind}.")

    def kind_of(self, name):
        kind_index = 1
        if name in self.subroutine_level.keys():
            return self.subroutine_level[name][kind_index]
        elif name in self.class_level.keys():
            return self.class_level[name][kind_index]
        else:
            raise KeyError(f"{name} not found in symbol table!!")

    def type_of(self, name):
        type_index = 0
        if name in self.subroutine_level.keys():
            return self.subroutine_level[name][type_index]
        elif name in self.class_level.keys():
            return self.class_level[name][type_index]
        else:
            raise KeyError(f"{name} not found in symbol table!!")

    def index_of(self, name):
        index_index = 2
        if name in self.subroutine_level.keys():
            return self.subroutine_level[name][index_index]
        elif name in self.class_level.keys():
            return self.class_level[name][index_index]
        else:
            raise KeyError(f"{name} not found in symbol table!!")