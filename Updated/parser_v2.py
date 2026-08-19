import ast
import sys

TOKENS_FILE = "tokens.txt"

# =============================================================================
# GRAMMAR — Context-Free Grammar (CFG) production rules
#
# The parser below implements exactly this grammar:
#
#   program      → function*
#
#   function     → Keyword Identifier "(" ")" block
#
#   block        → "{" statement* "}"
#
#   statement    → "if" "(" expression ")" statement ( "else" statement )?
#               |  "return" expression ";"
#               |  block
#               |  declaration
#               |  expression ";"
#
#   declaration  → Keyword ( Identifier ( "=" expression )? ),+ ";"
#
#   expression   → assignment
#
#   assignment   → equality ( "=" assignment )?
#
#   equality     → add ( ("==" | "!=") add )*
#
#   add          → mul ( ("+" | "-") mul )*
#
#   mul          → primary ( ("*" | "/") primary )*
#
#   primary      → "(" expression ")"
#               |  Identifier
#               |  Constant
#
# The dictionary below maps each non-terminal name to its rule string(s)
# for reference and documentation purposes.
# =============================================================================

GRAMMAR = {
    "program":     ["function*"],
    "function":    ["Keyword Identifier '(' ')' block"],
    "block":       ["'{' statement* '}'"],
    "statement":   [
                    "'if' '(' expression ')' statement ( 'else' statement )?",
                    "'return' expression ';'",
                    "block",
                    "declaration",
                    "expression ';'",
                   ],
    "declaration": ["Keyword ( Identifier ( '=' expression )? ),+ ';'"],
    "expression":  ["assignment"],
    "assignment":  ["equality ( '=' assignment )?"],
    "equality":    ["add ( ('==' | '!=') add )*"],
    "add":         ["mul ( ('+' | '-') mul )*"],
    "mul":         ["primary ( ('*' | '/') primary )*"],
    "primary":     [
                    "'(' expression ')'",
                    "Identifier",
                    "Constant",
                   ],
}


def print_grammar():
    print("=" * 60)
    print("GRAMMAR — Production Rules")
    print("=" * 60)
    for lhs, rules in GRAMMAR.items():
        if len(rules) == 1:
            print(f"  {lhs:<14} →  {rules[0]}")
        else:
            print(f"  {lhs:<14} →  {rules[0]}")
            for rule in rules[1:]:
                print(f"  {'':14}  |  {rule}")
    print("=" * 60)
    print()


# =============================================================================
# TOKEN STREAM
# =============================================================================

t = []
pos = 0


def peek():
    if pos < len(t):
        return t[pos]
    return ("EOF", "")


def consume():
    global pos
    tok = peek()
    pos += 1
    return tok


def match(ttype, value=None):
    tok = peek()
    if tok[0] != ttype:
        return False
    if value is not None and tok[1] != value:
        return False
    consume()
    return True


def expect(ttype, value=None):
    tok = peek()
    if tok[0] != ttype or (value is not None and tok[1] != value):
        raise SyntaxError("bad token " + str(tok))
    return consume()


# =============================================================================
# PARSER — implements the grammar rules above
# Each function corresponds directly to one non-terminal in the grammar.
# =============================================================================

def parse_program():
    # program → function*
    funcs = []
    while peek()[0] != "EOF":
        funcs.append(parse_function())
    return ("program", funcs)


def parse_function():
    # function → Keyword Identifier "(" ")" block
    typ = expect("Keyword")[1]
    name = expect("Identifier")[1]
    expect("Special Character", "(")
    expect("Special Character", ")")
    body = parse_block()
    return ("function", typ, name, body)


def parse_block():
    # block → "{" statement* "}"
    expect("Special Character", "{")
    stmts = []
    while not (peek()[0] == "Special Character" and peek()[1] == "}"):
        stmts.append(parse_statement())
    expect("Special Character", "}")
    return ("block", stmts)


def parse_statement():
    # statement → "if" "(" expression ")" statement ( "else" statement )?
    if match("Keyword", "if"):
        expect("Special Character", "(")
        cond = parse_expression()
        expect("Special Character", ")")
        then = parse_statement()
        els = None
        if match("Keyword", "else"):
            els = parse_statement()
        return ("if", cond, then, els)

    # statement → "return" expression ";"
    if match("Keyword", "return"):
        expr = parse_expression()
        expect("Special Character", ";")
        return ("return", expr)

    # statement → block
    if peek()[0] == "Special Character" and peek()[1] == "{":
        return parse_block()

    # statement → declaration
    if peek()[0] == "Keyword":
        return parse_declaration()

    # statement → expression ";"
    expr = parse_expression()
    expect("Special Character", ";")
    return ("expr", expr)


def parse_declaration():
    # declaration → Keyword ( Identifier ( "=" expression )? ),+ ";"
    typ = consume()[1]
    vars = []
    while True:
        name = expect("Identifier")[1]
        init = None
        if match("Operator", "="):
            init = parse_expression()
        vars.append((name, init))
        if not match("Special Character", ","):
            break
    expect("Special Character", ";")
    return ("decl", typ, vars)


def parse_expression():
    # expression → assignment
    return parse_assignment()


def parse_assignment():
    # assignment → equality ( "=" assignment )?
    left = parse_equality()
    if match("Operator", "="):
        right = parse_assignment()
        return ("assign", left, right)
    return left


def parse_equality():
    # equality → add ( ("==" | "!=") add )*
    node = parse_add()
    while True:
        if match("Operator", "=="):
            node = ("binop", "==", node, parse_add())
            continue
        if match("Operator", "!="):
            node = ("binop", "!=", node, parse_add())
            continue
        break
    return node


def parse_add():
    # add → mul ( ("+" | "-") mul )*
    node = parse_mul()
    while True:
        if match("Operator", "+"):
            node = ("binop", "+", node, parse_mul())
            continue
        if match("Operator", "-"):
            node = ("binop", "-", node, parse_mul())
            continue
        break
    return node


def parse_mul():
    # mul → primary ( ("*" | "/") primary )*
    node = parse_primary()
    while True:
        if match("Operator", "*"):
            node = ("binop", "*", node, parse_primary())
            continue
        if match("Operator", "/"):
            node = ("binop", "/", node, parse_primary())
            continue
        break
    return node


def parse_primary():
    # primary → "(" expression ")"  |  Identifier  |  Constant
    if match("Special Character", "("):
        node = parse_expression()
        expect("Special Character", ")")
        return node
    if peek()[0] == "Identifier":
        return ("id", consume()[1])
    if peek()[0] == "Constant":
        return ("num", consume()[1])
    raise SyntaxError("bad expr " + str(peek()))


# =============================================================================
# PARSE TREE PRINTER
# =============================================================================

def print_tree(node, prefix="", is_last=True, is_root=True):
    connector = "" if is_root else ("└─ " if is_last else "├─ ")
    if isinstance(node, tuple):
        print(f"{prefix}{connector}{node[0]}")
        child_prefix = prefix + ("   " if is_last else "│  ")
        children = list(node[1:])
        for idx, child in enumerate(children):
            last_child = idx == len(children) - 1
            print_tree(child, child_prefix, last_child, False)
    elif isinstance(node, list):
        for idx, child in enumerate(node):
            last_child = idx == len(node) - 1
            print_tree(child, prefix, last_child, False)
    else:
        print(f"{prefix}{connector}{node}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    global t, pos

    # Print grammar rules
    print_grammar()

    # Step 1: Read tokens from tokens file
    try:
        with open(TOKENS_FILE, "r") as f:
            raw = f.read().strip()
        t = ast.literal_eval(raw)
    except FileNotFoundError:
        print(f"Error: tokens file '{TOKENS_FILE}' not found. Run scanner_v2.py first.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading tokens file: {e}")
        sys.exit(1)

    pos = 0

    # Step 2: Parse and print the tree
    try:
        ast_tree = parse_program()
    except SyntaxError as exc:
        tok = peek()
        print("Syntax error near", tok, "-", exc)
        print("\nRejected")
        return

    print_tree(ast_tree)
    print("\nAccepted")


if __name__ == "__main__":
    main()
