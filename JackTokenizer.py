import re
from enum import Enum

EMPTY_STRING = ''

SPACE = " "

keyword_list = ['class', 'constructor', 'function', 'method', 'field', 'static',
                'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this',
                'let', 'do', 'if', 'else', 'while', 'return']

symbol_list = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~']
symbol_dict = {'<': '&lt;', '>': '&gt;', '"': '&quot;', '&': '&amp;'}


class TokenType(Enum):
    """
    Class of Enums that represent token type
    """
    KEYWORD = 1
    SYMBOL = 2
    IDENTIFIER = 3
    INT_CONST = 4
    STRING_CONST = 5


token_type_dict = {TokenType.KEYWORD: 'keyword', TokenType.SYMBOL: 'symbol', TokenType.IDENTIFIER: 'identifier',
                   TokenType.INT_CONST: 'integerConstant', TokenType.STRING_CONST: 'stringConstant'}


class JackTokenizer:
    """
    Handles the parsing of a single .vm file, and encapsulates access to the input code. It reads VM commands,
    parses them, and provides convenient access to their components. In addition, it removes all white space and
    comments.
    """

    def __init__(self, file_path):
        """
        Constructor - Opens the input file/stream and gets ready to parse it.
        :param file_path: Input file / stream
        """
        self.file = open(file_path, 'r')
        self._jack_code = self.file.readlines()
        self.file.close()
        self._jack_code = self.clean_lines(self._jack_code)
        self._curr_index = 0
        self._length = len(self._jack_code)
        self._curr_token = None

    def has_more_tokens(self):
        """
        Are there more commands in the input?
        :return: boolean
        """
        return self._curr_index <= (self._length - 1)

    def advance(self):
        """
        Reads the next command from the input and makes it the current command. Should be called only if hasMoreCommands
        is true. Initially there is no current command.
        """
        self._curr_token = self._jack_code[self._curr_index]
        self._curr_index += 1

    def token_type(self):
        """
        Returns the type of the current VM command. C_ARITHMETIC is returned for all the arithmetic commands
        :return: C_ARITHMETIC, C_PUSH, C_POP, C_LABEL, C_GOTO, C_IF, C_FUNCTION, C_RETURN, C_CALL
        """
        if self._curr_token in symbol_list:
            return TokenType.SYMBOL
        elif self._curr_token in keyword_list:
            return TokenType.KEYWORD
        elif self._curr_token.startswith('"') and self._curr_token.endswith('"'):
            return TokenType.STRING_CONST
        elif self._curr_token.isdigit():
            return TokenType.INT_CONST
        else:
            return TokenType.IDENTIFIER

    def key_word(self):
        """
        returns the keyword which is the current token. Should be called only when tokenType() is KEYWORD.
        :return: keyword stirng
        """
        return self._curr_token

    def symbol(self):
        """
        returns the character which is the current token. Should be called only when tokenType() is SYMBOL.
        :return: char
        """
        if self._curr_token in symbol_dict:
            return symbol_dict[self._curr_token]
        return self._curr_token

    def identifier(self):
        """
        returns the identifier which is the current token. Should be called only when tokenType() is IDENTIFIER
        :return: identifier string
        """
        return self._curr_token

    def int_val(self):
        """
        returns the integer value of the current token. Should be called only when tokenType() is INT_CONST
        :return:
        """
        return self._curr_token

    def string_val(self):
        """
        returns the string value of the current token, without the double quotes. Should be called only when tokenType()
        is STRING_CONST.
        :return: string
        """
        return self._curr_token[1:-1]

    @staticmethod
    def clean_lines(file):
        """
        get an array of lines and clear the whitespaces and comments
        :param file: vm lines array
        :return: cleaned vm lines array
        """
        lines = []
        for line in file:
            if '//' in line:
                if line.count('"', 0, line.find('//')) % 2 == 0:
                    line = line[:line.find('//')]
            lines.append(line)
        one_string = EMPTY_STRING.join(lines)
        one_string = re.sub('\n', EMPTY_STRING, one_string)
        one_string = re.sub('/\*.*?\*/', EMPTY_STRING, one_string)
        string_split = one_string.split('"')
        tokens = []
        for i in range(len(string_split)):
            if i % 2 == 0:
                for symbol in symbol_list:
                    string_split[i] = string_split[i].replace(symbol, SPACE + symbol + SPACE)
                string_split[i] = re.sub(r'\s+', SPACE, string_split[i])
                tokens = tokens + string_split[i].split()
            else:
                tokens = tokens + ['"' + string_split[i] + '"']
        return tokens

    def get_curr_token(self):
        return self._curr_token


token_type_func_dict = {TokenType.KEYWORD: JackTokenizer.key_word, TokenType.SYMBOL: JackTokenizer.symbol,
                        TokenType.IDENTIFIER: JackTokenizer.identifier,
                        TokenType.INT_CONST: JackTokenizer.int_val, TokenType.STRING_CONST: JackTokenizer.string_val}
