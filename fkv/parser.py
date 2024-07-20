import parsy as p

quote = p.string('"')
token = p.regex(r"\w+")
colon = p.string(':')
period = p.string('.')

digits = p.regex(r"\d+")
_int = digits.map(int)
_float = p.seq(digits, period, digits).map(lambda x: float(x[0] + x[1] + x[2]))
number = _float | _int

value_check = p.peek(p.char_from('{[').optional())


@p.generate
def quoted():
    l = yield quote
    v = yield token
    r = yield quote

    assert l == r
    return v


@p.generate
def json_key():
    v = yield quoted
    yield p.whitespace.optional()
    yield colon
    yield p.whitespace.optional()
    return v


@p.generate
def json_value():
    yield p.whitespace.optional()
    c = yield value_check

    if c == '{':
        v = yield json_value
    elif c == '[':
        v = yield json_list
    else:
        v = yield quoted | number

    yield p.whitespace.optional()

    return v


@p.generate
def json_list():
    lst = []
    yield p.string('[')
    while True:
        yield p.whitespace.optional()
        i = yield json_value.optional()
        yield p.string(',').optional()
        yield p.whitespace.optional()
        if i is not None:
            lst.append(i)
        else:
            yield p.string(']')
            yield p.string(',').optional()
            break
    return lst




@p.generate
def json_kv():
    key = yield json_key
    value = yield json_value
    return key, value
