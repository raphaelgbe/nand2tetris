import argparse
import warnings

_BIT_LENGTH = 16

class Code:
    translate_dest = {
        "": "000",
        "M": "001",
        "D": "010",
        "MD": "011",
        "A": "100",
        "AM": "101",
        "AD": "110",
        "AMD": "111",
    }

    translate_comp = {
        "": "101010",
        "0": "101010",
        "1": "111111",
        "-1": "111010",
        "D": "001100",
        "A": "110000",
        "M": "110000",
        "!D": "001101",
        "!A":  "110001",
        "!M":  "110001",
        "-D": "001111",
        "-A": "110011",
        "-M": "110011",
        "D+1": "011111",
        "A+1": "110111",
        "M+1": "110111",
        "D-1": "001110",
        "A-1": "110010",
        "M-1": "110010",
        "D+A": "000010",
        "D+M": "000010",
        "D-A": "010011",
        "D-M": "010011",
        "A-D": "000111",
        "M-D": "000111",
        "D&A": "000000",
        "D&M": "000000",
        "D|A": "010101",
        "D|M": "010101",
    }

    translate_jump = {
        "null": "000",
        "JGT": "001",
        "JEQ": "010",
        "JGE": "011",
        "JLT": "100",
        "JNE": "101",
        "JLE": "110",
        "JMP": "111",
    }

    def translate_c_instruction(line):
        out = "111"
        if "=" in line:
            e_ind = line.find("=")
        else:
            e_ind = -1
        if ";" in line:
            comp_end = line.find(";")
        else:
            comp_end = len(line)
        if comp_end < 0:
            comp = ""
        else:
            comp = line[e_ind + 1:comp_end].strip().replace(" ", "")
        if "M" in comp:
            out += "1"
        else:
            out += "0"
        out += Code.translate_comp[comp]
        if "=" in line:
            out += Code.translate_dest[line[:e_ind].strip()]
        else:
            out += "000"
        if "J" in line:
            j_ind = line.find("J")
            out += Code.translate_jump[line[j_ind:j_ind + 3]]
        else:
            out += "000"
        return out

class SymbolicTable:
    def __init__(self):
        self.table = {f"R{i}": i for i in range(16)}
        self.table.update({
            "SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4, "SCREEN": 16384, "KBD": 24576
        })
        self.first_available_var_address = 16

    def update(self, key, value):
        self.table.update({key: value})

    def create_new_var(self, var_address):
        self.update(var_address, self.first_available_var_address)
        self.first_available_var_address += 1
        return self.table[var_address]

    def __contains__(self, key):
        return (key in self.table)

    def __getitem__(self, item):
        return self.table[item]

class Parser:
    def __init__(self, lines, symbolic_table):
        self.lines = lines
        self.symbolic_table = symbolic_table
        self.first_pass_done = False

    def first_pass(self):
        new_lines = []
        for line in self.lines:
            if line.startswith("("):
                new_label = line[line.find("(") + 1:line.find(")")]
                self.symbolic_table.update(new_label, len(new_lines))
            else:
                # by assumption it's not a pseudo-command
                new_lines.append(line)
        self.lines = new_lines
        self.first_pass_done = True

    def second_pass(self):
        #print(self.lines)
        outs = []
        if not self.first_pass_done:
            warnings.warn("Trying to do first pass before second pass! This won't work if your assembly code contains symbolic data, so make sure this isn't the case!!!")
        for line in self.lines:
            if line.startswith("@"):
                address = line[1:]
                if address in self.symbolic_table:
                    address = self.symbolic_table[address]
                else:
                    try:
                        address = int(address)
                    except ValueError:
                        address = self.symbolic_table.create_new_var(address)
                machine_language_instruction = "{0:b}".format(address).zfill(_BIT_LENGTH)
            else:
                # in this case we have a C instruction:
                machine_language_instruction = Code.translate_c_instruction(line)
            outs.append(machine_language_instruction)
        return outs

class Main:
    def __init__(self, filename):
        self.filename = filename
        self.output_filename = filename.replace(".asm", ".hack")
        self._run()

    def _write_output_file(self):
        with open(self.output_filename, "w") as f:
            #f.writelines(self.machine_language_lines)
            for line in self.machine_language_lines:
                f.write(line + "\n")

    def _get_cleaned_lines_from_filename(self):
        with open(self.filename, "r") as f:
            lines = [line.replace("\n", "").replace("\r", "").strip() for line in f.readlines()]
        lines = [line[:line.find("//")] if "//" in line else line for line in lines if (line and not line.startswith("//"))]
        return lines

    def _run(self):
        symbolic_table = SymbolicTable()
        lines = self._get_cleaned_lines_from_filename()
        parser = Parser(lines, symbolic_table)
        parser.first_pass()
        self.machine_language_lines = parser.second_pass()
        self._write_output_file()
        print(f"Done! Output file save at {self.output_filename} !")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-filename", help="Name of the .asm file to translate in machine language", type=str, required=True)
    args = parser.parse_args()
    Main(args.input_filename)