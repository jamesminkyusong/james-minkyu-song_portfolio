import re
from lark import Lark, Transformer, Token

class color:
    # regex strings are darker/less poppy color
    # figure out packaging # setuptools -> toml
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class NatexCompiler(Transformer):
    def __init__(self, natex):
        super().__init__()
        self._natex_str = natex._natex_str
        self._ast = natex._tree
        self._debugging = natex._debugging
        self._debugging_str_literals = []
        self._debugging_str_rules = []
        self._debugging_post_literal = dict()  # (Parent(start, end), Children [starts, ends], Children (regexs))
        self._ngrams = None  # will be different in the future
        self._macros = None  # will be different in the future
        self._vars = []
        self._assignments = set()
        self._final_regex = None
        self._match_str = natex._input
        self._prev_token_len = None

    def start(self, args):
        # any time the negation is inside a flexible sequence,
        # [-hello, world]
        # any time the negation is following a flexible sequence
        # [hello, world], -goodbye
        self._final_regex = args[0]
        return args[0]

    def term(self, args):
        return Token("term", args[0], args[0].start_pos, end_pos=args[0].end_pos)

    # def find_flexible_negation_children(self, tree, rule):
    #     for node in tree:
    #         if isinstance(node, Tree):
    #             try:
    #                 if node.data == "flexible_sequence":
    #             except:
    #                 pass
    # subtree = tree.data, [t.children[0] for t in self._transform_children(tree)]
    #         if self.find_flexible_negation_children(sub_tree_list, rule):
    #             return True
    #     else:
    #         if node == rule:
    #             return True
    # return False

    def flexible_sequence(self, args):
        natex_str = ''.join([r"(?:.|\s)*?", r"(?:.|\s)*?".join(args), r"(?:.|\s)*?"])
        natex_token = Token("flexible_sequence", natex_str, args[0].start_pos, end_pos=args[-1].end_pos)
        if self._debugging:
            self._debugging_str_rules.append(natex_token)
        return natex_token

    def rigid_sequence(self, args):
        natex_str = r'\s*'.join(args)
        natex_token = Token("rigid_sequence", natex_str, args[0].start_pos, end_pos=args[-1].end_pos)
        if self._debugging:
            self._debugging_str_rules.append(natex_token)
        return natex_token

    def conjunction(self, args):
        natex_str = '.*?'.join([fr'(?=.*?{term})' for term in args]) + '.*?'
        natex_token = Token("conjunction", natex_str, args[0].start_pos, end_pos=args[-1].end_pos)
        if self._debugging:
            self._debugging_str_rules.append(natex_token)
        return natex_token

    def disjunction(self, args):
        natex_str = r'(?:{})'.format(r'|'.join([r'(?:{})'.format(term) for term in args]))
        natex_token = Token("disjunction", natex_str, args[0].start_pos, end_pos=args[-1].end_pos)
        if self._debugging:
            self._debugging_str_rules.append(natex_token)
        return natex_token

    def kleene_star(self, args):
        natex_str = r'(?:{}\s*?)*'.format(args[0])
        natex_token = Token("kleene_star", natex_str, args[0].start_pos, end_pos=args[0].end_pos)
        if self._debugging:
            self._debugging_str_rules.append(natex_token)
        return natex_token

    def negation(self, args):
        natex_str = r'(?!.*?{}.*?)'.format(args[0]) + '.*?'
        natex_token = Token("negation", natex_str, args[0].start_pos, end_pos=args[0].end_pos)
        if self._debugging:
            self._debugging_str_rules.append(natex_token)
        return natex_token

    def regex(self, args):
        natex_str = args[0]
        natex_token = Token("regex", natex_str, args[0].start_pos, end_pos=args[0].end_pos)
        if self._debugging:
            self._debugging_str_rules.append(natex_token)
        return natex_token

    def literal(self, args):
        start_bool = False
        end_bool = False
        # try making this into a different function for usage when Macro returns a String.
        literal_str = args[0]
        og_str = literal_str

        if re.fullmatch('\w', args[0][0]):
            start_bool = True
            literal_str = r'\s*\b' + literal_str
        if re.fullmatch('\w', args[0][-1]):
            end_bool = True
            if not start_bool:
                literal_str = r'\s*' + literal_str + r'\b\s*?'
            else:
                literal_str += r'\b\s*?'
        if not end_bool:
            literal_str += r'\s*'
        natex_token = Token("literal", literal_str, args[0].start_pos, end_pos=args[0].end_pos)
        if self._debugging:
            self._debugging_str_literals.append([og_str, natex_token])
        return natex_token

    def reference(self, args):
        symbol = args[0]
        if symbol in self._assignments:
            value = '(?P={})'.format(symbol)
        elif symbol in self._vars:
            value = self._vars[symbol]
        else:
            value = None
        if value == 'None':
            pass

    def assignment(self, args):
        term = args[0]
        value = args[1][0]
        natex_str = '(?P<{}>{})'.format(term, value)
        if self._debugging:
            self._debugging_str_rules.append(f"\t{'assignment':20} : {natex_str}\n")
        return natex_str

    # usage should be same, but backend is different
    # $ for both macro and variable - distinguish by try/except
    # only variable table / no separate macro table
    # provide empty variable table using match object when there's no updated vtable
    # also provide support for users who provide variable tables, (in the match and top level).
    # 3 options
        # if Macro returns false, negative lookahead
        # if Macro returns True, return ""
        # if Macro returns string,
        #   use literal padding and then return the padded regex String.
    # $myvar = $foo(1,2)
    # [$foo(1,2), x, y]
    # [$myvar = $foo(1,2), x, y]
    # [$myvar = $foo(1, $baz = $bat(1,3),
    #       x, y]

    # you can have asgmt to macro, asgmt to var
    # ref to macro, ref to var

    # think of a name proc(?) load_models(?)
    # compilation should always proceed (no early exit)

    # allowed to be variables, another macro call, assignment (these are nestable)
    # anything else that is not these are treated as string literal
    # macro() $macro()
    # var does not have () $var
    # Less Capslock
    # when macro/ var is assigned do not make a named capture group ->
    # just directly assign to the var table

    def macro(self, args):
        symbol = args[0]
        macro_args = args[1:]
        for i in range(len(macro_args)):
            if isinstance(macro_args[i], Token):
                macro_args[i] = str(macro_args[i])
        if symbol in self._macros:
            macro = self._macros[symbol]
            try:
                return macro(self._ngrams, self._vars, macro_args)
            except Exception as e:
                print('ERROR: Macro {} raised exception {}'.format(symbol, repr(e)))
                return '_MACRO_EXCEPTION_' # >>> import re; x=r'(?!x)x' # if macro returns false
        else:
            print('ERROR: Macro {} not found'.format(symbol))
            return '_MACRO_NOT_FOUND_'

    def macro_arg(self, args):
        return args[0][0]

    def macro_literal(self, args):
        pass

    def symbol(self, args):
        return args[0]

    def bracketed_sequence(self, args):
        return Token(args[0].type, args[0], args[0].start_pos, end_pos=args[0].end_pos)

    @property
    def debugging_str_literals(self):
        if len(self._debugging_str_literals)>0:
            sorted_literals = sorted(self._debugging_str_literals, key=lambda token: token[1].start_pos)
            debug_str = self._natex_str
            conversions = []
            count = 0
            prev_lens = 0
            for og_token_str, literal_token in sorted_literals:
                s = literal_token.start_pos
                e = literal_token.end_pos
                bolded_token = color.BOLD + color.GREEN + og_token_str + color.END
                literal_token = literal_token.replace(og_token_str, bolded_token)
                self._debugging_post_literal[og_token_str] = bolded_token
                if prev_lens == 0:
                    conversions.append(debug_str[:s] + literal_token + debug_str[e:])
                else:
                    conversions.append(
                        conversions[count][:s + prev_lens] + literal_token + conversions[count][e + prev_lens:])
                    count += 1
                prev_lens += len(literal_token) - len(og_token_str)
            return "\t\t\t\t" + f" {'natex literals':15} : " + conversions[-1] + "\n"
        return ""

    @property
    def debugging_str_rules(self):
        dot_line = "\n" + ". ." * 20 + "\n"
        og_str = self._natex_str
        syntax = self._debugging_str_rules
        converted_syntax = []
        for literal_token in syntax:
            s = literal_token.start_pos
            e = literal_token.end_pos
            for k, v in self._debugging_post_literal.items():
                literal_token.value = literal_token.value.replace(k, v)
            conversion = og_str[:s] + literal_token.value + og_str[e:]
            converted_syntax.append(f"\t{literal_token.type:20} : {conversion}\n")
        debug_rules_final_str = "\t\t" + "\t\t".join(converted_syntax).rstrip()
        final_regex = self._final_regex
        for k, v in self._debugging_post_literal.items():
            final_regex = final_regex.replace(k, v)
        debug_rules_final_str += "\n\n\t\t\t" + f"{'Final regex pattern':15}  : " + final_regex + dot_line
        return debug_rules_final_str


class Natex:
    grammar = r"""
            start: bracketed_sequence | rigid_sequence
            rigid_sequence: term (","? term)*
            bracketed_sequence: flexible_sequence | conjunction | disjunction | regex

            term: flexible_sequence | conjunction | disjunction | negation
                | regex | reference | kleene_star | assignment  | literal

            flexible_sequence: "[" term (","? term)* "]"
            conjunction: "<" term (","? term)* ">"
            disjunction: "{" term (","? term)* "}"

            negation: "~" term
            kleene_star: term "*"

            regex: "/" /[^\/]+/ "/"
            reference: "$" symbol ( "(" macro_arg? (","? macro_arg)* ")" )?
            assignment: "$" symbol "=" term

            macro_arg: macro_arg_string | macro_literal | reference
            macro_literal: /[^#), `][^#),`]*/
            macro_arg_string: "`" /[^`]+/ "`"

            literal: /[^ (){}\[\]<>`,\*\~\$\=\/][^(){}\[\]<>`,\*\~\$\=\/]*[^ (){}\[\]<>`,\*\~\$\=\/]|[^ (){}\[\]<>`,\*\~\$\=\/]/
                | "\"" /[^\"]+/ "\"" | "`" /[^`]+/ "`"
            symbol: /[a-z_A-Z.0-9]+/

            %import common.WS
            %ignore WS
            """

    parser = Lark(grammar, parser='earley', propagate_positions=True)

    def __init__(self, natex_str, *args, **kwargs):
        self._debugging = False
        self._debug_tree = False
        if len(args) > 0:
            debug_values = args
            if len(debug_values) > 0:
                self._debugging = debug_values[0]
                self._debug_tree = False
            if len(debug_values) > 1:
                self._debug_tree = debug_values[1]
        for key, value in kwargs.items():
            if key == "debug":
                self._debugging = value
            if key == "debug_tree":
                self._debug_tree = value
        self._input = ""
        self._natex_str = natex_str
        self._tree = Natex.parser.parse(natex_str)
        self._compiler = NatexCompiler(self)
        self._regex = self._compiler.transform(self._tree)
        self._debugging_str = ""
        self._ngrams = None
        self._macros = None
        self._vars = []
        self._assignments = set()

    def debug_str(self):
        dash_line = "\n" + "-" * 60 + "\n"
        dot_line = "\n" + ". ." * 20 + "\n"
        double_line = "\n" + "=" * 60 + "\n"
        self._debugging_str = f"{dash_line}  Natex Compilation  - "
        self._debugging_str += f"\n\t  Natex Pattern  : {self._natex_str}".rjust(10)
        self._debugging_str += f"\n\t  Match String   : {self._input}".rjust(60)
        if self._debug_tree:
            pretty_tree = self._tree.pretty()
            pretty_tree = "\n".join(["            " + s for s in pretty_tree.split("\n")]).rstrip()
            self._debugging_str += f"{dash_line}\t {'Natex AST':15} - {double_line}{pretty_tree}{double_line}"
        self._debugging_str += f"\t {'Natex Components':15} -{dot_line}\t\t\t{'Input Natex Pattern':20} : {self._natex_str}\n "

        self._debugging_str += self._compiler.debugging_str_literals
        self._debugging_str += self._compiler.debugging_str_rules
        print(self._debugging_str)

    def recompile_for_debugging(self, input_str):
        self._input = input_str
        self.debug_str()

    def match(self, input_str):
        if self._debugging:
            self.recompile_for_debugging(input_str)
        return re.fullmatch(self._regex, input_str)


if __name__ == "__main__":
    nl = ["[~food, drink, burger]", "{burger, pizza}",
        "[{eat, drink}, tomorrow]"]  # "-CS, courses, are, hard, and, fun", "<-i, really*>, love, sports", "-country, <world, city>",
    ns = [
        "let's food drink, and burger", "burger",
        "drinks tomorrow"]  # "-CS, courses, are, hard, and, fun", "<-i, really*>, love, sports", "-country, <world, city>",
    # nl = ["[{eat, drink}, tomorrow]"]  # "-CS, courses, are, hard, and, fun", "<-i, really*>, love, sports", "-country, <world, city>",
    # ns = ["drink tomorrow"]
    nfail = ["food burger drink", "pie",
             "drink today"]  # "CS courses are fun and hard", "i sports", "goodnight world cities",
    # nfail = ["drink today"] #"CS courses are fun and hard", "i sports", "goodnight world cities",

    for natex_patter, success, fail in zip(nl, ns, nfail):
        natex = Natex(natex_patter, True, True)
        print(natex_patter, success, bool(natex.match(success)))
        print(natex_patter, fail, bool(natex.match(fail)))
    natex = Natex('/[a-c]+/', True, True)
    natex.match('abccba')
    #     print("-------------------------------------")
    # natex1 = Natex('-econ, cs')
    # print(natex1.match('I cs'))
    #
    # print(natex1.match('I cs' + '.'))
    # natex.match('i love sports')
    # print(natex.match('i really really love sports'))
    # print(natex_patter, natex.match(success), natex.match(fail))
    # natex = Natex('[CS, courses, are, fun]')
    # print(natex.match('CS courses at emory are not fun' + '\n' + 'but it is essential'))  # new line does not -> CHANGED
    #
    # print(natex.match('abcdcbadd'))
