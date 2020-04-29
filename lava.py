#
# Lava - A production grammar system.
#
# Given a grammar, generate random potential inputs that satisfy
# that grammar. This is useful for test generation.
#
# (C) 2020, Emin Gun Sirer.
# See the file LICENSE for licensing details.
#
import sys
import ply.lex as lex
import ply.yacc as yacc
import parser as pythonparser
import collections
import random

tokens = (
    'LABEL', 'DEFN', 'OR', 'STRING', 'NEWLINE', 'LPAREN', 'RPAREN', 'NUMBER',
    )

(TSTRING, TCONCAT, TLABEL, TCHOICES) = range(4)
ntypes=["STRING", "CONCAT", "LABEL", "CHOICE"]

class Node:
    def __init__(self, op, val, weights=None, code=None):
        self.op = op
        self.val = val
        self.weight = weights if weights is not None else [1]*len(val) if op==TCHOICES else [1]
        self.code = code
        
    def __str__(self):
        s = "Node(type=%s,weight=%s,code=%s," % (ntypes[self.op], self.weight, "none" if self.code is None else "exists")
        if self.op == TSTRING or self.op == TLABEL:
            s += ("val=%s)" % self.val)
        elif self.op == TCONCAT or self.op == TCHOICES:
            s += "".join([str(n) for n in self.val]) + ")"
        else:
            return "should not happen"
        return s
    
    def execute(self):
        if self.code is not None:
            if not eval(self.code):
                return
        if self.op == TSTRING:
            print(self.val, end='')
        elif self.op == TCONCAT:
            for n in self.val:
                n.execute()
        elif self.op == TCHOICES:
            x = random.choices(self.val, self.weight)[0]
            x.execute()
        elif self.op == TLABEL:
            if self.val not in names:
                print ("Error: label %s not defined" % self.val)
            names[self.val].execute()

# Tokens
t_OR       = r'\|'
t_DEFN     = r':'
t_LPAREN   = r'{'
t_RPAREN   = r'}'
t_STRING   = r'\"[^"]*\"'
t_LABEL    = r'[a-zA-Z_][a-zA-Z0-9_-]*'

def t_NUMBER(t):
    r'\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        print("Integer value too large %d", t.value)
        t.value = 0
    return t

# Ignored characters
t_ignore = " \t"

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    return t

def t_error(t):
    print("Illegal character '%s' on line %d" % (t.value[0], t.lexer.lineno))
    t.lexer.skip(1)
    
# Parsing rules

# dictionary of names
last = None
names = { }
nrules = collections.defaultdict(int)

def p_statements(t):
    '''stmtlist : 
                | stmtlist statement NEWLINE'''
    global last
    if len(t) >= 2 and t[2] is not None:
        last = t[2]
            
def p_statement_action(t):
    'statement : LABEL LABEL LPAREN STRING RPAREN'
    if t[1] != "action":
        print ("Expected keyword action")
        return
    source_string = t[4].strip('"')
    try:
        st = pythonparser.suite(source_string)
        code = st.compile()
        label = t[2]
        if label in names:
            node = names[label]
        else:
            node = Node(TSTRING, "")
            names[label] = node
        node.code = code
    except:
        print("error in code fragment for %s" % t[2])

def p_statement_rule(t):
    '''statement : LABEL DEFN rhs'''
    # check to see if a weight is specified
    if len(t) > 4:
        weight = t[4]
        rhs = t[6]
    else:
        weight = 1
        rhs = t[3]
    label = t[1]
    if label in names:
        existing = names[label]
        if existing.op == TCHOICES:
            existing.val.append(rhs)
            existing.weight.append(weight)
        else:
            new = Node(TCHOICES, [rhs, existing], [weight] + existing.weight)
            names[label] = new
    else:
        names[label] = rhs
        t[0] = label

def p_rhs(t):
    '''rhs : expressions
           | LPAREN NUMBER RPAREN expressions
           | rhs OR expressions
           | rhs OR LPAREN NUMBER RPAREN expressions'''
    if len(t) == 2:
        t[0] = t[1]
    elif len(t) == 5:
        t[4].weight = t[2]
        t[0] = t[4]
    else: # we have an OR expression
        if len(t) == 4:
            weight = 1
            existing = t[1]
            rhs = t[3]
        else:
            existing = t[1]
            rhs = t[6]
            weight = t[4]
        if existing.op == TCHOICES:
            existing.val.append(rhs)
            existing.weight.append(weight)
            t[0] = existing
        else:
            new = Node(TCHOICES, [rhs, existing], [weight] + existing.weight)
            t[0] = new

def p_expressions(t):
    '''expressions : 
                   | expressions expression'''
    if len(t) == 1:
        t[0] = None
    else:
        if t[1] == None:
            t[0] = t[2]
        elif t[1].op == TSTRING and t[2].op == TSTRING:
            t[1].val += t[2].val
            t[0] = t[1]
        else:
            t[0] = Node(TCONCAT, [t[1], t[2]])

def p_expression_singleton(t):
    '''expression : STRING
                  | LABEL'''
    if t[1] == '"\\n"':
        t[0] = Node(TSTRING, '\n')
    elif t[1][0] == '"':
        t[0] = Node(TSTRING, t[1].strip('"'))
    else:
        t[0] = Node(TLABEL, t[1])

def p_error(t):
    print("Syntax error at '%s'" % t.value)

# Build the lexer
debug=False
lexer = lex.lex(debug=0)
parser = yacc.yacc()

with open(sys.argv[1], "r") as f:
    grammar = f.read()
    p = parser.parse(grammar, debug=debug)

    # dump all the rules
#    for p in names:
#        print ("rule for %s" % p)
#        print (names[p])
#    print ("last production rule is %s" % last)
    
    if last is not None:
#        print (names[last])

        names[last].execute()
        
