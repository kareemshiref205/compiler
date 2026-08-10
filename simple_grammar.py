# =============================================================================
# SIMPLE GRAMMAR - Practical Implementation
# Compiler Design Course
# =============================================================================
# A Simple Grammar is a context-free grammar where every production rule
# starts with a UNIQUE terminal symbol. This means that by just looking at
# the next input character, we can immediately know which rule to apply.
# No lookahead or backtracking is needed.
#
# GRAMMAR USED IN THIS FILE:
#
#   S -> a A
#   S -> b B
#   A -> c
#   A -> d
#   B -> e
#
# This is Simple because:
#   - S -> a A  starts with terminal 'a'  (unique)
#   - S -> b B  starts with terminal 'b'  (unique)
#   - A -> c    starts with terminal 'c'  (unique)
#   - A -> d    starts with terminal 'd'  (unique)
#   - B -> e    starts with terminal 'e'  (unique)
#
# No two rules for the same non-terminal start with the same terminal.
# =============================================================================


# --- The Grammar Definition ---

def get_grammar():
    """
    Returns the grammar as a dictionary.
    Key   = non-terminal symbol
    Value = list of production rules (each rule is a list of symbols)
    """
    grammar = {
        "S": [["a", "A"], ["b", "B"]],
        "A": [["c"],      ["d"]],
        "B": [["e"]],
    }
    return grammar


# --- Build the Predict Table ---

def build_predict_table(grammar):
    """
    For a Simple Grammar, the predict set of each rule is just its
    first terminal symbol. We build a table:
        predict_table[non_terminal][terminal] = rule to apply
    """
    predict_table = {}

    for non_terminal, rules in grammar.items():
        predict_table[non_terminal] = {}
        for rule in rules:
            first_symbol = rule[0]  # In a Simple Grammar, this is always a terminal
            predict_table[non_terminal][first_symbol] = rule

    return predict_table


# --- Check if Grammar is Simple ---

def check_is_simple(grammar):
    """
    A grammar is Simple if, for every non-terminal, no two rules
    start with the same terminal symbol.
    Returns True if Simple, False otherwise.
    """
    for non_terminal, rules in grammar.items():
        seen_terminals = []
        for rule in rules:
            first_symbol = rule[0]
            if first_symbol in seen_terminals:
                print(f"  CONFLICT: Non-terminal '{non_terminal}' has two rules starting with '{first_symbol}'")
                return False
            seen_terminals.append(first_symbol)
    return True


# --- Parse an Input String ---

def parse(input_string, predict_table, start_symbol):
    """
    Tries to parse the input string using the Simple Grammar.
    Uses a stack-based top-down parsing approach.

    Stack starts with the start symbol.
    At each step:
      - If top of stack is a terminal -> match it with current input character
      - If top of stack is a non-terminal -> look up which rule to apply
    """
    stack = [start_symbol]  # Start with the start symbol on the stack
    index = 0               # Current position in the input string
    tokens = list(input_string)

    print(f"\n  Parsing: '{input_string}'")
    print(f"  {'Stack':<25} {'Remaining Input':<20} {'Action'}")
    print(f"  {'-'*65}")

    while stack:
        top = stack[-1]
        current = tokens[index] if index < len(tokens) else "$"  # $ = end of input

        stack_display = " ".join(stack)
        remaining = "".join(tokens[index:]) if index < len(tokens) else "$"

        if top == current:
            # Terminal matched — consume it
            action = f"Match '{current}'"
            print(f"  {stack_display:<25} {remaining:<20} {action}")
            stack.pop()
            index += 1

        elif top in predict_table:
            # Non-terminal — look up the rule
            if current in predict_table[top]:
                rule = predict_table[top][current]
                action = f"Apply {top} -> {' '.join(rule)}"
                print(f"  {stack_display:<25} {remaining:<20} {action}")
                stack.pop()
                # Push rule symbols in reverse so leftmost is on top
                for symbol in reversed(rule):
                    stack.append(symbol)
            else:
                print(f"  {stack_display:<25} {remaining:<20} ERROR: No rule for '{top}' on input '{current}'")
                return False
        else:
            # Terminal on stack but doesn't match input
            print(f"  {stack_display:<25} {remaining:<20} ERROR: Expected '{top}' but got '{current}'")
            return False

    # After stack is empty, input must also be fully consumed
    if index == len(tokens):
        return True
    else:
        print(f"  Input not fully consumed. Remaining: {''.join(tokens[index:])}")
        return False


# --- Display the Predict Table ---

def display_predict_table(predict_table):
    """Prints the predict table in a readable format."""
    print("\n  Predict Table:")
    print(f"  {'Non-Terminal':<15} {'Terminal':<12} {'Rule'}")
    print(f"  {'-'*40}")
    for non_terminal, entries in predict_table.items():
        for terminal, rule in entries.items():
            rule_str = f"{non_terminal} -> {' '.join(rule)}"
            print(f"  {non_terminal:<15} {terminal:<12} {rule_str}")


# --- Main ---

def main():
    print("=" * 65)
    print("  SIMPLE GRAMMAR - Demonstration")
    print("=" * 65)

    grammar = get_grammar()

    # Print the grammar
    print("\n  Grammar Rules:")
    for non_terminal, rules in grammar.items():
        for rule in rules:
            print(f"    {non_terminal} -> {' '.join(rule)}")

    # Check if it qualifies as Simple Grammar
    print("\n  Checking if grammar is Simple...")
    is_simple = check_is_simple(grammar)
    if is_simple:
        print("  Result: YES — This is a Simple Grammar.")
    else:
        print("  Result: NO — This is NOT a Simple Grammar.")
        return

    # Build and display the predict table
    predict_table = build_predict_table(grammar)
    display_predict_table(predict_table)

    # Test inputs
    test_inputs = ["ac", "ad", "be", "ae", "bc", "a"]

    print("\n" + "=" * 65)
    print("  PARSING TEST CASES")
    print("=" * 65)

    for inp in test_inputs:
        result = parse(inp, predict_table, start_symbol="S")
        verdict = "ACCEPTED" if result else "REJECTED"
        print(f"  --> '{inp}' : {verdict}")
        print()


if __name__ == "__main__":
    main()
