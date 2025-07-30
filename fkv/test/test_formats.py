import pytest
from fkv.parsers.formats import (
    detect_format, parse_json, parse_ini, parse_properties,
    get_parser_for_format
)


def test_detect_format_by_extension():
    """Test format detection based on file extension."""
    assert detect_format("", ".json") == "json"
    assert detect_format("", ".yaml") == "yaml"
    assert detect_format("", ".ini") == "ini"
    assert detect_format("", ".toml") == "toml"
    assert detect_format("", ".xml") == "xml"
    assert detect_format("", ".properties") == "properties"


def test_detect_format_by_content():
    """Test format detection based on content."""
    json_content = '{"key": "value"}'
    assert detect_format(json_content) == "json"
    
    xml_content = '<root><key>value</key></root>'
    assert detect_format(xml_content) == "xml"
    
    yaml_content = """
    key: value
    nested:
      subkey: subvalue
    """
    assert detect_format(yaml_content) == "yaml"
    
    ini_content = """
    [section]
    key = value
    """
    assert detect_format(ini_content) == "ini"
    
    properties_content = """key=value
another.key=another.value"""
    assert detect_format(properties_content) == "properties"


def test_parse_json():
    """Test JSON parsing."""
    content = '{"key": "value", "nested": {"subkey": 123}}'
    result = parse_json(content)
    assert result == {"key": "value", "nested": {"subkey": 123}}


def test_parse_ini():
    """Test INI parsing."""
    content = """
    [section1]
    key1 = value1
    key2 = 123
    
    [section2]
    key3 = true
    """
    result = parse_ini(content)
    assert "section1" in result
    assert "section2" in result
    assert result["section1"]["key1"] == "value1"
    assert result["section1"]["key2"] == 123
    assert result["section2"]["key3"] is True


def test_parse_properties():
    """Test properties file parsing."""
    content = """
    # Comment
    simple.key=value
    nested.config.value=123
    boolean.value=true
    """
    result = parse_properties(content)
    assert result["simple"]["key"] == "value"
    assert result["nested"]["config"]["value"] == 123
    assert result["boolean"]["value"] is True


def test_get_parser_for_format():
    """Test getting parser functions for different formats."""
    assert get_parser_for_format("json") == parse_json
    assert get_parser_for_format("ini") == parse_ini
    assert get_parser_for_format("properties") == parse_properties
    assert get_parser_for_format("unknown") is None