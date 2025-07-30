import pytest
from fkv.main import matches_pattern, extract_keys_from_data


def test_exact_match_functionality():
    """Test exact key matching vs regex matching."""
    # Test exact match
    assert matches_pattern("database", "database", exact_match=True)
    assert not matches_pattern("database.host", "database", exact_match=True)
    assert not matches_pattern("my_database", "database", exact_match=True)
    
    # Test regex match (default)
    assert matches_pattern("database", "database", exact_match=False)
    assert matches_pattern("database.host", "database", exact_match=False)
    assert matches_pattern("my_database", "database", exact_match=False)


def test_case_sensitive_exact_match():
    """Test case sensitivity with exact matching."""
    assert matches_pattern("Database", "database", case_sensitive=False, exact_match=True)
    assert not matches_pattern("Database", "database", case_sensitive=True, exact_match=True)


def test_extract_keys_with_exact_match():
    """Test extracting keys with exact match filtering."""
    data = {
        "database": {"host": "localhost"},
        "database_url": "postgres://localhost",
        "my_database": {"name": "test"}
    }
    
    # Exact match should only find "database"
    exact_results = extract_keys_from_data(data, "database", exact_match=True)
    exact_keys = [key for key, _ in exact_results]
    assert "database" in exact_keys
    assert "database_url" not in exact_keys
    assert "my_database" not in exact_keys
    
    # Regex match should find all containing "database"
    regex_results = extract_keys_from_data(data, "database", exact_match=False)
    regex_keys = [key for key, _ in regex_results]
    assert "database" in regex_keys
    assert "database_url" in regex_keys
    assert "my_database" in regex_keys


def test_key_focused_search():
    """Test the key-focused search approach."""
    data = {
        "api_key": "secret123",
        "api_version": "2.0",
        "database": {
            "host": "localhost",
            "password": "secret_pass"
        }
    }
    
    # Search for API keys
    api_results = extract_keys_from_data(data, "api.*")
    api_pairs = [(key, value) for key, value in api_results]
    
    assert ("api_key", "secret123") in api_pairs
    assert ("api_version", "2.0") in api_pairs
    
    # Search for password
    password_results = extract_keys_from_data(data, ".*password.*")
    password_pairs = [(key, value) for key, value in password_results]
    
    assert ("database.password", "secret_pass") in password_pairs


def test_nested_key_exact_match():
    """Test exact matching with nested keys."""
    data = {
        "config": {
            "database": {"host": "localhost"},
            "database_backup": {"host": "backup.localhost"}
        }
    }
    
    # Exact match for nested key
    results = extract_keys_from_data(data, "config.database", exact_match=True)
    keys = [key for key, _ in results]
    
    assert "config.database" in keys
    assert "config.database_backup" not in keys
    assert len([k for k in keys if k == "config.database"]) == 1


def test_empty_pattern_returns_all():
    """Test that empty pattern returns all keys."""
    data = {"key1": "value1", "key2": "value2"}
    
    results = extract_keys_from_data(data, "")
    assert len(results) == 2
    
    results = extract_keys_from_data(data, None)
    assert len(results) == 2