class JackTokenizer:
    _SPECIAL_SYMBOLS_MAP = {"<": "&lt;", ">": "&gt;", '"': "&quot;", "&": "&amp;"}
    _SYMBOLS = set("{}()[]<>.,;+*-/&|=~")
    _KEYWORDS = {"class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean", "void", "true", "false", "null", "this", "let", "do", "if", "else", "while", "return"}

    def __init__(self, code):
        self.code = self._remove_noise(code)
        self.current_token = None
        self._token_type = None

    def _remove_noise(self, txt):
        """Do a first pass to remove comments"""
        double_quotes_count = 0
        remove_up_to = -1
        for i, c in enumerate(txt):
            if c == '"':
                double_quotes_count += 1
            elif c == "/":
                if (double_quotes_count % 2): # maybe we are in a string, between double-quotes??? then skip!
                    continue
                if (i < len(txt) - 1):
                    if txt[i + 1] == "/":
                        remove_up_to = txt[i + 1:].find("\n")
                        if remove_up_to == -1:
                            remove_up_to = len(txt)
                            txt_to_process = ""
                        else:
                            txt_to_process = txt[i + 1 + remove_up_to + 1:]
                        break
                    elif txt[i + 1] == "*":
                        remove_up_to = txt[i + 1:].find("*/")
                        txt_to_process = txt[i + 1 + remove_up_to + 2:]
                        break
                    else:
                        pass
        if remove_up_to >= 0:
            out = txt[:i] + self._remove_noise(txt_to_process)
        else:
            out = txt
        return out.replace("\r\n", " ").replace("\n", " ").strip()

    def has_more_tokens(self):
        if self.code:  # given that comments & new lines are removed, only whitespaces & token elements left, but removed at each update so no processing necessary
            return True
        return False

    def advance(self):
        if self.code[0] in self._SYMBOLS:
            self.current_token = self.code[0]
            i = 1
            self._token_type = "symbol"
        elif self.code[0] == '"':
            i = self.code[1:].find('"')
            self.current_token = self.code[1:i + 1]
            i += 2
            self._token_type = "string_val"
        elif self.code[0].isnumeric():
            i = 1
            while self.code[i].isnumeric():
                i += 1
            self.current_token = self.code[:i]
            self._token_type = "int_val"
        elif self.code[0].isalpha():
            i = 1
            while (self.code[i].isalpha() or (self.code[i] == "_") or self.code[i].isnumeric()):
                i += 1
            self.current_token = self.code[:i]
            self._token_type = "keyword" if (self.current_token in self._KEYWORDS) else "identifier"
        else:
            raise ValueError(f"Unexpected code characters encountered! Here's beginning of what's left to process in the code:\n {self.code[:100]}")
        self.code = self.code[i:].lstrip()

    def token_type(self):
        return self._token_type

    def keyword(self):
        return self.current_token

    def symbol(self):
        if self.current_token in self._SPECIAL_SYMBOLS_MAP.keys():
            return self._SPECIAL_SYMBOLS_MAP[self.current_token]
        return self.current_token

    def identifier(self):
        return self.current_token

    def int_val(self):
        return self.current_token

    def string_val(self):
        return self.current_token