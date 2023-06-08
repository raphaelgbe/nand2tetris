from symbol_table import SymbolTable
from vm_writer import VMWriter


class CompilationEngine:
    """
    Assumes a well-formatted input, containing no syntaxic error
    (so no need to check for instance that we have a curly bracket
    where we should have one, or a class name/correct type).
    """
    _UNARY_OPERATORS = {
        "-": "neg",
        "~": "not"
        }
    _BINARY_OPERATORS = {
        '*': "call Math.multiply 2",
        '|': "or",
        '&amp;': "and",
        '&gt;': "gt",
        '&lt;': "lt",
        '=': "eq",
        '-': "sub",
        '+': "add",
        '/': "call Math.divide 2"
        }
    _IF_COUNTER = 0
    _WHILE_COUNTER = 0

    def __init__(self, tokens: list, symbolic_table: SymbolTable, vm_writer: VMWriter):
        self.tokens = tokens
        self.symbolic_table = symbolic_table
        self.vm_writer = vm_writer
        self.cursor = 0
        self._current_token = self.tokens[self.cursor]
        self.parsed = []
        self.compile_class()

    @property
    def current_token(self):
        return self.tokens[self.cursor]

    @property
    def clean_token(self):
        token = self.tokens[self.cursor]
        return token[token.find(">") + 1:token.find("</")]

    def compile_class(self):
        self.parsed.extend(["<class>", self.current_token])  # extend with class tag & keyword
        self.cursor += 1
        self.parsed.append(self.current_token)  # append class name identifier
        self.class_name = self.clean_token
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
        current_kind = self.clean_token
        self.cursor += 1
        self.parsed.append(self.current_token)  # append keyword type
        current_type = self.clean_token
        self.cursor += 1
        self.parsed.append(self.current_token)  # append variable name identifier
        self.symbolic_table.define(self.clean_token, current_type, current_kind)
        self.cursor += 1
        while ("," in self.current_token):
            self.parsed.append(self.current_token)  # append ',' symbol
            self.cursor += 1
            self.parsed.append(self.current_token)  # append variable name identifier
            self.symbolic_table.define(self.clean_token, current_type, current_kind)
            self.cursor += 1
        self.parsed.append(self.current_token)  # append ';' symbol
        self.parsed.append("</classVarDec>")

    def compile_subroutine(self):
        self.symbolic_table.start_subroutine()
        self.parsed.append("<subroutineDec>")
        self.parsed.append(self.current_token)  # append keyword 'constructor' or 'method' or 'function'
        subroutine_kind = self.clean_token
        self.cursor += 1
        self.parsed.append(self.current_token)  # append keyword 'void' or type
        subroutine_return_type = self.clean_token
        self.cursor += 1
        self.parsed.append(self.current_token)  # append subroutine identifier
        subroutine_name = self.clean_token
        self.cursor += 1
        self.parsed.append(self.current_token)  # append left parenthesis symbol
        self.cursor += 1
        # for a method, we need to define the pointer as argument 0:
        if subroutine_kind == "method":
            self.symbolic_table.define("this", self.class_name, "argument")
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
        self.vm_writer.write_function(self.class_name + "." + subroutine_name, self.symbolic_table.var_count("local"))
        # for a method, the first thing to do is to set this to the correct object obtained from argument 0:
        if subroutine_kind == "method":
            self.vm_writer.write_push("argument", 0)
            self.vm_writer.write_pop("pointer", 0)
        # before getting to statements, let's create 'this' if the subroutine is a constructor:
        if subroutine_kind == "constructor":
            self.vm_writer.write_push("constant", self.symbolic_table.var_count("field"))
            self.vm_writer.write_call("Memory.alloc", 1)
            self.vm_writer.write_pop("pointer", 0)
        self.compile_statements()
        self.parsed.append(self.current_token)  # append right curly bracket symbol
        self.parsed.append("</subroutineBody>")
        self.parsed.append("</subroutineDec>")

    def compile_parameter_list(self):
        self.parsed.append("<parameterList>")
        self.parsed.append(self.current_token)  # append type keyword or identifier
        current_type = self.clean_token
        self.cursor += 1
        self.parsed.append(self.current_token)  # append variable name identifier
        self.symbolic_table.define(self.clean_token, current_type, "argument")
        self.cursor += 1
        while ("," in self.current_token):
            self.parsed.append(self.current_token)  # append ',' symbol
            self.cursor += 1
            self.parsed.append(self.current_token)  # append type keyword or identifier
            current_type = self.clean_token
            self.cursor += 1
            self.parsed.append(self.current_token)  # append variable name identifier
            self.symbolic_table.define(self.clean_token, current_type, "argument")
            self.cursor += 1
        self.parsed.append("</parameterList>")

    def compile_var_dec(self):
        self.parsed.append("<varDec>")
        self.parsed.append(self.current_token)  # append 'var' keyword
        self.cursor += 1
        self.parsed.append(self.current_token)  # append type keyword or identifier
        current_type = self.clean_token
        self.cursor += 1
        self.parsed.append(self.current_token)  # append variable name identifier
        self.symbolic_table.define(self.clean_token, current_type, "local")
        self.cursor += 1
        while ("," in self.current_token):
            self.parsed.append(self.current_token)  # append ',' symbol
            self.cursor += 1
            self.parsed.append(self.current_token)  # append variable name identifier
            self.symbolic_table.define(self.clean_token, current_type, "local")
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
        subroutine_name_split = [self.clean_token]
        self.cursor += 1
        while ('.' in self.current_token):
            self.parsed.append(self.current_token)  # append '.' symbol
            self.cursor += 1
            self.parsed.append(self.current_token)  # append identifier (class or variable or subroutine name)
            subroutine_name_split.append(self.clean_token)
            self.cursor += 1
        # if len(subroutine_name_split) == 1, this is a method call on this, so default for is_method is True here:
        is_method = True
        if len(subroutine_name_split) > 1:
            # two ways to know if method or other kind of subroutine:
            # - check if first element is object or class via capitalization of first letter
            # - check via symbol table (but if error of undefined var doesn't seem like a good approach)
            # we'll pick the first approach, thus assuming that the user respects writing conventions
            is_method = not (subroutine_name_split[0][0].isupper())
            if is_method:
                obj_name = subroutine_name_split[0]
                obj_kind, obj_type, obj_index = self.symbolic_table.kind_of(obj_name), self.symbolic_table.type_of(obj_name), self.symbolic_table.index_of(obj_name)
                self.vm_writer.write_push(obj_kind, obj_index)
                subroutine_name_split[0] = obj_type
        else:
            # in this case, subroutine_name_split is of the form [method_name], so we can simply adapt to it:
            self.vm_writer.write_push("pointer", 0)  # the method is called on this
            subroutine_name_split = [self.class_name] + subroutine_name_split
        self.parsed.append(self.current_token)  # append left parenthesis symbol
        subroutine_name = ".".join(subroutine_name_split)
        self.cursor += 1
        num_args = self.compile_expression_list() + int(is_method)  # expression list advances the cursor (via expression)
        self.vm_writer.write_call(subroutine_name, num_args)
        # do is called on void usually (& o/w doesn't retrieve return of callee) so let's just pop output
        # void subroutines are also always called using do statements in Jack, so this is practical here
        self.vm_writer.write_pop("temp", 0)
        self.parsed.append(self.current_token)  # append right parenthesis symbol
        self.cursor += 1
        self.parsed.append(self.current_token)  # append ';' symbol
        self.parsed.append("</doStatement>")

    def compile_let(self):
        self.parsed.append("<letStatement>")
        self.parsed.append(self.current_token)  # append 'let' keyword
        self.cursor += 1
        self.parsed.append(self.current_token)  # append variable name identifier
        name_assigned = self.clean_token
        type_assigned, kind_assigned, index_assigned = self.symbolic_table.type_of(name_assigned), self.symbolic_table.kind_of(name_assigned), self.symbolic_table.index_of(name_assigned)
        self.cursor += 1
        if ("[" in self.current_token):
            self.parsed.append(self.current_token)  # append left square bracket symbol
            self.cursor += 1
            self.vm_writer.write_push(kind_assigned, index_assigned)
            self.compile_expression()  # advances cursor
            self.parsed.append(self.current_token)  # append right square bracket symbol
            self.cursor += 1
            self.vm_writer.write_arithmetic("add")  #  add 'that 0' address with expression (index)
            self.parsed.append(self.current_token)  # append '=' symbol
            self.cursor += 1
            self.compile_expression()  # advances cursor
            # expects compile_expression to 'push' expression
            self.vm_writer.write_pop("temp", 0)
            self.vm_writer.write_pop("pointer", 1)  # effect: 'that' is now the array element being accessed on left-hand side
            self.vm_writer.write_push("temp", 0)
            self.vm_writer.write_pop("that", 0)
        else:
            self.parsed.append(self.current_token)  # append '=' symbol
            self.cursor += 1
            self.compile_expression()  # advances cursor
            # expects compile_expression to 'push' expression
            self.vm_writer.write_pop(kind_assigned, index_assigned)
        self.parsed.append(self.current_token)  # append ';' symbol
        self.parsed.append("</letStatement>")

    def compile_while(self):
        label_l1 = f"{self.class_name}.WHILE{self._WHILE_COUNTER}.L1"
        label_l2 = f"{self.class_name}.WHILE{self._WHILE_COUNTER}.L2"
        self._WHILE_COUNTER += 1
        self.vm_writer.write_label(label_l1)
        self.parsed.append("<whileStatement>")
        self.parsed.append(self.current_token)  # append 'while' keyword
        self.cursor += 1
        self.parsed.append(self.current_token)  # append left parenthesis symbol
        self.cursor += 1
        self.compile_expression()  # advances cursor
        self.vm_writer.write_arithmetic("not")  # negate conditional expression
        self.vm_writer.write_if(label_l2)
        self.parsed.append(self.current_token)  # append right parenthesis symbol
        self.cursor += 1
        self.parsed.append(self.current_token)  # append left curly bracket symbol
        self.cursor += 1
        self.compile_statements()
        self.parsed.append(self.current_token)  # append right curly bracket symbol
        self.vm_writer.write_goto(label_l1)
        self.vm_writer.write_label(label_l2)
        self.parsed.append("</whileStatement>")

    def compile_return(self):
        self.parsed.append("<returnStatement>")
        self.parsed.append(self.current_token)  # append 'return' keyword
        self.cursor += 1
        if not (';' in self.current_token):
            self.compile_expression()  # advances cursor
        else:
            self.vm_writer.write_push("constant", 0)  # push dummy output
        self.vm_writer.write_return()
        self.parsed.append(self.current_token)  # append ';' symbol
        self.parsed.append("</returnStatement>")

    def compile_if(self):
        label_l1 = f"{self.class_name}.IF{self._IF_COUNTER}.L1"
        label_l2 = f"{self.class_name}.IF{self._IF_COUNTER}.L2"
        self._IF_COUNTER += 1
        self.parsed.append("<ifStatement>")
        self.parsed.append(self.current_token)  # append 'if' keyword
        self.cursor += 1
        self.parsed.append(self.current_token)  # append left parenthesis symbol
        self.cursor += 1
        self.compile_expression()  # advances cursor
        self.vm_writer.write_arithmetic("not")  # negate conditional expression
        self.vm_writer.write_if(label_l1)
        self.parsed.append(self.current_token)  # append right parenthesis symbol
        self.cursor += 1
        self.parsed.append(self.current_token)  # append left curly bracket symbol
        self.cursor += 1
        self.compile_statements()
        self.vm_writer.write_goto(label_l2)
        self.vm_writer.write_label(label_l1)
        self.parsed.append(self.current_token)  # append right curly bracket symbol
        if (len(self.parsed) > self.cursor + 1) and ('else' in self.tokens[self.cursor + 1]):
            self.cursor += 1
            self.parsed.append(self.current_token)  # append 'else' keyword
            self.cursor += 1
            self.parsed.append(self.current_token)  # append left curly bracket symbol
            self.cursor += 1
            self.compile_statements()
            self.parsed.append(self.current_token)  # append right curly bracket symbol
        self.vm_writer.write_label(label_l2)
        self.parsed.append("</ifStatement>")

    def compile_expression(self):
        self.parsed.append("<expression>")
        self.compile_term()  # append (first) term
        self.cursor += 1
        while bool(sum([(w in self.current_token[:self.current_token.find("</")]) for w in self._BINARY_OPERATORS.keys()])):  # .find(...) used to avoid matching '/' from tag closure
            binary_op_command = self._BINARY_OPERATORS[self.clean_token]
            self.parsed.append(self.current_token)  # append binary operator symbol
            self.cursor += 1
            self.compile_term()
            self.vm_writer.write_arithmetic(binary_op_command)
            self.cursor += 1
        self.parsed.append("</expression>")

    def compile_term(self):
        self.parsed.append("<term>")
        self.parsed.append(self.current_token)
        if bool(sum([(w in self.current_token) for w in self._UNARY_OPERATORS.keys()])):
            unary_operator_command = self._UNARY_OPERATORS[self.clean_token]
            self.cursor += 1
            self.compile_term()
            self.vm_writer.write_arithmetic(unary_operator_command)
        elif ('(' in self.current_token):
            self.cursor += 1
            self.compile_expression()  # advances cursor
            self.parsed.append(self.current_token)  # append right parenthesis
        elif bool(sum([(w in self.current_token) for w in {"integerConstant", "keyword", "stringConstant"}])):
            if "integer" in self.current_token:
                integer = self.clean_token
                self.vm_writer.write_push("constant", integer)
            elif "string" in self.current_token:
                string_wout_quotes = self.clean_token  # jack_analyzer already removes double quotes
                self.vm_writer.write_push("constant", len(string_wout_quotes))
                self.vm_writer.write_call("String.new", 1)
                for char in string_wout_quotes:
                    self.vm_writer.write_push("constant", ord(char))  # ord(.) gets the ASCII value of its argument
                    self.vm_writer.write_call("String.appendChar", 2)
            else: # keywordConstant case
                if self.clean_token == "null":
                    self.vm_writer.write_push("constant", 0)
                elif self.clean_token == "false":
                    self.vm_writer.write_push("constant", 0)
                elif self.clean_token == "true":
                    self.vm_writer.write_push("constant", 1)
                    self.vm_writer.write_arithmetic("neg")
                elif self.clean_token == "this":
                    self.vm_writer.write_push("pointer", 0)
                else:
                    raise ValueError(f"Unexpected keyword constant value: {self.clean_token}")
        else:
            # in this case we know we start with a var/subroutine/class name
            if (len(self.parsed) > self.cursor + 1):
                first_name = self.clean_token
                subroutine_name_split = [first_name]  # only used in case of subroutine call
                if ('.' in self.tokens[self.cursor + 1]):
                    self.cursor += 1
                    while ('.' in self.current_token):
                        self.parsed.append(self.current_token)  # append '.' symbol
                        self.cursor += 1
                        self.parsed.append(self.current_token)  # append identifier (class or variable or subroutine name)
                        subroutine_name_split.append(self.clean_token)
                        self.cursor += 1
                    self.cursor -= 1
                if ('[' in self.tokens[self.cursor + 1]):
                    # NOTE: the Jack grammar excludes accessing an array without using a var name, e.g. cannot do SomeClass.someArrayAccessor()[index], but only arrayName[index]
                    self.cursor += 1
                    self.parsed.append(self.current_token)  # append left square bracket symbol
                    self.cursor += 1
                    k, i = self.symbolic_table.kind_of(first_name), self.symbolic_table.index_of(first_name)
                    self.vm_writer.write_push(k, i)
                    self.compile_expression()  # advances the cursor by 1
                    self.vm_writer.write_arithmetic("add")
                    self.vm_writer.write_pop("pointer", 1)
                    self.vm_writer.write_push("that", 0)
                    self.parsed.append(self.current_token)  # append right square bracket symbol
                elif ('(' in self.tokens[self.cursor + 1]):
                    self.cursor += 1
                    self.parsed.append(self.current_token)  # append left parenthesis symbol
                    self.cursor += 1
                    is_method = not (subroutine_name_split[0][0].isupper())  # as explained in compile_do ; actually no need to test subroutine_name_split len, but let's leave it for clarity above
                    if is_method:
                        if len(subroutine_name_split) > 1:
                            # first element is an object we want to call the method on, so let's proceed as previously in compile_do:
                            obj_name = subroutine_name_split[0]
                            obj_kind, obj_type, obj_index = self.symbolic_table.kind_of(obj_name), self.symbolic_table.type_of(obj_name), self.symbolic_table.index_of(obj_name)
                            self.vm_writer.write_push(obj_kind, obj_index)
                            subroutine_name_split[0] = obj_type
                        else:
                            subroutine_name_split = [self.class_name] + subroutine_name_split
                            self.vm_writer.write_push("pointer", 0)
                    num_args = self.compile_expression_list() + int(is_method)  # advances the cursor by 1
                    subroutine_name = ".".join(subroutine_name_split)
                    self.vm_writer.write_call(subroutine_name, num_args)
                    # NOTE: the Jack grammar doesn't allow the call subroutine to be void in expressions (which makes sense really)
                    self.parsed.append(self.current_token)  # append right parenthesis symbol
                else:
                    # in this case no array access nor subroutine call, so since previous ifs ruled out expressions/constants, must be var name
                    # NOTE: this also implies that there was no '.' detected in last while loop, as fields can only be accessed via accessors in Jack
                    k, i = self.symbolic_table.kind_of(first_name), self.symbolic_table.index_of(first_name)
                    self.vm_writer.write_push(k, i)
        self.parsed.append("</term>")

    def compile_expression_list(self):
        self.parsed.append("<expressionList>")
        num_expressions = 0
        if not (')' in self.current_token):
            self.compile_expression()  # expression advances the cursor
            num_expressions += 1
            while (',' in self.current_token):
                self.parsed.append(self.current_token)  # append ',' symbol
                self.cursor += 1
                self.compile_expression()
                num_expressions += 1
        self.parsed.append("</expressionList>")
        return num_expressions
