import JackTokenizer

INDENT_PLACE = -2

class_var_dec = ['static', 'field']

VAR = 'var'

ELSE = 'else'

unary_op = ['-', '~']

DOT = '.'

END_OF_LINE = ';'

OPEN_ROUND = '('

OPEN_SQUARE = '['

CLOSE_ROUND = ")"

COMMA = ','

CLOSE_TALTAL = '}'

SINGLE_INDENTATION = '  '

op = ['+', '-', '*', '/', '&', '|', '<', '>', '=']

CLASS = 'class'
CLASS_VAR_DEC = 'classVarDec'
SUBROUTINE_DEC = 'subroutineDec'
SUBROUTINE_BODY = 'subroutineBody'
PARAMETER_LIST = 'parameterList'
VAR_DEC = 'varDec'
LET_STATEMENT = 'letStatement'
DO_STATEMENT = 'doStatement'
EXPRESSION = 'expression'
EXPRESSION_LIST = 'expressionList'
STATEMENTS = 'statements'
RETURN_STATEMENT = 'returnStatement'
IF_STATEMENT = 'ifStatement'
WHILE_STATEMENT = 'whileStatement'
TERM = 'term'


class CompilationEngine:
    """
    This module effects the actual compilation into XML form. It gets its input from a JackTokenizer and
    writes its parsed XML structure into an output file/stream. This is done by a series of compilexxx()
    methods, where xxx is a corresponding syntactic element of the Jack grammar. The contract between these
    methods is that each compilexxx() method should read the syntactic construct xxx from the input,
    advance() the tokenizer exactly beyond xxx, and output the XML parsing of xxx. Thus,
    compilexxx()may only be called if indeed xxx is the next syntactic element of the input.
    """

    def __init__(self, input_file_path, output):
        """
        creates a new compilation engine with the given input and output. The next method called must be compileClass().
        :param input_file_path: input file path
        :param output: output file to write to
        """
        self.tokenizer = JackTokenizer.JackTokenizer(input_file_path)
        self.file = output
        self.indentation = ''
        self.statements_func_dict = {'let': self.compile_let, 'do': self.compile_do, 'while': self.compile_while,
                                     'if': self.compile_if, 'return': self.compile_return}

    def write_element(self, element, is_close=False):
        """
        writh <element> tag and handles indentation
        :param element: element
        :param is_close: is open or close tag
        :return:
        """
        if is_close:
            self.indentation = self.indentation[:INDENT_PLACE]
            self.file.write(self.indentation)
            self.file.write('</')
            self.file.write(element)
            self.file.write('>\n')
        else:
            self.file.write(self.indentation)
            self.file.write('<')
            self.file.write(element)
            self.file.write('>\n')
            self.indentation += SINGLE_INDENTATION

    def write_token(self):
        """
        write token to to the file and advances the tokenizer
        """
        token_type = self.tokenizer.token_type()
        token = JackTokenizer.token_type_dict[token_type]
        content = JackTokenizer.token_type_func_dict[token_type](self.tokenizer)
        self.file.write(self.indentation)
        self.file.write('<')
        self.file.write(token)
        self.file.write('>')
        self.file.write(JackTokenizer.SPACE)
        self.file.write(content)
        self.file.write(JackTokenizer.SPACE)
        self.file.write('</')
        self.file.write(token)
        self.file.write('>\n')
        if self.tokenizer.has_more_tokens():
            self.tokenizer.advance()

    def compile_class(self):
        """
        compiles a complete class.
        """
        # <class>
        self.tokenizer.advance()
        self.write_element(CLASS)
        # <keyword> class
        self.write_token()
        # <identifier> class_name
        self.write_token()
        # <symbol> {
        self.write_token()
        # inner class
        while self.tokenizer.get_curr_token() != CLOSE_TALTAL:
            # classVarDec
            while self.tokenizer.key_word() in class_var_dec:
                self.compile_class_var_dec()
            # subroutine
            b = self.tokenizer.token_type()
            while self.tokenizer.token_type() is JackTokenizer.TokenType.KEYWORD:
                self.compile_subroutine()
        # <symbol> }
        self.write_token()
        self.write_element(CLASS, True)

    def compile_class_var_dec(self):
        """
        compiles a static declaration or a field declaration.
        """
        self.compile_var(CLASS_VAR_DEC)

    def compile_subroutine(self):
        """
        compiles a complete method, function, or constructor.
        """
        # <subroutineDec>
        self.write_element(SUBROUTINE_DEC)
        # <keyword> constructor | function | method
        self.write_token()
        # <keyword | identifier> type
        self.write_token()
        # <identifier> subroutine name
        self.write_token()
        # <symbol> (
        self.write_token()
        self.compile_parameter_list()
        # <symbol> )
        self.write_token()
        # <subroutineBody>
        self.write_element(SUBROUTINE_BODY)
        # <symbol> {
        self.write_token()
        while self.tokenizer.key_word() == VAR:
            self.compile_var_dec()
        self.compile_statements()
        # <symbol> }
        self.write_token()
        self.write_element(SUBROUTINE_BODY, True)
        self.write_element(SUBROUTINE_DEC, True)

    def compile_parameter_list(self):
        """
        compiles a (possibly empty) parameter list, not including the enclosing Parenthesis.
        """
        # <parameterList>
        self.write_element(PARAMETER_LIST)
        while self.tokenizer.get_curr_token() != CLOSE_ROUND:
            if self.tokenizer.get_curr_token() == COMMA:
                self.write_token()
            self.write_token()
            self.write_token()
        self.write_element(PARAMETER_LIST, True)

    def compile_var_dec(self):
        """
        compiles a var declaration.
        """
        self.compile_var(VAR_DEC)

    def compile_var(self, element):
        """
        comile var
        :param element: element type - class var or var dec
        :return:
        """
        # docing is for classVarDec
        # <classVarDec>
        self.write_element(element)
        # <keyword> field | static
        self.write_token()
        # <keyword> type
        self.write_token()
        # <identifier>
        self.write_token()
        # , varName
        while self.tokenizer.get_curr_token() == COMMA:
            self.write_token()
            self.write_token()
        # <symbol> ;
        self.write_token()
        self.write_element(element, True)

    def compile_statements(self):
        """
        compiles a sequence of statements, not including the enclosing Parenthesis.
        """
        self.write_element(STATEMENTS)
        while self.tokenizer.get_curr_token() != CLOSE_TALTAL:
            self.statements_func_dict[self.tokenizer.get_curr_token()]()
        self.write_element(STATEMENTS, True)

    def compile_let(self):
        """
        Compiles a let statement
        """
        self.write_element(LET_STATEMENT)
        # let
        self.write_token()
        # varName
        self.write_token()
        if self.tokenizer.get_curr_token() == OPEN_SQUARE:
            self.pre_expression_compile()
        # =
        self.write_token()
        self.compile_expression()
        # ;
        self.write_token()
        self.write_element(LET_STATEMENT, True)

    def pre_expression_compile(self):
        """
        compiles an expression including the Parenthesis
        :return:
        """
        # [ / (
        self.write_token()
        self.compile_expression()
        # ] / )
        self.write_token()

    def compile_do(self):
        """
        Compiles a do statement
        """
        self.write_element(DO_STATEMENT)
        # do
        self.write_token()
        # subroutineName | var
        self.write_token()
        if self.tokenizer.get_curr_token() == OPEN_ROUND:
            self.pre_compile_expression_list()
        else:
            # .
            self.write_token()
            # subroutineName
            self.write_token()
            self.pre_compile_expression_list()
        # ;
        self.write_token()
        self.write_element(DO_STATEMENT, True)

    def pre_compile_expression_list(self):
        """
        compiles an expression list including the Parenthesis
        """
        # (
        self.write_token()
        self.compile_expression_list()
        # )
        self.write_token()

    def compile_while(self):
        """
        Compiles a while statement
        """
        self.write_element(WHILE_STATEMENT)
        # while
        self.write_token()
        self.pre_expression_compile()
        self.pre_statements_compile()
        self.write_element(WHILE_STATEMENT, True)

    def pre_statements_compile(self):
        """
        compiles statements including the Parenthesis
        """
        # {
        self.write_token()
        self.compile_statements()
        # }
        self.write_token()

    def compile_if(self):
        """
        compiles an if statement, possibly with a trailing else clause.
        """
        self.write_element(IF_STATEMENT)
        # if
        self.write_token()
        self.pre_expression_compile()
        self.pre_statements_compile()
        if self.tokenizer.get_curr_token() == ELSE:
            # else
            self.write_token()
            self.pre_statements_compile()
        self.write_element(IF_STATEMENT, True)

    def compile_return(self):
        """
        compiles a return statement.
        """
        self.write_element(RETURN_STATEMENT)
        # return
        self.write_token()
        if self.tokenizer.get_curr_token() != END_OF_LINE:
            self.compile_expression()
        # ;
        self.write_token()
        self.write_element(RETURN_STATEMENT, True)

    def compile_expression(self):
        """
        compiles an expression.
        """
        self.write_element(EXPRESSION)
        self.compile_term()
        while self.tokenizer.get_curr_token() in op:
            # op
            self.write_token()
            self.compile_term()
        self.write_element(EXPRESSION, True)

    def compile_term(self):
        """
        compiles a term. This method is faced with a slight difficulty when trying to decide between some of the
        alternative rules. Specifically, if the current token is an identifier, it must still distinguish between a
        variable, an array entry, and a subroutine call. The distinction can be made by looking ahead one extra
        token.
        """
        self.write_element(TERM)
        if self.tokenizer.get_curr_token() == OPEN_ROUND:
            self.pre_expression_compile()
        elif self.tokenizer.token_type() is JackTokenizer.TokenType.IDENTIFIER:
            self.write_token()
            if self.tokenizer.get_curr_token() == DOT:
                # .
                self.write_token()
                # subroutineName
                self.write_token()
                self.pre_compile_expression_list()
            elif self.tokenizer.get_curr_token() == OPEN_ROUND:
                self.pre_compile_expression_list()
            elif self.tokenizer.get_curr_token() == OPEN_SQUARE:
                self.pre_expression_compile()
        elif self.tokenizer.get_curr_token() in unary_op:
            # unaryOp
            self.write_token()
            self.compile_term()
        else:
            self.write_token()
        self.write_element(TERM, True)

    def compile_expression_list(self):
        """
        compiles a (possibly empty) comma separated list of expressions.
        """
        self.write_element(EXPRESSION_LIST)
        while self.tokenizer.get_curr_token() != CLOSE_ROUND:
            if self.tokenizer.get_curr_token() == COMMA:
                self.write_token()
            self.compile_expression()
        self.write_element(EXPRESSION_LIST, True)
