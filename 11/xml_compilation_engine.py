class CompilationEngine:
    """
    Assumes a well-formatted input, containing no syntaxic error
    (so no need to check for instance that we have a curly bracket
    where we should have one, or a class name/correct type).
    """
    _UNARY_OPERATORS = set("-~")
    _BINARY_OPERATORS = set("+-*/|=").union({"&lt;", "&gt;", "&amp;"})

    def __init__(self, tokens):
        self.tokens = tokens
        self.cursor = 0
        self._current_token = self.tokens[self.cursor]
        self.parsed = []
        self.compile_class()

    @property
    def current_token(self):
        return self.tokens[self.cursor]

    def compile_class(self):
        self.parsed.extend(["<class>", self.current_token])  # extend with class tag & keyword
        self.cursor += 1
        self.parsed.append(self.current_token)  # append class name identifier
        self.cursor += 1
        self.parsed.append(self.current_token)  # append left curly bracket
        self.cursor += 1
        while (("field" in self.current_token) or ("static" in self.current_token)):
            self.compile_class_var_dec()
            self.cursor += 1
        while (("constructor" in self.current_token) or ("method" in self.current_token) or ("function" in self.current_token)):
            self.compile_subroutine()
            self.cursor += 1
        self.parsed.append(self.current_token)  # append right curly bracket
        self.parsed.append("</class>")

    def compile_class_var_dec(self):
        self.parsed.append("<classVarDec>")
        self.parsed.append(self.current_token)  # append keyword 'static' or 'field'
        self.cursor += 1
        self.parsed.append(self.current_token)  # append keyword type
        self.cursor += 1
        self.parsed.append(self.current_token)  # append variable name identifier
        self.cursor += 1
        while ("," in self.current_token):
            self.parsed.append(self.current_token)  # append ',' symbol
            self.cursor += 1
            self.parsed.append(self.current_token)  # append variable name identifier
            self.cursor += 1
        self.parsed.append(self.current_token)  # append ';' symbol
        self.parsed.append("</classVarDec>")

    def compile_subroutine(self):
        self.parsed.append("<subroutineDec>")
        self.parsed.append(self.current_token)  # append keyword 'constructor' or 'method' or 'function'
        self.cursor += 1
        self.parsed.append(self.current_token)  # append keyword 'void' or type
        self.cursor += 1
        self.parsed.append(self.current_token)  # append subroutine identifier
        self.cursor += 1
        self.parsed.append(self.current_token)  # append left parenthesis symbol
        self.cursor += 1
        if not (')' in self.current_token):
            self.compile_parameter_list()  # advances the cursor
        else:
            self.parsed.extend(["<parameterList>", "</parameterList>"])
        self.parsed.append(self.current_token)  # append right parenthesis symbol
        self.cursor += 1
        self.parsed.append("<subroutineBody>")
        self.parsed.append(self.current_token)  # append left curly bracket symbol
        self.cursor += 1
        while ('var' in self.current_token):
            self.compile_var_dec()
            self.cursor += 1
        self.compile_statements()
        self.parsed.append(self.current_token)  # append right curly bracket symbol
        self.parsed.append("</subroutineBody>")
        self.parsed.append("</subroutineDec>")

    def compile_parameter_list(self):
        self.parsed.append("<parameterList>")
        self.parsed.append(self.current_token)  # append type keyword or identifier
        self.cursor += 1
        self.parsed.append(self.current_token)  # append variable name identifier
        self.cursor += 1
        while ("," in self.current_token):
            self.parsed.append(self.current_token)  # append ',' symbol
            self.cursor += 1
            self.parsed.append(self.current_token)  # append type keyword or identifier
            self.cursor += 1
            self.parsed.append(self.current_token)  # append variable name identifier
            self.cursor += 1
        self.parsed.append("</parameterList>")

    def compile_var_dec(self):
        self.parsed.append("<varDec>")
        self.parsed.append(self.current_token)  # append 'var' keyword
        self.cursor += 1
        self.parsed.append(self.current_token)  # append type keyword or identifier
        self.cursor += 1
        self.parsed.append(self.current_token)  # append variable name identifier
        self.cursor += 1
        while ("," in self.current_token):
            self.parsed.append(self.current_token)  # append ',' symbol
            self.cursor += 1
            self.parsed.append(self.current_token)  # append variable name identifier
            self.cursor += 1
        self.parsed.append(self.current_token)  # append ';' symbol
        self.parsed.append("</varDec>")

    def compile_statements(self):
        self.parsed.append("<statements>")
        while bool(sum([(w in self.current_token) for w in {"let", "if", "while", "do", "return"}])):
            if "let" in self.current_token:
                self.compile_let()
            elif "if" in self.current_token:
                self.compile_if()
            elif "while" in self.current_token:
                self.compile_while()
            elif "do" in self.current_token:
                self.compile_do()
            elif "return" in self.current_token:
                self.compile_return()
            self.cursor += 1
        self.parsed.append("</statements>")

    def compile_do(self):
        self.parsed.append("<doStatement>")
        self.parsed.append(self.current_token)  # append 'do' keyword
        self.cursor += 1
        self.parsed.append(self.current_token)  # append first identifier (class or variable or subroutine name)
        self.cursor += 1
        while ('.' in self.current_token):
            self.parsed.append(self.current_token)  # append '.' symbol
            self.cursor += 1
            self.parsed.append(self.current_token)  # append identifier (class or variable or subroutine name)
            self.cursor += 1
        self.parsed.append(self.current_token)  # append left parenthesis symbol
        self.cursor += 1
        self.compile_expression_list()  # expression list advances the cursor (via expression)
        self.parsed.append(self.current_token)  # append right parenthesis symbol
        self.cursor += 1
        self.parsed.append(self.current_token)  # append ';' symbol
        self.parsed.append("</doStatement>")

    def compile_let(self):
        self.parsed.append("<letStatement>")
        self.parsed.append(self.current_token)  # append 'let' keyword
        self.cursor += 1
        self.parsed.append(self.current_token)  # append variable name identifier
        self.cursor += 1
        if ("[" in self.current_token):
            self.parsed.append(self.current_token)  # append left square bracket symbol
            self.cursor += 1
            self.compile_expression()  # advances cursor
            self.parsed.append(self.current_token)  # append right square bracket symbol
            self.cursor += 1
        self.parsed.append(self.current_token)  # append '=' symbol
        self.cursor += 1
        self.compile_expression()  # advances cursor
        self.parsed.append(self.current_token)  # append ';' symbol
        self.parsed.append("</letStatement>")

    def compile_while(self):
        self.parsed.append("<whileStatement>")
        self.parsed.append(self.current_token)  # append 'while' keyword
        self.cursor += 1
        self.parsed.append(self.current_token)  # append left parenthesis symbol
        self.cursor += 1
        self.compile_expression()  # advances cursor
        self.parsed.append(self.current_token)  # append right parenthesis symbol
        self.cursor += 1
        self.parsed.append(self.current_token)  # append left curly bracket symbol
        self.cursor += 1
        self.compile_statements()
        self.parsed.append(self.current_token)  # append right curly bracket symbol
        self.parsed.append("</whileStatement>")

    def compile_return(self):
        self.parsed.append("<returnStatement>")
        self.parsed.append(self.current_token)  # append 'return' keyword
        self.cursor += 1
        if not (';' in self.current_token):
            self.compile_expression()  # advances cursor
        self.parsed.append(self.current_token)  # append ';' symbol
        self.parsed.append("</returnStatement>")

    def compile_if(self):
        self.parsed.append("<ifStatement>")
        self.parsed.append(self.current_token)  # append 'if' keyword
        self.cursor += 1
        self.parsed.append(self.current_token)  # append left parenthesis symbol
        self.cursor += 1
        self.compile_expression()  # advances cursor
        self.parsed.append(self.current_token)  # append right parenthesis symbol
        self.cursor += 1
        self.parsed.append(self.current_token)  # append left curly bracket symbol
        self.cursor += 1
        self.compile_statements()
        self.parsed.append(self.current_token)  # append right curly bracket symbol
        if (len(self.parsed) > self.cursor + 1) and ('else' in self.tokens[self.cursor + 1]):
            self.cursor += 1
            self.parsed.append(self.current_token)  # append 'else' keyword
            self.cursor += 1
            self.parsed.append(self.current_token)  # append left curly bracket symbol
            self.cursor += 1
            self.compile_statements()
            self.parsed.append(self.current_token)  # append right curly bracket symbol
        self.parsed.append("</ifStatement>")

    def compile_expression(self):
        self.parsed.append("<expression>")
        self.compile_term()  # append (first) term
        self.cursor += 1
        while bool(sum([(w in self.current_token[:self.current_token.find("</")]) for w in self._BINARY_OPERATORS])):  # .find(...) used to avoid matching '/' from tag closure
            self.parsed.append(self.current_token)  # append binary operator symbol
            self.cursor += 1
            self.compile_term()
            self.cursor += 1
        self.parsed.append("</expression>")

    def compile_term(self):
        self.parsed.append("<term>")
        self.parsed.append(self.current_token)
        if bool(sum([(w in self.current_token) for w in self._UNARY_OPERATORS])):
            self.cursor += 1
            self.compile_term()
        elif ('(' in self.current_token):
            self.cursor += 1
            self.compile_expression()  # advances cursor
            self.parsed.append(self.current_token)  # append right parenthesis
        elif bool(sum([(w in self.current_token) for w in {"integerConstant", "keywordConstant", "stringConstant"}])):
            pass
        else:
            # in this case we know we start with a var/subroutine/class name
            if (len(self.parsed) > self.cursor + 1):
                if ('.' in self.tokens[self.cursor + 1]):
                    self.cursor += 1
                    while ('.' in self.current_token):
                        self.parsed.append(self.current_token)  # append '.' symbol
                        self.cursor += 1
                        self.parsed.append(self.current_token)  # append identifier (class or variable or subroutine name)
                        self.cursor += 1
                    self.cursor -= 1
                if ('[' in self.tokens[self.cursor + 1]):
                    self.cursor += 1
                    self.parsed.append(self.current_token)  # append left square bracket symbol
                    self.cursor += 1
                    self.compile_expression()  # advances the cursor by 1
                    self.parsed.append(self.current_token)  # append right square bracket symbol
                elif ('(' in self.tokens[self.cursor + 1]):
                    self.cursor += 1
                    self.parsed.append(self.current_token)  # append left parenthesis symbol
                    self.cursor += 1
                    self.compile_expression_list()  # advances the cursor by 1
                    self.parsed.append(self.current_token)  # append right parenthesis symbol
        self.parsed.append("</term>")

    def compile_expression_list(self):
        self.parsed.append("<expressionList>")
        if not (')' in self.current_token):
            self.compile_expression()  # expression advances the cursor
            while (',' in self.current_token):
                self.parsed.append(self.current_token)  # append ',' symbol
                self.cursor += 1
                self.compile_expression()
        self.parsed.append("</expressionList>")
