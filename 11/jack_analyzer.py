import argparse
import os

from jack_tokenizer import JackTokenizer
from compilation_engine import CompilationEngine
from symbol_table import SymbolTable
from vm_writer import VMWriter


class JackAnalyzer:
    def __init__(self, input_path, generate_tokens_file, generate_xml_file):
        self.generate_tokens_file = True if generate_tokens_file.lower() in ["yes", "y", "oui", "o", "true", "1"] else False
        self.generate_xml_file = True if generate_xml_file.lower() in ["yes", "y", "oui", "o", "true", "1"] else False
        self.jack_files = {}
        if os.path.isfile(input_path):
            self.jack_files[input_path] = self._open(input_path)
        else:
            for name in os.listdir(input_path):
                if not name.endswith(".jack"):
                    continue
                filename = os.path.join(input_path, name)
                self.jack_files[filename] = self._open(filename)
        self._perform_syntax_analysis()

    def _open(self, filepath):
        with open(filepath, "r") as f:
            lines = [line for line in f.readlines() if line]
        return " ".join(lines)

    def _write_output_file(self, lines_to_write, filename):
        with open(filename, "w") as f:
            for line in lines_to_write:
                f.write(line + "\n")
        print(f"File {filename} successfully written!")

    def _perform_syntax_analysis(self):
        for filename, jack_file in self.jack_files.items():
            output_xml_filename = filename.replace(".jack", "_test.xml")
            output_tokens_filename = filename.replace(".jack", "T_test.xml")
            output_filename = filename.replace(".jack", ".vm")
            tokens = ["<tokens>"]
            jt = JackTokenizer(jack_file)
            while jt.has_more_tokens():
                jt.advance()
                token_type = jt.token_type()
                if token_type == "keyword":
                    tokens.append("<keyword>" + jt.keyword() + "</keyword>")
                elif token_type == "symbol":
                    tokens.append("<symbol>" + jt.symbol() + "</symbol>")
                elif token_type == "identifier":
                    tokens.append("<identifier>" + jt.identifier() + "</identifier>")
                elif token_type == "int_val":
                    tokens.append("<integerConstant>" + jt.int_val() + "</integerConstant>")
                elif token_type == "string_val":
                    tokens.append("<stringConstant>" + jt.string_val() + "</stringConstant>")
                else:
                    raise ValueError(f"Unexpected token type!! Found {token_type}")
            tokens.append("</tokens>")
            if self.generate_tokens_file:
                self._write_output_file(tokens, output_tokens_filename)
            tokens = tokens[1:-1]  # remove useless <token> tags
            st = SymbolTable()
            vmw = VMWriter()
            ce = CompilationEngine(tokens, st, vmw)
            if self.generate_xml_file:
                self._write_output_file(ce.parsed, output_xml_filename)
            self._write_output_file(ce.vm_writer.code, output_filename)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="the path to the file/directory to apply syntaxic analysis on", type=str, required=True)
    parser.add_argument("--generate-tokens-file", help="whether or not to generate the intermediate token file", type=str, default="yes")
    parser.add_argument("--generate-xml-file", help="whether or not to generate the intermediate XML file", type=str, default="yes")
    args = parser.parse_args()

    ja = JackAnalyzer(args.input, args.generate_tokens_file, args.generate_xml_file)