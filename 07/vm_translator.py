import argparse

from vm_parser import Parser
from code_writer import CodeWriter

class Main:
    def __init__(self, input_filename):
        with open(input_filename, "r") as f:
            self.vm_lines = f.readlines() #self._preprocess(f.readlines())
        self.output_filename = input_filename.replace(".vm", ".asm")  # assuming no '.vm' anywhere else than in the extension of the filepath
        self.parser = Parser(self.vm_lines)
        self.code_writer = CodeWriter(input_filename)
        self._run()

    def _write_output_file(self, outs):
        with open(self.output_filename, "w") as f:
            for line in outs:
                f.write(line + "\n")

    def _run(self):
        outs = []
        while self.parser.has_more_commands():
            self.parser.advance()
            cmd_type = self.parser.command_type()
            outs += ["//" + self.parser.vm_lines[self.parser.current_line_id]]  # write original VM lines
            if cmd_type == "C_ARITHMETIC":
                outs += self.code_writer.write_arithmetic(self.parser.arg1())
            elif cmd_type in ["C_PUSH", "C_POP"]:
                outs += self.code_writer.write_push_pop(cmd_type, self.parser.arg1(), self.parser.arg2())
            else:
                raise NotImplementedError("Translation not implemented yet for branching & call/function/return types")
        self._write_output_file(outs)
        print(f"Done! Output Hack assembly file can be found at {self.output_filename}")

if __name__ == "__main__":
    # if bug just make sure
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Path to input file", type=str, required=True)
    args = parser.parse_args()

    Main(args.input)