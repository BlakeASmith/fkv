from fkv.parsers.primatives import ByteStream 
from io import BytesIO


def test_bytestream_does_yield_does_terminate():
    input = BytesIO(b"foobar")
    stream = ByteStream(input)

    assert next(stream) == 'f'
    assert (''.join(c for c in stream)) == "oobar"


def test_bytestream_lookahead_does_not_consume():
    input = BytesIO(b"foobar")
    stream = ByteStream(input)

    assert stream.lookahead() == 'f'
    assert next(stream) == 'f'
    assert stream.lookahead(2) == 'oo'
    assert stream.lookahead(3) == 'oob'
    assert stream.lookahead(4) == 'ooba'
    assert (''.join(c for c in stream)) == "oobar"


def test_lookbehind():
    input = BytesIO(b"foobar")
    stream = ByteStream(input)

    assert next(stream) == 'f'
    assert next(stream) == 'o'
    assert next(stream) == 'o'
    assert stream.lookbehind(2) == 'oo'
    assert next(stream) == 'b'
    assert stream.lookbehind(4) == 'foob'
    assert stream.lookbehind(3) == 'oob'
    assert stream.lookbehind(1) == 'b'
    stream = ByteStream(input)

