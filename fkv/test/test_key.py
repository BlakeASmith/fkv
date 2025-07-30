from fkv.parsers.key import keys
from fkv.parsers.primatives import bytestream
import pytest
import json
from io import BytesIO


def test_key():
    input = BytesIO(b'"foo": "bar" fdsahfa aaaf llsls///// "cat"="bar"')
    stream = bytestream(input)

    _keys_offsets = list(keys(stream))
    assert _keys_offsets == [("foo", 1), ("cat", 38)]


def test_key_on_json():
    input = {"foo": {"bar": "value"}, "cat": [7]}
    binary = BytesIO(json.dumps(input).encode('utf-8'))
    stream = bytestream(binary)

    _keys = list(keys(stream))

    # The enhanced parser finds all potential keys, including values
    expected_keys = ["foo", "bar", "value", "cat"]
    actual_keys = [key for key, _ in _keys]
    
    for expected in expected_keys:
        assert expected in actual_keys



