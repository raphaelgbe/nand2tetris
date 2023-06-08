import argparse
import os
from collections import OrderedDict # actually useless but to keep things "clean"

from vm_parser import Parser
from code_writer import CodeWriter

class Main:
    def __init__(self, input_path):
        self.vm_files = OrderedDict()
        self.is_directory = False
        if os.path.isfile(input_path):
            print(f"Translating input file {input_path}!")
            with open(input_path, "r") as f:
                self.vm_files[input_path] = f.readlines() #self._preprocess(f.readlines())
            self.output_filename = input_path.replace(".vm", ".asm")
        elif os.path.isdir(input_path):
            print(f"Translating input directory {input_path}!")
            self.is_directory = True
            for filename in os.listdir(input_path):
                if not filename.endswith(".vm"):
                    continue
                input_filename = os.path.join(input_path, filename)
                with open(input_filename, "r") as f:
                    self.vm_files[input_filename] = f.readlines() #self._preprocess(f.readlines())
            dirname = os.path.basename(os.path.normpath(input_path))
            self.output_filename = os.path.join(input_path, dirname + ".asm")
        else:
            raise ValueError(f"{input_path} is not a valid file/directory path!")
        self.code_writer = CodeWriter(list(self.vm_files.keys())[0]) # the reason why OrderedDict instead of dict ; useless though bc while looping will change it
        self._run()

    def _write_output_file(self, outs):
        with open(self.output_filename, "w") as f:
            for line in outs:
                f.write(line + "\n")

    def _run(self):
        outs = self.code_writer.write_init() if self.is_directory else []
        for input_filename, vm_lines in self.vm_files.items():
            self.parser = Parser(vm_lines)  # change parser to apply on new file VM lines
            self.code_writer.input_filename = input_filename  # change filename for labels that keep track of class name
            while self.parser.has_more_commands():
                self.parser.advance()
                cmd_type = self.parser.command_type()
                outs += ["//" + self.parser.vm_lines[self.parser.current_line_id]]  # write original VM lines
                if cmd_type == "C_ARITHMETIC":
                    outs += self.code_writer.write_arithmetic(self.parser.arg1())
                elif cmd_type in ["C_PUSH", "C_POP"]:
                    outs += self.code_writer.write_push_pop(cmd_type, self.parser.arg1(), self.parser.arg2())
                elif cmd_type == "C_LABEL":
                    outs += self.code_writer.write_label(self.parser.arg1())
                elif cmd_type == "C_GOTO":
                    outs += self.code_writer.write_goto(self.parser.arg1())
                elif cmd_type == "C_IF":
                    outs += self.code_writer.write_if(self.parser.arg1())
                elif cmd_type == "C_CALL":
                    outs += self.code_writer.write_call(self.parser.arg1(), self.parser.arg2())
                elif cmd_type == "C_FUNCTION":
                    outs += self.code_writer.write_function(self.parser.arg1(), self.parser.arg2())
                elif cmd_type == "C_RETURN":
                    outs += self.code_writer.write_return()
                else:
                    raise NotImplementedError(f"Command type {cmd_type} not found !!")
        self._write_output_file(outs)
        print(f"Done! Output Hack assembly file can be found at {self.output_filename}")

if __name__ == "__main__":
    # if bug just make sure
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Path to input file/directory", type=str, required=True)
    args = parser.parse_args()

    Main(args.input)