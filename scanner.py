codeToBeScanned = """
int main() {
    int x,y;
    // This is a single-line comment
    if (x == 42) {
        /* This is
           a block
           comment *///
        x = x-3;
    } else {
        y = 3.1; // Another comment
    }
    return 0;
}
"""


def _strip_comments(code):
    comments = []
    filtered_code = ""
    inside_block = False
    block_comment = ""

    for line in code.split("\n"):
        if inside_block:
            if "*/" in line:
                part_before_end, part_after_end = line.split("*/", 1)
                block_comment += part_before_end
                comments.append(block_comment.strip())
                block_comment = ""
                inside_block = False
                rest = part_after_end
                if "//" in rest:
                    code_part, comment_part = rest.split("//", 1)
                    filtered_code += code_part + "\n"
                    comments.append(comment_part.strip())
                else:
                    filtered_code += rest + "\n"
            else:
                block_comment += line + "\n"
            continue

        if "//" in line:
            code_part, comment_part = line.split("//", 1)
            filtered_code += code_part + "\n"
            comments.append(comment_part.strip())
        elif "/*" in line:
            part_before, part_after = line.split("/*", 1)
            filtered_code += part_before
            if "*/" in part_after:
                comment_part, rest = part_after.split("*/", 1)
                comments.append(comment_part.strip())
                if "//" in rest:
                    code_part, comment_part = rest.split("//", 1)
                    filtered_code += code_part + "\n"
                    comments.append(comment_part.strip())
                else:
                    filtered_code += rest + "\n"
            else:
                block_comment = part_after + "\n"
                inside_block = True
                filtered_code += "\n"
        else:
            filtered_code += line + "\n"

    return filtered_code, comments


KEYWORDS = {"int", "float", "double", "char", "if", "else", "for", "while", "return", "void"}
SPECIAL_CHARS = {"(", ")", "{", "}", "[", "]", ";", ",", ":"}
MULTI_CHAR_OPERATORS = {"==", "!=", "<=", ">=", "++", "--", "+=", "-=", "*=", "/=", "&&", "||"}
SINGLE_CHAR_OPERATORS = {"+", "-", "*", "/", "=", "<", ">", "!", "&", "|", "%", "^"}


def _is_numeric(token):
    if token.count(".") > 1:
        return False
    stripped = token.replace(".", "")
    return stripped.isdigit()


def _tokenize(filtered_code):
    tokens = []
    current_token = ""
    i = 0
    length = len(filtered_code)

    def flush():
        nonlocal current_token
        if not current_token:
            return
        if current_token in KEYWORDS:
            tokens.append(("Keyword", current_token))
        elif _is_numeric(current_token):
            tokens.append(("Constant", current_token))
        else:
            tokens.append(("Identifier", current_token))
        current_token = ""

    while i < length:
        char = filtered_code[i]
        two_char = filtered_code[i : i + 2]

        if char.isspace():
            flush()
            i += 1
            continue

        if two_char in MULTI_CHAR_OPERATORS:
            flush()
            tokens.append(("Operator", two_char))
            i += 2
            continue

        if char in SPECIAL_CHARS:
            flush()
            tokens.append(("Special Character", char))
            i += 1
            continue

        if char in SINGLE_CHAR_OPERATORS:
            flush()
            tokens.append(("Operator", char))
            i += 1
            continue

        current_token += char
        i += 1

    flush()
    return tokens


def scanner(code):
    filtered_code, comments = _strip_comments(code)
    tokens = _tokenize(filtered_code)
    return tokens, comments


if __name__ == "__main__":
    tokens, comments = scanner(codeToBeScanned)
    print("------")
    print(comments)
    print("------")
    print(tokens)
