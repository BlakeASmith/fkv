import pytest
import json
import tempfile
import os
from pathlib import Path
from fkv.main import find_keys_in_text, extract_keys_from_data, matches_pattern


def test_find_keys_in_json_text():
    """Test finding keys in JSON text."""
    json_text = '{"api_key": "secret", "database": {"host": "localhost"}}'
    results = find_keys_in_text(json_text, 'json')
    
    keys = [r['key'] for r in results]
    assert 'api_key' in keys
    assert 'database' in keys
    assert 'database.host' in keys


def test_extract_keys_from_nested_data():
    """Test extracting keys from nested data structures."""
    data = {
        "level1": {
            "level2": {
                "key": "value"
            },
            "array": [
                {"item_key": "item_value"}
            ]
        }
    }
    
    results = extract_keys_from_data(data)
    keys = [key for key, _ in results]
    
    assert "level1" in keys
    assert "level1.level2" in keys
    assert "level1.level2.key" in keys
    assert "level1.array[0].item_key" in keys


def test_pattern_matching():
    """Test pattern matching functionality."""
    assert matches_pattern("api_key", "api.*")
    assert matches_pattern("database.host", ".*host.*")
    assert not matches_pattern("unrelated", "api.*")
    
    # Test case sensitivity
    assert matches_pattern("API_KEY", "api.*", case_sensitive=False)
    assert not matches_pattern("API_KEY", "api.*", case_sensitive=True)


def test_extract_keys_with_pattern():
    """Test extracting keys with pattern filtering."""
    data = {
        "api_key": "secret",
        "api_version": "2.0",
        "database_host": "localhost",
        "database_port": 5432
    }
    
    # Test pattern matching
    api_results = extract_keys_from_data(data, "api.*")
    api_keys = [key for key, _ in api_results]
    assert "api_key" in api_keys
    assert "api_version" in api_keys
    assert "database_host" not in api_keys
    
    db_results = extract_keys_from_data(data, "database.*")
    db_keys = [key for key, _ in db_results]
    assert "database_host" in db_keys
    assert "database_port" in db_keys
    assert "api_key" not in db_keys


def test_find_keys_in_ini_text():
    """Test finding keys in INI text."""
    ini_text = """
    [database]
    host = localhost
    port = 5432
    
    [api]
    version = 2.0
    """
    
    results = find_keys_in_text(ini_text, 'ini')
    keys = [r['key'] for r in results]
    
    assert 'database' in keys
    assert 'database.host' in keys
    assert 'database.port' in keys
    assert 'api' in keys
    assert 'api.version' in keys


def test_find_keys_in_yaml_text():
    """Test finding keys in YAML text."""
    yaml_text = """
    api_key: secret123
    database:
      host: localhost
      port: 5432
    servers:
      - name: web1
        url: https://web1.example.com
    """
    
    results = find_keys_in_text(yaml_text, 'yaml')
    keys = [r['key'] for r in results]
    
    assert 'api_key' in keys
    assert 'database' in keys
    assert 'database.host' in keys
    assert 'database.port' in keys
    assert 'servers' in keys


def test_properties_parsing():
    """Test properties file parsing."""
    props_text = """
    # Configuration
    app.name=MyApp
    app.version=1.0
    database.url=jdbc://localhost:5432
    """
    
    results = find_keys_in_text(props_text, 'properties')
    keys = [r['key'] for r in results]
    
    assert 'app' in keys
    assert 'app.name' in keys
    assert 'app.version' in keys
    assert 'database' in keys
    assert 'database.url' in keys