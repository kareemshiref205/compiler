# =============================================================================
# QUASI-SIMPLE GRAMMAR - Practical Implementation
# Compiler Design Course
# =============================================================================
# A Quasi-Simple Grammar relaxes one rule from Simple Grammar:
# production rules are ALLOWED to start with a non-terminal,
# BUT only if that non-terminal itself starts with a unique terminal.
#
# In other words, we compute the FIRST SET of each rule (the set of
# terminals that can appear as the first character derived from that rule),
# and no two rules for the same non-terminal may share a terminal in their
# FIRST sets.
#
# A Simple Grammar is a special case of Quasi-Simple Grammar where every
# rule starts directly with a terminal (so FIRST sets are trivially single
# terminals). Quasi-Simple Grammar allows rules to start with a non-terminal,
# as long as the FIRST sets remain disjoint.
#
# GRAMMAR USED IN THIS FILE:
#
#   S -> A x
#   S -> B y
#   A -> a
#   A -> b
#   B -> c
#
# FIRST sets:
#   FIRST(A x) = FIRST(A) = {a, b}
#   FIRST(B y) = FIRST(B) = {c}
#   FIRST(a)   = {a}
#   FIRST(b)   = {b}
#   FIRST(c)   = {c}
#
# For non-terminal S:
#   Rule "A x" has FIRST = {a, b}
#   Rule "B y" has FIRST = {c}
#   These sets are DISJOINT -> Quasi-Simple (and in fact Simple at this level).
#
# This grammar is NOT Simple at the top level (S's rules start with
# non-terminals A and B), but it IS Quasi-Simple because the FIRST sets
# are disjoint.
# =============================================================================


# --- The Grammar Definition ---

def get_grammar():
    """
    Returns the grammar as a dictionary.
    Key   = non-terminal
    Value = list of production rules (each rule is a list of symbols)
    """
    grammar = {
        "S": [["A", "x"], ["B", "y"]],
        "A": [["a"],       ["b"]],
        "B": [["c"]],
    }
    return grammar


def get_terminals(grammar):
    """Returns the set of all terminal symbols in the grammar."""
    non_terminals = set(grammar.keys())
    terminals = set()
    for rules in grammar.values():
        for rule in rules:
            for symbol in rule:
                if symbol not in non_terminals:
                    terminals.add(symbol)
    return terminals


# --- Compute FIRST Sets ---

def compute_first_sets(grammar):
    """
    Computes the FIRST set for every non-terminal.
    FIRST(X) = set of terminals that can start a string derived from X.

    Algorithm:
      - If X is a terminal, FIRST(X) = {X}
      - If X -> a ..., add 'a' to FIRST(X)
      - If X -> Y ..., add FIRST(Y) to FIRST(X)
      Repeat until no changes occur (fixed-point iteration).
    """
    non_terminals = set(grammar.keys())
    first = {nt: set() for nt in non_terminals}

    changed = True
    while changed:
        changed = False
        for non_terminal, rules in grammar.items():
            for rule in rules:
                first_symbol = rule[0]
                if first_symbol not in non_terminals:
                    # It's a terminal — add it directly
                    if first_symbol not in first[non_terminal]:
                        first[non_terminal].add(first_symbol)
                        changed = True
                else:
                    # It's a non-terminal — add its FIRST set
                    for terminal in first[first_symbol]:
                        if terminal not in first[non_terminal]:
                            first[non_terminal].add(terminal)
                            changed = True

    return first


def compute_first_of_rule(rule, first_sets, non_terminals):
    """
    Computes the FIRST set of a specific rule (sequence of symbols).
    For a simple rule like [A, x], FIRST = FIRST(A) if A is a non-terminal,
    or {A} if A is a terminal.
    (We ignore epsilon/nullable symbols for simplicity here.)
    """
    first_symbol = rule[0]
    if first_symbol in non_terminals:
        return set(first_sets[first_symbol])
    else:
        return {first_symbol}


# --- Check if Grammar is Quasi-Simple ---

def check_is_quasi_simple(grammar, first_sets):
    """
    A grammar is Quasi-Simple if, for every non-terminal, the FIRST sets
    of all its production rules are pairwise disjoint (no overlap).
    Returns True if Quasi-Simple, False otherwise.
    """
    non_terminals = set(grammar.keys())
    is_quasi_simple = True

    for non_terminal, rules in grammar.items():
        rule_first_sets = []
        for rule in rules:
            rule_first = compute_first_of_rule(rule, first_sets, non_terminals)
            rule_first_sets.append((rule, rule_first))

        # Check all pairs for overlap
        for i in range(len(rule_first_sets)):
            for j in range(i + 1, len(rule_first_sets)):
                rule_i, first_i = rule_first_sets[i]
                rule_j, first_j = rule_first_sets[j]
                overlap = first_i & first_j
                if overlap:
                    print(f"  CONFLICT in '{non_terminal}': "
                          f"rules '{' '.join(rule_i)}' and '{' '.join(rule_j)}' "
                          f"share FIRST terminal(s): {overlap}")
                    is_quasi_simple = False

    return is_quasi_simple


# --- Build the Predict Table ---

def build_predict_table(grammar, first_sets):
    """
    Builds a predict table using FIRST sets.
    predict_table[non_terminal][terminal] = rule to apply
    """
    non_terminals = set(grammar.keys())
    predict_table = {}

    for non_terminal, rules in grammar.items():
        predict_table[non_terminal] = {}
        for rule in rules:
            rule_first = compute_first_of_rule(rule, first_sets, non_terminals)
            for terminal in rule_first:
                predict_table[non_terminal][terminal] = rule

    return predict_table


# --- Parse an Input String ---

def parse(input_string, predict_table, start_symbol):
    """
    Top-down stack-based parser using the predict table built from FIRST sets.
    Same mechanism as Simple Grammar, but the predict table was built
    using computed FIRST sets rather than trivial first-symbol lookup.
    """
    stack = [start_symbol]
    index = 0
    tokens = list(input_string)
    non_terminals = set(predict_table.keys())

    print(f"\n  Parsing: '{input_string}'")
    print(f"  {'Stack':<25} {'Remaining Input':<20} {'Action'}")
    print(f"  {'-'*65}")

    while stack:
        top = stack[-1]
        current = tokens[index] if index < len(tokens) else "$"

        stack_display = " ".join(stack)
        remaining = "".join(tokens[index:]) if index < len(tokens) else "$"

        if top == current and top not in non_terminals:
            # Terminal match
            action = f"Match '{current}'"
            print(f"  {stack_display:<25} {remaining:<20} {action}")
            stack.pop()
            index += 1

        elif top in predict_table:
            # Non-terminal: look up rule via FIRST-based predict table
            if current in predict_table[top]:
                rule = predict_table[top][current]
                action = f"Apply {top} -> {' '.join(rule)}"
                print(f"  {stack_display:<25} {remaining:<20} {action}")
                stack.pop()
                for symbol in reversed(rule):
                    stack.append(symbol)
            else:
                print(f"  {stack_display:<25} {remaining:<20} ERROR: No rule for '{top}' on input '{current}'")
                return False
        else:
            print(f"  {stack_display:<25} {remaining:<20} ERROR: Expected '{top}' but got '{current}'")
            return False

    if index == len(tokens):
        return True
    else:
        print(f"  Input not fully consumed. Remaining: {''.join(tokens[index:])}")
        return False


# --- Display Functions ---

def display_first_sets(first_sets):
    print("\n  FIRST Sets (computed):")
    print(f"  {'Non-Terminal':<15} {'FIRST Set'}")
    print(f"  {'-'*35}")
    for nt, first in first_sets.items():
        print(f"  {nt:<15} {sorted(first)}")


def display_predict_table(predict_table):
    print("\n  Predict Table (built from FIRST sets):")
    print(f"  {'Non-Terminal':<15} {'Terminal':<12} {'Rule'}")
    print(f"  {'-'*45}")
    for non_terminal, entries in predict_table.items():
        for terminal, rule in entries.items():
            rule_str = f"{non_terminal} -> {' '.join(rule)}"
            print(f"  {non_terminal:<15} {terminal:<12} {rule_str}")


# --- Main ---

def main():
    print("=" * 65)
    print("  QUASI-SIMPLE GRAMMAR - Demonstration")
    print("=" * 65)

    grammar = get_grammar()

    # Print grammar
    print("\n  Grammar Rules:")
    for non_terminal, rules in grammar.items():
        for rule in rules:
            print(f"    {non_terminal} -> {' '.join(rule)}")

    # Compute FIRST sets
    first_sets = compute_first_sets(grammar)
    display_first_sets(first_sets)

    # Check Quasi-Simple
    print("\n  Checking if grammar is Quasi-Simple...")
    is_qs = check_is_quasi_simple(grammar, first_sets)
    if is_qs:
        print("  Result: YES — This is a Quasi-Simple Grammar.")
    else:
        print("  Result: NO — This is NOT a Quasi-Simple Grammar.")
        return

    # Build predict table from FIRST sets
    predict_table = build_predict_table(grammar, first_sets)
    display_predict_table(predict_table)

    # Test inputs
    # Valid: "ax" (S->Ax, A->a => "ax"), "bx" (S->Ax, A->b => "bx"), "cy" (S->By, B->c => "cy")
    # Invalid: "ay" (A can produce 'a' but S chose rule B->y which doesn't fit), "cx"
    test_inputs = ["ax", "bx", "cy", "ay", "cx", "x"]

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
