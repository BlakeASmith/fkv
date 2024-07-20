import parsy as p
import pytest

from fkv.parser import quoted, json_key, number, json_kv


def test_number():
    assert number.parse("14") == 14
    assert number.parse("14.4") == 14.4
    assert number.parse("199.9877777") == 199.9877777
    assert number.parse("1.0") == 1.0 == 1


def test_quoted_str_matches_quoted_does_not_match_jsonkey():
    quoted_str = '"key"'
    v = quoted.parse(quoted_str)
    assert v == "key"
    with pytest.raises(p.ParseError):
        json_key.parse(quoted_str)


def test_jsonkey_matches():
    for _key in (
            '"key":',
            '"key": ',
            '"key" : ',
            '"key" :',
    ):
        v = json_key.parse(_key)
        assert v == "key"


def test_json_kv_matches():
    for _kv in (
        '"key":"value"',
        '"key": "value"',
        '"key": "value" ',
        '"key" : "value" ',
    ):
        v = json_kv.parse(_kv)
        assert v == ("key", "value")

    v = json_kv.parse('"key": 7')
    assert v == ("key", 7)

    v = json_kv.parse('"key": 7.998')
    assert v == ("key", 7.998)
