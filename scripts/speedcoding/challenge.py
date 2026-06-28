def _clean_lines(src: str):
    return [line.strip() for line in src.splitlines() if line.strip()]


def _strip_decl(lines):
    return [
        line
        for line in lines
        if not line.lower().startswith(("program ", "implicit none", "integer ::", "end program"))
    ]


def _split_args(text: str):
    args, cur, depth, quote = [], "", 0, None
    for ch in text:
        if quote:
            cur += ch
            if ch == quote:
                quote = None
            continue
        if ch in "'\"":
            quote = ch
            cur += ch
        elif ch == "(":
            depth += 1
            cur += ch
        elif ch == ")":
            depth -= 1
            cur += ch
        elif ch == "," and depth == 0:
            args.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        args.append(cur.strip())
    return args


def _tokenize(expr: str):
    tokens, i = [], 0
    while i < len(expr):
        ch = expr[i]
        if ch.isspace():
            i += 1
        elif ch in "'\"":
            j = i + 1
            while j < len(expr) and expr[j] != ch:
                j += 1
            tokens.append(("str", expr[i + 1 : j]))
            i = j + 1
        elif ch.isdigit():
            j = i
            while j < len(expr) and expr[j].isdigit():
                j += 1
            tokens.append(("num", int(expr[i:j])))
            i = j
        elif ch.isalpha() or ch == "_":
            j = i
            while j < len(expr) and (expr[j].isalnum() or expr[j] == "_"):
                j += 1
            tokens.append(("id", expr[i:j].lower()))
            i = j
        elif expr[i : i + 5].lower() in (".and.",):
            tokens.append(("op", "and"))
            i += 5
        elif expr[i : i + 4].lower() in (".eq.", ".ne.", ".gt.", ".ge.", ".lt.", ".le.", ".or."):
            mapping = {".eq.": "==", ".ne.": "!=", ".gt.": ">", ".ge.": ">=", ".lt.": "<", ".le.": "<="}
            value = expr[i : i + 4].lower()
            tokens.append(("op", "or" if value == ".or." else mapping[value]))
            i += 4
        elif expr[i : i + 2] in (">=", "<=", "==", "!=", "/=", "**"):
            tokens.append(("op", "!=" if expr[i : i + 2] == "/=" else expr[i : i + 2]))
            i += 2
        elif ch in "+-*/(),<>":
            tokens.append(("op", ch))
            i += 1
        else:
            i += 1
    return tokens


def _calc_expr(expr, env, funcs):
    tokens, pos = _tokenize(expr), 0

    def peek(value=None):
        if pos >= len(tokens):
            return None
        tok = tokens[pos]
        return tok if value is None or tok[1] == value else None

    def take(value=None):
        nonlocal pos
        tok = peek(value)
        if tok is not None:
            pos += 1
        return tok

    def parse_primary():
        tok = take()
        if tok[0] == "num" or tok[0] == "str":
            return tok[1]
        if tok[1] == "(":
            val = parse_compare()
            take(")")
            return val
        if tok[1] == "-":
            return -parse_primary()
        name = tok[1]
        if take("("):
            args = []
            if not peek(")"):
                while True:
                    args.append(parse_compare())
                    if not take(","):
                        break
            take(")")
            if name == "mod":
                return args[0] % args[1]
            if name == "abs":
                return abs(args[0])
            if name == "min":
                return min(args)
            if name == "max":
                return max(args)
            return _run_function(funcs[name], args, funcs)
        return env.get(name, 0)

    def parse_power():
        val = parse_primary()
        if peek("**"):
            take("**")
            val = val ** parse_power()
        return val

    def parse_mul():
        val = parse_power()
        while peek("*") or peek("/"):
            op = take()[1]
            rhs = parse_power()
            val = val * rhs if op == "*" else val // rhs
        return val

    def parse_add():
        val = parse_mul()
        while peek("+") or peek("-"):
            op = take()[1]
            rhs = parse_mul()
            val = val + rhs if op == "+" else val - rhs
        return val

    def parse_compare():
        val = parse_add()
        if peek() and peek()[1] in (">", "<", ">=", "<=", "==", "!="):
            op = take()[1]
            rhs = parse_add()
            if op == ">":
                return val > rhs
            if op == "<":
                return val < rhs
            if op == ">=":
                return val >= rhs
            if op == "<=":
                return val <= rhs
            if op == "==":
                return val == rhs
            return val != rhs
        return val

    def parse_and():
        val = parse_compare()
        while peek("and"):
            take("and")
            val = bool(val) and bool(parse_compare())
        return val

    def parse_or():
        val = parse_and()
        while peek("or"):
            take("or")
            val = bool(val) or bool(parse_and())
        return val

    return parse_or()


def _find_matching(lines, start, opener, closer):
    depth = 0
    for i in range(start, len(lines)):
        low = lines[i].lower()
        if low.startswith(opener):
            depth += 1
        elif low.startswith(closer):
            depth -= 1
            if depth == 0:
                return i
    return len(lines)


def _exec_block(lines, env, funcs):
    output = ""
    i = 0
    while i < len(lines):
        line = lines[i]
        low = line.lower()
        if low.startswith("print"):
            payload = line.split("*", 1)[1].strip()
            if payload.startswith(","):
                payload = payload[1:].strip()
            values = [_calc_expr(part, env, funcs) for part in _split_args(payload)]
            output += "".join(str(v) for v in values) + "\n"
            i += 1
        elif low.startswith("do "):
            head = line[3:].strip()
            var, bounds = head.split("=", 1)
            parts = _split_args(bounds)
            start_s, end_s = parts[:2]
            step_s = parts[2] if len(parts) > 2 else "1"
            end_i = _find_matching(lines, i, "do ", "end do")
            body = lines[i + 1 : end_i]
            start_v = int(_calc_expr(start_s, env, funcs))
            end_v = int(_calc_expr(end_s, env, funcs))
            step_v = int(_calc_expr(step_s, env, funcs))
            stop_v = end_v + (1 if step_v > 0 else -1)
            for value in range(start_v, stop_v, step_v):
                env[var.strip().lower()] = value
                output += _exec_block(body, env, funcs)
            i = end_i + 1
        elif low.startswith("if ") and low.endswith("then"):
            cond = line[line.find("(") + 1 : line.rfind(")")]
            end_i = _find_matching(lines, i, "if ", "end if")
            depth, else_i = 0, None
            for j in range(i + 1, end_i):
                l2 = lines[j].lower()
                if l2.startswith("if ") and l2.endswith("then"):
                    depth += 1
                elif l2.startswith("end if"):
                    depth -= 1
                elif l2 == "else" and depth == 0:
                    else_i = j
                    break
            if _calc_expr(cond, env, funcs):
                body = lines[i + 1 : else_i if else_i is not None else end_i]
            else:
                body = lines[else_i + 1 : end_i] if else_i is not None else []
            output += _exec_block(body, env, funcs)
            i = end_i + 1
        elif "=" in line and not low.startswith("end "):
            var, expr = line.split("=", 1)
            env[var.strip().lower()] = _calc_expr(expr, env, funcs)
            i += 1
        else:
            i += 1
    return output


def _parse_functions(lines):
    funcs, main = {}, []
    i = 0
    while i < len(lines):
        low = lines[i].lower()
        if low == "contains":
            i += 1
            continue
        if low.startswith("function "):
            header = lines[i]
            name = header.split("function", 1)[1].split("(", 1)[0].strip().lower()
            args_s = header.split("(", 1)[1].split(")", 1)[0]
            result = header.lower().split("result(", 1)[1].split(")", 1)[0].strip()
            end_i = _find_matching(lines, i, "function ", "end function")
            body = _strip_decl(lines[i + 1 : end_i])
            funcs[name] = {"args": [a.strip().lower() for a in _split_args(args_s)], "result": result, "body": body}
            i = end_i + 1
        else:
            main.append(lines[i])
            i += 1
    return _strip_decl(main), funcs


def _run_function(func, args, funcs):
    env = dict(zip(func["args"], args))
    _exec_block(func["body"], env, funcs)
    return env.get(func["result"], 0)


def speedcoding(fortran_file: str) -> str:
    """
    Evaluate a Fortran code

    Args:
        fortran_file: the content of the Fortran file. No file access is needed.

    Returns:
        The evaluation of the Fortran code. It must be a string.
    """

    lines = _clean_lines(fortran_file)
    main, funcs = _parse_functions(lines)
    return _exec_block(main, {}, funcs).rstrip("\n")
