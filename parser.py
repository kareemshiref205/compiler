from scanner import codeToBeScanned, scanner

t, _ = scanner(codeToBeScanned)
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

def parse_program():
    funcs = []
    while peek()[0] != "EOF":
        funcs.append(parse_function())
    return ("program", funcs)

def parse_function():
    typ = expect("Keyword")[1]
    name = expect("Identifier")[1]
    expect("Special Character", "(")
    expect("Special Character", ")")
    body = parse_block()
    return ("function", typ, name, body)

def parse_block():
    expect("Special Character", "{")
    stmts = []
    while not (peek()[0] == "Special Character" and peek()[1] == "}"):
        stmts.append(parse_statement())
    expect("Special Character", "}")
    return ("block", stmts)

def parse_statement():
    if match("Keyword", "if"):
        expect("Special Character", "(")
        cond = parse_expression()
        expect("Special Character", ")")
        then = parse_statement()
        els = None
        if match("Keyword", "else"):
            els = parse_statement()
        return ("if", cond, then, els)
    if match("Keyword", "return"):
        expr = parse_expression()
        expect("Special Character", ";")
        return ("return", expr)
    if peek()[0] == "Special Character" and peek()[1] == "{":
        return parse_block()
    if peek()[0] == "Keyword":
        return parse_declaration()
    expr = parse_expression()
    expect("Special Character", ";")
    return ("expr", expr)

def parse_declaration():
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
    return parse_assignment()

def parse_assignment():
    left = parse_equality()
    if match("Operator", "="):
        right = parse_assignment()
        return ("assign", left, right)
    return left

def parse_equality():
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
    if match("Special Character", "("):
        node = parse_expression()
        expect("Special Character", ")")
        return node
    if peek()[0] == "Identifier":
        return ("id", consume()[1])
    if peek()[0] == "Constant":
        return ("num", consume()[1])
    raise SyntaxError("bad expr " + str(peek()))

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


def main():
    try:
        ast = parse_program()
    except SyntaxError as exc:
        tok = peek()
        print("Syntax error near", tok, "-", exc)
        return
    print_tree(ast)

if __name__ == "__main__":
    main()
