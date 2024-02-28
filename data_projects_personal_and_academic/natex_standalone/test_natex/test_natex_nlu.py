# from legacy.knowledge_base import KnowledgeBase
# from legacy.dialogue_flow import DialogueFlow, Speaker
from enum import Enum
from natex.natex_nlu import Natex


def test_flexible_sequence():
    natex = Natex('[quick, fox, brown, dog]', True, True)
    assert natex.match('the quick fox jumped over the brown dog')
    assert not natex.match('fox quick brown dog')
    assert not natex.match('')

def test_rigid_sequence():
    natex = Natex('quick, fox, brown, dog', True, False)
    assert natex.match('quick fox brown dog')
    assert not natex.match('the quick fox brown dog')

def test_disjunction():
    natex = Natex('{quick, fox, brown, dog}', debug=True, debug_tree=True)
    assert natex.match('fox')
    assert natex.match('dog')
    assert not natex.match('the dog')

def test_conjunction():
    natex = Natex('<quick, fox, brown, dog>', True)
    assert natex.match('the quick fox and the brown dog')
    assert natex.match('the brown fox and the quick dog')
    assert not natex.match('the fox and the quick dog')

# \bi\b\s*(?:\breally\b)*\s*\blove\b\s*\bsports\b
def test_kleene_star():
    natex = Natex('i, really*, love, sports')
    assert natex.match('i really love sports')
    assert natex.match('i love sports')
    assert natex.match('i really really love sports')
    assert natex.match('i love sports')

def test_negation():
    natex = Natex('~{bad, horrible, not}', True)
    assert natex.match('i am good')
    assert natex.match('good')
    assert not natex.match('i am not good')
    assert not natex.match('i am horrible')
    assert not natex.match('bad')
    natex = Natex('~bad, [good]', True)
    # natex = Natex('~bad [good]')
    assert natex.match('good')
    assert not natex.match('bad but good',)
    assert not natex.match('good but bad')
    assert natex.match('im good sort of')
    assert not natex.match('im good sort of but bad')
    assert not natex.match('im bad but also good')

def test_regex():
    natex = Natex('/[a-c]+/', True, True)
    assert natex.match('abccba')
    assert not natex.match('abcdabcd')

def test_flexible_sequence_base():
    natex = Natex('[CS, courses, are, fun]')  # need to use everything in order

    assert natex.match('CS courses are fun')
    assert natex.match(' CS courses are fun')  # allows leading spaces
    assert natex.match('CS courses are fun' + ' ')  # not trailing spaces ->CHANGED

    assert not natex.match('are CS courses fun or not')  # order of natex matters
    assert not natex.match('cs 253 is not fun')
    assert natex.match('CS courses are fun.')  # symbols not allowed -> CHANGED

def test_flexible_sequence_edge():
    natex = Natex('[CS, courses, are, fun]')  # need to use everything in order
    assert natex.match('CS.courses.are.fun')  # is this expected? # flag
    assert natex.match('CS.courses are.fun.fun')
    assert natex.match('CS.courses.are.fun.fun.') # CHANGED
    assert natex.match('The CS courses at emory are not fun' + '  ' + 'but it is essential')
    assert natex.match('CS courses at emory are not fun' + '\t' + 'but it is essential')  # tab matches
    assert natex.match('CS courses at emory are not fun' + '\n' + 'but it is essential')  # new line does not -> CHANGED

# get rid of brackets [ ]
def test_rigid_sequence_base():
    natex = Natex('CS, courses, are, hard, and, fun', True, True)

    assert natex.match('CS courses are hard and fun')
    assert not natex.match('CS courses are hard but fun')
    assert not natex.match('CS courses are not hard')
    assert not natex.match(' ' + 'CS courses are hard')
    # assert not natex.match('CS courses are hard' + ' ')
    # assert not natex.match('CS courses are hard' + ' ')
    # assert not natex.match('!CS course are hard')
    # assert not natex.match('CS course are not hard')

def test_rigid_sequence_edge():
    natex = Natex('CS, courses, are, hard')
    assert not natex.match('CS!courses!are!hard')  # is this normal? -> CHANGED
    assert not natex.match('CS!courses!are!hard!') # -> CHANGED
    assert natex.match('CS courses' + '  ' + 'are hard')
    assert natex.match('CS courses' + '\t' + 'are hard')
    assert natex.match('CS courses' + '\n' + 'are hard')
    # new line in the middle allowed, but not allowed in flexible sequence


# disjunction is a set {} that matches whether
# the input string is one of the values in the set

def test_disjunction_base():
    natex = Natex('{I enjoy coding, coding, fun, cs}', True)
    assert natex.match('I enjoy coding')
    assert natex.match('I enjoy coding' + ' ') # -> CHANGED

    assert natex.match('coding')
    assert natex.match('fun')
    assert not natex.match('Cs')

def test_disjunction_edge():
    natex = Natex('{I enjoy coding, coding, fun, cs}')
    assert not natex.match('I!enjoy!coding')
    assert not natex.match('I enjoy' + '  ' + 'coding')
    assert not natex.match('I enjoy' + '\t' + 'coding')
    assert not natex.match('I enjoy' + '\n' + 'coding')
    assert natex.match('\t' + 'cs')
    assert natex.match('cs' + '\t') # -> CHANGED


# conjunction is enclosed in <>
def test_conjunction_base():
    natex = Natex('<CS, courses, are, hard>')
    assert natex.match('CS courses are hard')
    assert natex.match('CS courses are hard' + ' ')
    assert natex.match('CS courses are hard' + '.') # This should match + line 166 output is correct.

    assert natex.match('hard they are, courses of CS')  # order doesn't matter

    assert not natex.match('MATH courses are hard')  # generic fail case

def test_conjunction_edge():
    natex = Natex('<CS, courses, are, hard>')
    assert natex.match('CS courses !are hard')
    assert natex.match('!CS,courses,are,hard.123')
    assert not natex.match('!CS,courses,are,hard123')

    assert natex.match('"CS"courses"are"hard"')
    assert natex.match('"CS"" ""courses"" ""are"" ""hard"')

    assert natex.match('CS courses' + '  ' + 'are hard')
    assert natex.match('CS courses' + '\t' + 'are hard')
    assert not natex.match('CS courses' + '\n' + 'are hard')  # new line doesn't


def test_negation_base():
    natex1 = Natex('~{math, econ}, like, cs')
    assert natex1.match('I like cs')
    assert natex1.match('I like cs')
    assert natex1.match('  ' + 'I like cs')
    assert natex1.match('I like' + ' ' + 'cs')

    natex2 = Natex('I like, {cs, ~math, ~econ}')  # negation needs to be first
    assert natex2.match('I like cs')
    assert natex2.match('I like math')  # this could match

def test_negation_edge():
    natex1 = Natex('~{math, econ}, like, cs')
    assert natex1.match('.' + 'I like cs') # -> CHANGED
    assert natex1.match('I like cs' + ' ') # -> CHANGED
    assert not natex1.match('I like cs' + '.') # -> CHANGED
    assert natex1.match('I like' + '  ' + 'cs')
    assert natex1.match('I like' + '\t' + 'cs')
    assert natex1.match('I like' + '\n' + 'cs')

def test_regex_base():
    natex = Natex('/[a-zA-Z]+/, like, cs, /[0-9]+/', True, True)
    assert natex.match('I like cs 253')
    assert not natex.match('I like ! cs 171')  # should this work?!

    assert not natex.match('I like cs171')
    assert not natex.match('I like cs' + ' ')
    assert not natex.match('I like cs' + '.')
    assert not natex.match('I like cs 171!')

def test_regex_edge():
    natex = Natex('/[a-zA-Z]+/, like, cs, /[0-9]+/')
    assert natex.match('I like' + '\t' + 'cs 253')
    assert natex.match('I like' + '\n' + 'cs 370')
    assert natex.match('I like' + '  ' + 'cs 170')

def test_literals():
    natex = Natex("`hello world`", True, True)
    assert natex.match("hello world")
    natex = Natex('`"hello world"`', True, True)
    assert natex.match('"hello world"')

# def test_reference_base():
#     v1 = {'A': 'cs', 'B': 'nlp', 'C': 'math'}
#     natex1 = Natex('my favorite subject is, {$A, $B, $C}')
#
#     assert natex1.match('my favorite subject is cs', vars=v1)
#     assert natex1.match('my favorite'+' '+'subject is cs', vars=v1)
#
#     assert natex1.match('my favorite subject is nlp', vars=v1)
#     assert not natex1.match('my favorite subject is econ', vars=v1)
#
#     natex2 = Natex('{$A, $B, $C} is my favorite subject')
#     assert natex2.match('cs is my favorite subject', vars=v1)
#
#
# def test_reference_edge():
#     v1 = {'A': 'cs', 'B': 'nlp', 'C': 'math'}
#     natex1 = Natex('my favorite subject is, {$A, $B, $C}')
#     assert natex1.match('my favorite subject is'+'\t'+'cs', vars=v1)  # check flag
#     assert natex1.match('my favorite subject is'+'\n'+'cs', vars=v1)  # check flag
#     assert not natex1.match('my favorite subject is cs.', vars=v1)
#
#     natex2 = Natex('{$A, $B, $C} is my favorite subject')
#     assert natex2.match('cs'+'\t'+'is my favorite subject', vars=v1) # check flag
#     assert natex2.match('cs'+'\n'+'is my favorite subject', vars=v1) # check flag
#
# def test_assignment():
#     v = {'A': 'cs'}
#     natex = Natex('i took, {a, an}, $A={econ, math} class today')
#     assert not natex.match('i took a cs class today', vars=v)
#     assert natex.match('i took an econ class today', vars=v)
#     assert v['A'] == 'econ'
#     assert natex.match('i took a math class today', vars=v)
#     assert v['A'] == 'math'

# fix
# commas
# build test cases for these
# and  raise compiler error for specific cases
# works
# -{x, y} standard way
# {-x, -y} not x or not y so weird
# -<x,y>
# <-x,-y>
# -[x,y]
# [-x, -y] compiler error when negation is directly inside flexible sequence
# -x works
# [x] -y negation has to be the first

# regex
def test_integration_flexible_negation_base():
    # pre appends .* (eats up everything) then checking negation (doesn't work)
    natex = Natex('~cs, [is, very, fun]') # '-cs [is, very, fun]' is the CORRECT SYNTAX # pytest raises
    assert natex.match('math is very fun')
    assert natex.match('math is' + ' ' + 'very fun')
    assert natex.match(' ' + 'math is very fun')  # should work
    assert not natex.match('cs is very fun')
    # we want to have a compiler error specifically, when negation is used inside the sequence

def test_integration_flexible_negation_edge():
    natex = Natex('~cs, [is, very, fun]')
    assert not natex.match('math is' + '\n' + 'very fun')  # flag # -> CHANGED
    assert natex.match('math is' + '  ' + 'very fun')
    assert natex.match('math is' + '\t' + 'very fun')
    assert natex.match('math is' + '!' + 'very fun')  # should work
    assert natex.match('math is very fun' + ' ') # -> CHANGED
    assert natex.match('math is very fun' + '.') # -> CHANGED

# what this should be doing:
# ending with "fun" and "boring" should only match and everything else should fail.
def test_integration_rigid_sequence_negation_base():
    natex1 = Natex('~cs, is, very, {fun, boring}') # {fun, boring} automatically under rigid
    assert natex1.match('math is very fun')
    assert natex1.match('math is very boring')
    assert not natex1.match('math is very exciting')
    assert natex1.match('math is'+' '+'very fun')

    natex2 = Natex('~cs, ~is, very, {fun, boring}')
    assert natex2.match('courses are very fun')
    assert not natex2.match('math is very fun')  # matches is # -> NOT CHANGED NEED FIX
    # may have to fix how negation is handled in rigid sequence,
    # by re-writing the natex string inside the compiler.

def test_integration_rigid_sequence_negation_edge():
    natex1 = Natex('~cs, is, very, {fun, boring}')
    assert natex1.match('math is'+'  '+'very boring')
    assert natex1.match('math is'+'\t'+'very fun')
    assert not natex1.match('math is'+'\n'+'very fun')  # new line flag
    assert not natex1.match('econ!is!very!fun')  # this works

    natex2 = Natex('~cs, ~is, very, {fun, boring}')
    assert natex2.match('courses!are!very!fun')  # this works
    assert not natex2.match('math.is.very.fun')  # matches is
    assert not natex2.match('math ? very fun') # symbol is not being handled
    assert natex2.match('cs is very fun')  # does not match cs



# negation fix needed
# negation is eating up everything
# NOT -> CHANGED
def test_integration_disjunction_negation_base():
    natex2 = Natex('~{cs}')
    assert not natex2.match('cs'+'\t')
    assert not natex2.match('cs'+' ')
    assert not natex2.match('cs'+'  ')
    assert not natex2.match('c.cs')
    assert not natex2.match('math.')  # symbols still same result

    natex3 = Natex('~{cs, nlp, econ}')
    assert not natex3.match('cs')
    assert not natex3.match('cs'+' ')
    assert not natex3.match('cs'+'  ')

    assert not natex3.match('nlp')
    assert not natex3.match('econ')
    assert natex3.match('good')
    assert natex3.match('good'+' ')
    assert natex3.match(' '+'good')
    assert not natex3.match('econ.nlp.cs')
    assert not natex3.match('how is cs?')
    assert not natex3.match('how fun is nlp?')
    assert natex3.match('how interesting is economics?')
    assert natex3.match('is math fun?')

def test_integration_conjunction_negation():
    natex1 = Natex('<~math, food>')
    assert natex1.match('hello food')
    assert natex1.match(' food 123 ')
    assert natex1.match('cs food ')
    assert not natex1.match('food math')  # check whether math food works
    assert not natex1.match('math food')
    assert natex1.match('food')

    natex2 = Natex('~<math, food>')  # NOT (both math AND food)
    assert natex2.match('hello')
    assert not natex2.match('food')
    assert not natex2.match('math')
    assert not natex2.match('math food')
    assert natex2.match('math drink')
    assert natex2.match('science drink')
    assert natex2.match('science food')
    assert natex2.match('science drink')
    assert natex2.match('science'+' '+'drink')
    assert natex2.match('science'+'\t'+'drink')
    assert not natex2.match('science'+'\n'+'drink')

# def test_reference():
#     v1 = {'A': 'apple', 'B': 'brown', 'C': 'charlie'}
#     v2 = {'C': 'candice'}
#     natex = Natex('i saw $C today')
#     assert natex.match('i saw charlie today', vars=v1,)
#     assert natex.match('i saw charlie today',) is None
#     assert not natex.match('i saw candice today', vars=v1)
#     assert natex.match('i saw candice today', vars=v2)
#
# def test_assignment():
#     v = {'A': 'apple'}
#     # natex = Natex('i ate a $A={orange, raddish} today')
#     natex = Natex('i ate a, $A={orange, raddish}, today')
#
#     assert natex.match('i ate a orange today', vars=v)
#     assert v['A'] == 'orange'
#     assert natex.match('i ate a raddish today', vars=v)
#     assert v['A'] == 'raddish'
#     assert natex.match('i ate a raddish today')
#     assert not natex.match('i ate a carrot today', vars=v)
#     natex = Natex('i ate a, $B={orange, raddish}, today')
#     assert natex.match('i ate a raddish today', vars=v)
#     assert v['B'] == 'raddish'
#
# def test_assignment_within_disjunction():
#     vars = {}
#     natex = Natex('{$A=hello, $A=hi}')
#     assert natex.match('hello', vars=vars)
#     assert vars['A'] == 'hello'
#     vars = {}
#     assert natex.match('hi', vars=vars,)
#     assert vars['A'] == 'hi'
#
# def test_backreference():
#         # natex = Natex('$A good eat $A={apple, banana}')
#     natex = Natex('$A, good, eat, $A={apple, banana}')
#
#     v = {'A': 'apple'}
#     assert natex.match('apple good eat banana', vars=v,)
#     assert v['A'] == 'banana'
#     # natex = Natex('$A={apple, banana} good eat $A')
#     natex = Natex('$A={apple, banana}, good, eat, $A')
#
#     v = {'A': 'apple'}
#     assert natex.match('banana good eat banana', vars=v,)
#     assert v['A'] == 'banana'
#     assert not natex.match('apple good eat banana',)
#     assert v['A'] != 'apple'
#
# def SIMPLE(ngrams, vars, args):
#     return {'foo', 'bar', 'bat', 'baz'}
#
# def HAPPY(ngrams, vars, args):
#     if ngrams & {'yay', 'hooray', 'happy', 'good', 'nice', 'love'}:
#         vars['SENTIMENT'] = 'happy'
#         return True
#     else:
#         return False
#
# def FIRSTS(ngrams, vars, args):
#     firsts = ''
#     for arg in args:
#         if isinstance(arg, str) and arg[0] == '$':
#             arg = vars[arg[1:]]
#         firsts += arg[0]
#     return {firsts, firsts[::-1]}
#
# def SET(ngrams, vars, args):
#     return set(args)
#
# def INTER(ngrams, vars, args):
#     return set.intersection(*args)
#
# def MOVIE(ngrams, vars, args):
#     return ngrams & {'Avengers', 'Star Wars'}
#
# macros = {'SIMPLE': SIMPLE, 'HAPPY': HAPPY, 'FIRSTS': FIRSTS, 'INTER': INTER, 'SET': SET, 'MOVIE': MOVIE}
#
# def test_simple_macro():
#     # natex = Natex('i #SIMPLE', macros=macros)
#     natex = Natex('i, #SIMPLE', macros=macros)
#     assert natex.match('i foo')
#     assert natex.match('i bar')
#     assert not natex.match('i err')
#     # natex = Natex('i #SIMPLE()', macros=macros)
#     natex = Natex('i, #SIMPLE()', macros=macros)
#
#     assert natex.match('i foo')
#     assert natex.match('i bar')
#     assert not natex.match('i err')
#
# def test_macro_with_args():
#     v = {'X': 'carrot'}
#     natex = Natex('#FIRSTS(apple, banana, $X)', macros=macros)
#     assert natex.match('abc', vars=v,)
#     assert natex.match('cba', vars=v)
#
# def test_macro_with_assignment():
#     v = {}
#     natex = Natex('#HAPPY', macros=macros)
#     assert natex.match('i am good today', vars=v,)
#     assert v['SENTIMENT'] == 'happy'
#     assert not natex.match('i am bad')
#
# def test_nested_macro():
#     natex = Natex('#INTER(#SET(apple, banana), #SET(apple, orange))', macros=macros)
#     assert natex.match('apple',)
#     assert not natex.match('orange')
#
# def test_sigdial_natex1():
#     natex = Natex('[{have, did} you {seen, watch} $MOVIE={avengers, star wars}]', macros=macros)
#     assert natex.match('so have you seen avengers')
#
# def test_sigdial_natex2():
#     natex = Natex('[I {watched, saw} $MOVIE={avengers, star wars}]', macros=macros)
#     assert natex.match('last night I saw avengers')
#
# class States(Enum):
#     A = 0
#     B = 1
#     C = 2
#     D = 3
#     E = 4
#
# def test_ontology():
#     kb = KnowledgeBase()
#     ontology = {
#         "ontology": {
#             "season": [
#                 "fall",
#                 "spring",
#                 "summer",
#                 "winter"
#             ],
#             "month": [
#                 "january",
#                 "february",
#                 "march",
#                 "april",
#                 "may",
#                 "june",
#                 "july",
#                 "august",
#                 "september",
#                 "october",
#                 "november",
#                 "december"
#             ]
#         }
#     }
#     kb.load_json(ontology)
#     df = DialogueFlow(States.A, Speaker.USER, kb=kb)
#     df.add_state(States.A)
#     df.add_state(States.B)
#     df.add_state(States.C)
#     df.add_state(States.D)
#     df.add_state(States.E)
#     df.set_error_successor(States.A, States.E)
#     df.set_error_successor(States.B, States.E)
#     df.set_error_successor(States.C, States.E)
#     df.set_error_successor(States.D, States.E)
#     df.add_user_transition(States.A, States.B, "[#ONT(month)]")
#     df.add_system_transition(States.B, States.C, "B to C")
#     df.add_user_transition(States.C, States.D, "[$m=#ONT(month), $s=#ONT(season)]")
#
#     df.user_turn("january")
#     assert df.state() == States.B
#     assert df.system_turn() == "B to C"
#     df.user_turn("october is in the fall season")
#     assert df.state() == States.D
#     assert df._vars["m"] == "october"
#     assert df._vars["s"] == "fall"
#
#     df.set_state(States.A)
#     df.set_speaker(Speaker.USER)
#     df.user_turn("hello there",)
#     assert df.state() == States.E
#



################################### INTEGRATION TESTS ####################################

# def test_integration_opening_component():
#
#     kb = KnowledgeBase()
#     kb.load_json_file("opening_database.json")
#
#     receive_how_are_you = "{" \
#                             "[how are you]," \
#                             "[how you doing]," \
#                             "[what about you]," \
#                             "[whats up with you]," \
#                             "[how you are]," \
#                             "[how about you]" \
#                         "}"
#     # feelings_pos_and_not_received_how_are_you = "{" \
#     #                                             "[!#ONT_NEG(ont_negation), -%s, [#ONT(ont_feelings_positive)]]," \
#     #                                             "[! -%s, [#ONT(ont_negation)], [#ONT(ont_feelings_negative)]]," \
#     #                                             "#IsPositiveSentiment" \
#     #                                             "}" % (receive_how_are_you, receive_how_are_you)
#     feelings_pos_and_not_received_how_are_you = "{" \
#                                                 "#ONT_NEG(ont_negation), -%s, [#ONT(ont_feelings_positive)]," \
#                                                 " -%s, [#ONT(ont_negation)], [#ONT(ont_feelings_negative)]," \
#                                                 "#IsPositiveSentiment" \
#                                                 "}" % (receive_how_are_you, receive_how_are_you)
#     print(feelings_pos_and_not_received_how_are_you)
#
#     nlu = Natex(feelings_pos_and_not_received_how_are_you, macros={"ONT": ONTE(kb), "ONT_NEG": ONT_NEG(kb)})
#
#     m = nlu.match("im not too bad",)
#     assert m
#     m = nlu.match("great i guess",)
#     assert m
#     m = nlu.match("great",)
#     assert m
#     m = nlu.match("i seem to be pretty great thanks",)
#     assert m
#     m = nlu.match("not bad",)
#     assert m
#     m = nlu.match("thanks im not bad dude",)
#     assert m
#     m = nlu.match("well how are you")
#     assert not m
#     m = nlu.match("pretty well how are you",)
#     assert not m
#     m = nlu.match("not well how are you",)
#     assert not m
#     m = nlu.match("how are you im not well",)
#     assert not m
#     m = nlu.match("im bad",)
#     assert not m
#     m = nlu.match("bad",)
#     assert not m
#     m = nlu.match("im doing ok",)
#     assert not m
#     feelings_neg_and_not_received_how_are_you = "{" \
#                                                 "#ONT_NEG(ont_negation), -%s, [#ONT(ont_feelings_negative)]," \
#                                                 "-%s, [#ONT(ont_negation)], [{#ONT(ont_feelings_positive),#ONT(ont_feelings_neutral)}]," \
#                                                 "#IsNegativeSentiment" \
#                                                 "}" % (receive_how_are_you, receive_how_are_you)
#     nlu = Natex(feelings_neg_and_not_received_how_are_you, macros={"ONT": ONTE(kb), "ONT_NEG": ONT_NEG(kb)})
#     m = nlu.match("bad i guess",)
#     assert m
#     m = nlu.match("bad",)
#     assert m
#     m = nlu.match("i seem to be pretty bad thanks",)
#     assert m
#     m = nlu.match("not good",)
#     assert m
#     m = nlu.match("thanks im not ok dude",)
#     assert m
#     m = nlu.match("great i guess",)
#     assert not m
#     m = nlu.match("great",)
#     assert not m
#     m = nlu.match("i seem to be pretty great thanks",)
#     assert not m
#     m = nlu.match("not bad",)
#     assert not m
#     m = nlu.match("thanks im not bad dude",)
#     assert not m
#     m = nlu.match("ok how are you",)
#     assert not m
#     m = nlu.match("pretty well how are you",)
#     assert not m
#     m = nlu.match("not well how are you",)
#     assert not m
#     m = nlu.match("how are you im not well",)
#     assert not m
#     feelings_neutral_and_not_received_how_are_you = "#ONT_NEG(ont_negation), -%s, [#ONT(ont_feelings_neutral)]" % (
#         receive_how_are_you)
#     nlu = Natex(feelings_neutral_and_not_received_how_are_you, macros={"ONT": ONTE(kb), "ONT_NEG": ONT_NEG(kb)})
#     m = nlu.match("ok i guess",)
#     assert m
#     m = nlu.match("ok",)
#     assert m
#     m = nlu.match("i seem to be ok thanks",)
#     assert m
#     m = nlu.match("great i guess",)
#     assert not m
#     m = nlu.match("great",)
#     assert not m
#     m = nlu.match("i seem to be pretty great thanks",)
#     assert not m
#     m = nlu.match("not bad",)
#     assert not m
#     m = nlu.match("thanks im not bad dude",)
#     assert not m
#     m = nlu.match("ok how are you",)
#     assert not m
#     m = nlu.match("pretty well how are you",)
#     assert not m
#     m = nlu.match("not well how are you",)
#     assert not m
#     m = nlu.match("how are you im not well",)
#     assert not m
#     m = nlu.match("bad i guess",)
#     assert not m
#     m = nlu.match("bad",)
#     assert not m
#     m = nlu.match("i seem to be pretty bad thanks",)
#     assert not m
#     m = nlu.match("not good",)
#     assert not m
#     m = nlu.match("thanks im not ok dude",)
#     assert not m
#     feelings_pos_and_received_how_are_you = "{" \
#                                             "#ONT_NEG(ont_negation), [#ONT(ont_feelings_positive)], [%s]," \
#                                             "[#ONT(ont_negation), #ONT(ont_feelings_negative), %s]," \
#                                             "<#IsPositiveSentiment, %s>" \
#                                             "}" % (receive_how_are_you, receive_how_are_you, receive_how_are_you)
#     nlu = Natex(feelings_pos_and_received_how_are_you, macros={"ONT": ONTE(kb), "ONT_NEG": ONT_NEG(kb)})
#     m = nlu.match("pretty well how are you",)
#     assert m
#     m = nlu.match("great how are you",)
#     assert m
#     m = nlu.match("not too bad how are you",)
#     assert m
#     m = nlu.match("not bad how are you",)
#     assert m
#     m = nlu.match("ok i guess",)
#     assert not m
#     m = nlu.match("ok",)
#     assert not m
#     m = nlu.match("i seem to be ok thanks",)
#     assert not m
#     m = nlu.match("great i guess",)
#     assert not m
#     m = nlu.match("great",)
#     assert not m
#     m = nlu.match("i seem to be pretty great thanks",)
#     assert not m
#     m = nlu.match("not bad",)
#     assert not m
#     m = nlu.match("thanks im not bad dude",)
#     assert not m
#     m = nlu.match("ok how are you",)
#     assert not m
#     m = nlu.match("not well how are you",)
#     assert not m
#     m = nlu.match("how are you im not well",)
#     assert not m
#     m = nlu.match("bad i guess",)
#     assert not m
#     m = nlu.match("bad",)
#     assert not m
#     m = nlu.match("i seem to be pretty bad thanks",)
#     assert not m
#     m = nlu.match("not good",)
#     assert not m
#     m = nlu.match("thanks im not ok dude",)
#     assert not m
#     feelings_neg_and_received_how_are_you = "{" \
#                                             "[!#ONT_NEG(ont_negation), [#ONT(ont_feelings_negative)], [%s]]," \
#                                             "[#ONT(ont_negation), {#ONT(ont_feelings_positive),#ONT(ont_feelings_neutral)}, %s]," \
#                                             "<#IsNegativeSentiment, %s>" \
#                                             "}" % (receive_how_are_you, receive_how_are_you, receive_how_are_you)
#     nlu = Natex(feelings_neg_and_received_how_are_you, macros={"ONT": ONTE(kb), "ONT_NEG": ONT_NEG(kb)})
#     m = nlu.match("not well how are you",)
#     assert m
#     m = nlu.match("bad how are you",)
#     assert m
#     m = nlu.match("im bad how are you",)
#     assert m
#     m = nlu.match("ok i guess",)
#     assert not m
#     m = nlu.match("ok",)
#     assert not m
#     m = nlu.match("i seem to be ok thanks",)
#     assert not m
#     m = nlu.match("great i guess",)
#     assert not m
#     m = nlu.match("great",)
#     assert not m
#     m = nlu.match("i seem to be pretty great thanks",)
#     assert not m
#     m = nlu.match("not bad",)
#     assert not m
#     m = nlu.match("thanks im not bad dude",)
#     assert not m
#     m = nlu.match("ok how are you",)
#     assert not m
#     m = nlu.match("bad i guess",)
#     assert not m
#     m = nlu.match("bad",)
#     assert not m
#     m = nlu.match("i seem to be pretty bad thanks",)
#     assert not m
#     m = nlu.match("not good",)
#     assert not m
#     m = nlu.match("thanks im not ok dude",)
#     assert not m
#     m = nlu.match("pretty well how are you",)
#     assert not m
#     m = nlu.match("great how are you",)
#     assert not m
#     feelings_neutral_and_received_how_are_you = "[!#ONT_NEG(ont_negation), [#ONT(ont_feelings_neutral)], [%s]]" % (
#         receive_how_are_you)
#     nlu = Natex(feelings_neutral_and_received_how_are_you, macros={"ONT": ONTE(kb), "ONT_NEG": ONT_NEG(kb)})
#     m = nlu.match("ok but how are you",)
#     assert m
#     m = nlu.match("not ok how are you",)
#     assert not m
#     m = nlu.match("im not ok how are you",)
#     assert not m
#     m = nlu.match("not well how are you",)
#     assert not m
#     m = nlu.match("bad how are you",)
#     assert not m
#     m = nlu.match("im bad how are you",)
#     assert not m
#     m = nlu.match("ok i guess",)
#     assert not m
#     m = nlu.match("ok",)
#     assert not m
#     m = nlu.match("i seem to be ok thanks",)
#     assert not m
#     m = nlu.match("great i guess",)
#     assert not m
#     m = nlu.match("great",)
#     assert not m
#     m = nlu.match("i seem to be pretty great thanks",)
#     assert not m
#     m = nlu.match("not bad",)
#     assert not m
#     m = nlu.match("thanks im not bad dude",)
#     assert not m
#     m = nlu.match("bad i guess",)
#     assert not m
#     m = nlu.match("bad",)
#     assert not m
#     m = nlu.match("i seem to be pretty bad thanks",)
#     assert not m
#     m = nlu.match("not good",)
#     assert not m
#     m = nlu.match("thanks im not ok dude",)
#     assert not m
#     m = nlu.match("pretty well how are you",)
#     assert not m
#     m = nlu.match("great how are you",)
#     assert not m
#     decline_share = "{" \
#                     "[#ONT(ont_negation), {talk, talking, discuss, discussing, share, sharing, tell, telling, say, saying}]," \
#                     "[#ONT(ont_fillers), #ONT(ont_negative)]," \
#                     "[#ONT(ont_negative)]" \
#                     "<{dont,do not}, know>," \
#                     "<not, sure>" \
#                     "}"
#     nlu = Natex(decline_share, macros={"ONT": ONTE(kb), "ONT_NEG": ONT_NEG(kb)})
#     m = nlu.match("i dont know",)
#     assert m
#     m = nlu.match("im not sure",)
#     assert m
#     m = nlu.match("i dont want to tell you",)
#     assert m
#     m = nlu.match("no",)
#     assert m
#     m = nlu.match("i dont want to talk about it",)
#     assert m
#     m = nlu.match("ok but how are you",)
#     assert not m
#     m = nlu.match("not ok how are you",)
#     assert not m
#     m = nlu.match("im not ok how are you",)
#     assert not m
#     m = nlu.match("not well how are you",)
#     assert not m
#     m = nlu.match("bad how are you",)
#     assert not m
#     m = nlu.match("im bad how are you",)
#     assert not m
#     m = nlu.match("ok i guess",)
#     assert not m
#     m = nlu.match("ok",)
#     assert not m
#     m = nlu.match("i seem to be ok thanks",)
#     assert not m
#     m = nlu.match("great i guess",)
#     assert not m
#     m = nlu.match("great",)
#     assert not m
#     m = nlu.match("i seem to be pretty great thanks",)
#     assert not m
#     m = nlu.match("not bad",)
#     assert not m
#     m = nlu.match("thanks im not bad dude",)
#     assert not m
#     m = nlu.match("bad i guess",)
#     assert not m
#     m = nlu.match("bad",)
#     assert not m
#     m = nlu.match("i seem to be pretty bad thanks",)
#     assert not m
#     m = nlu.match("not good",)
#     assert not m
#     m = nlu.match("thanks im not ok dude",)
#     assert not m
#     m = nlu.match("pretty well how are you",)
#     assert not m
#     m = nlu.match("great how are you",)
#     assert not m




