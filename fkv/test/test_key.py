from fkv.parsers.key import keys
from fkv.parsers.primatives import bytestream
import pytest
import json
from io import BytesIO


def test_key():
    input = BytesIO(b'"foo": "bar" fdsahfa aaaf llsls///// "cat"="bar"')
    stream = bytestream(input)

    _keys_offsets = list(keys(stream))
    assert _keys_offsets == [("foo", 5), ("cat", 42)]


def test_key_on_json():
    input = {"foo": {"bar": "value"}, "cat": [7]}
    binary = BytesIO(json.dumps(input).encode('utf-8'))
    stream = bytestream(binary)

    _keys = keys(stream)

    assert next(_keys) == ("foo", 6)
    assert next(_keys) == ("bar", 14)
    assert next(_keys) == ("cat", 31)

    with pytest.raises(StopIteration):
        _ = next(_keys)



