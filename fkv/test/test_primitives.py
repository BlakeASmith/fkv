from fkv.parsers.primatives import bytestream 
import itertools
from io import BytesIO


def test_bytestream_does_yield_does_terminate():
    input = BytesIO(b"foobar")
    stream = bytestream(input)

    assert next(stream) == 'f'
    assert (''.join(c for c in stream)) == "oobar"


def test_bytestream_lookahead_does_not_consume():
    input = BytesIO(b"foobar")
    stream = bytestream(input)

    assert stream.lookahead() == list('f')
    assert next(stream) == 'f'
    assert stream.lookahead(2) == list('oo') 
    assert stream.lookahead(3) == list('oob')
    assert stream.lookahead(4) == list('ooba')
    assert (''.join(c for c in stream)) == "oobar"


def test_lookbehind():
    input = BytesIO(b"foobar")
    stream = bytestream(input)

    assert next(stream) == 'f'
    assert next(stream) == 'o'
    assert next(stream) == 'o'
    assert stream.lookbehind(2) == list('oo')
    assert next(stream) == 'b'
    assert stream.lookbehind(4) == list('foob')
    assert stream.lookbehind(3) == list('oob')
    assert stream.lookbehind(1) == list('b')
    stream = bytestream(input)


def test_looping():
    input = BytesIO(b"foobar")
    stream = bytestream(input)

    for c in stream:
        if c == 'b':
            break

    assert stream.lookbehind() == list('b')
    assert next(stream) == 'a'


def test_itertools_compat():
    input = BytesIO(b"foobar")
    stream = bytestream(input)

    dropping = itertools.dropwhile(lambda x: x != 'b', stream)

    assert next(dropping) == 'b'
    assert stream.lookbehind() == list('b')

    remaining = ''.join(itertools.takewhile(lambda x: x == 'a', stream))
    assert remaining == 'a'


def test_lookahead_does_not_increase_offset():
    input = BytesIO(b"foobar")
    stream = bytestream(input)

    offset = stream.offset

    assert offset == 0
    _ = stream.lookahead(4)
    assert stream.offset == 0

    _ = next(stream)
    assert stream.offset == 1



