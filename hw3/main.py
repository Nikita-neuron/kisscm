from sly_lexer import MyLexer
from sly_parser import MyParser
import json
import argparse

BNF = """
    <program> ::= <s-exp-list>
    <s-exp-list> ::= <s-exp> <s-exp-list> |
    <s-exp> ::= <data> | '(' <s-exp-list> ')'
    <data> ::= <INTEGER> | <STRING> | <IDENTIFIER>
"""

def get_text(file_name):
    with open(file_name, "r", encoding="utf-8") as file:
        text = file.read()
    return text

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()
    file_name = args.file

    text = get_text(file_name)
    lexer = MyLexer()
    parser = MyParser()

    tokens = lexer.tokenize(text)
    data = parser.parse(tokens)

    print(json.dumps(data, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()