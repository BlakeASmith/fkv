# fkv - Find Key-Value pairs

A powerful command-line tool for finding specific keys and their values across multiple file formats. The `fkv` tool is designed to quickly locate configuration values, API keys, passwords, and other key-value pairs in your configuration files.

## Features

- 🔑 **Key-focused search**: Find specific keys and their values quickly
- 🎯 **Pattern matching**: Search for keys using regex patterns or exact matches
- 🔍 **Multi-format support**: JSON, YAML, INI, TOML, XML, Properties, and more
- 🧠 **Smart format detection**: Automatically detects file formats based on content and extension
- 📁 **Directory processing**: Search across multiple files and directories recursively
- 📤 **Multiple output formats**: Plain text, JSON, or CSV output with values shown by default
- 🔧 **Flexible parsing**: Stream-based parsing for any key-value pattern
- ⚡ **Fast and efficient**: Built for performance with large files and directories

## Installation

Install using Poetry (recommended):

```bash
poetry install
```

Or install dependencies manually:

```bash
pip install parsy PyYAML
```

## Quick Start

```bash
# Find a specific key and its value
fkv -k api_key config.json

# Find nested key values
fkv -k "database.password" config.json

# Find all keys matching a pattern
fkv -p "api.*" config.json

# Search recursively through directories
fkv -k password -r /etc/configs/

# Exact key match (no regex)
fkv --exact-match -k database config.json

# Read from stdin
cat config.json | fkv -k api_key

# Show only keys (no values)
fkv --keys-only config.json
```

## Usage

```
fkv [OPTIONS] [FILES...]

Arguments:
  FILES                 Files to process (default: stdin)

Options:
  -k, --key KEY         Specific key to search for (exact match or regex pattern)
  -p, --pattern TEXT    Regex pattern to match keys (alias for --key)
  -f, --format          Force specific input format (json|yaml|ini|toml|xml|properties|auto)
  -o, --output          Output format (text|json|csv)
  -c, --case-sensitive  Case-sensitive pattern matching
  -r, --recursive       Recursively process directories
  -v, --verbose         Verbose output
  --keys-only           Show only keys (no values)
  --show-files          Show file names in output
  --exact-match         Exact key match instead of regex pattern
  -h, --help           Show help message
```

## Supported Formats

### JSON
```json
{
  "api_key": "secret123",
  "database": {
    "host": "localhost",
    "port": 5432
  }
}
```

**Output:**
```
api_key = secret123
database = {"host":"localhost","port":5432}
database.host = localhost
database.port = 5432
```

### YAML
```yaml
api_key: secret123
database:
  host: localhost
  port: 5432
servers:
  - name: web1
    url: https://web1.example.com
```

**Output:**
```
api_key = secret123
database = {"host":"localhost","port":5432}
database.host = localhost
database.port = 5432
servers = [{"name":"web1","url":"https://web1.example.com"}]
servers[0].name = web1
servers[0].url = https://web1.example.com
```

### INI Files
```ini
[database]
host = localhost
port = 5432

[api]
version = 2.0
timeout = 30
```

**Output:**
```
database
database.host
database.port
api
api.version
api.timeout
```

### Properties Files
```properties
app.name=MyApplication
app.version=1.0
database.url=jdbc://localhost:5432
logging.level=INFO
```

**Output:**
```
app
app.name
app.version
database
database.url
logging
logging.level
```

### XML
```xml
<config>
  <database host="localhost" port="5432">
    <name>myapp</name>
  </database>
  <api version="2.0"/>
</config>
```

**Output:**
```
config
config.database
config.database.host
config.database.port
config.database.name
config.api
config.api.version
```

## Examples

### Basic Usage

```bash
# Find a specific key
fkv -k api_key config.json

# Find nested keys
fkv -k "database.host" config.json

# Show all keys and values
fkv config.json

# Show only keys (no values)
fkv --keys-only config.json
```

### Pattern Matching

```bash
# Find all API-related keys and values
fkv -p "api.*" config.json

# Find all database configuration keys
fkv -p ".*database.*" config.json

# Case-insensitive search
fkv -p "API.*" config.json

# Exact key match (no regex)
fkv --exact-match -k database config.json
```

### Directory Processing

```bash
# Process all files in a directory
fkv /path/to/configs/

# Recursively process all configuration files
fkv -r /etc/ -p ".*password.*"

# Process specific file types recursively
fkv -r . -p ".*" --show-files | grep -E "\.(json|yaml|yml):"
```

### Output Formats

```bash
# JSON output
fkv config.json --show-values -o json

# CSV output for spreadsheet analysis
fkv -r configs/ --show-values --show-files -o csv > keys.csv

# Plain text (default)
fkv config.json --show-values
```

### Working with stdin

```bash
# Process output from other commands
curl -s https://api.example.com/config | fkv --show-values

# Process data from multiple sources
cat *.json | fkv -p "api.*"

# Use with jq for complex JSON processing
jq '.config' data.json | fkv --show-values
```

## Advanced Features

### Format Detection

The tool automatically detects file formats based on:
1. File extension (.json, .yaml, .ini, etc.)
2. Content analysis (JSON structure, YAML syntax, etc.)
3. Heuristic patterns

You can override detection with the `-f` flag:

```bash
# Force JSON parsing on a file without extension
fkv -f json mystery_file

# Force properties parsing
fkv -f properties config.txt
```

### Stream-based Parsing

In addition to format-specific parsing, `fkv` uses stream-based parsing to find key-value patterns in any text:

- Quoted keys: `"key": value`
- Unquoted keys: `key = value`
- Various separators: `:`, `=`

This makes it work even with non-standard or mixed formats.

### Nested Key Notation

Nested keys are represented using dot notation:
- `config.database.host`
- `users[0].name`
- `settings.api.endpoints[2].url`

### Regular Expressions

Pattern matching supports full regex syntax:

```bash
# Keys starting with 'api'
fkv -p "^api"

# Keys ending with 'url' or 'uri'
fkv -p ".*(url|uri)$"

# Keys containing numbers
fkv -p ".*[0-9].*"

# Complex patterns
fkv -p "(api|auth|security)\..*\.key"
```

## Performance

- **Streaming**: Processes large files without loading them entirely into memory
- **Parallel**: Can process multiple files efficiently
- **Optimized**: Format-specific parsers for better accuracy and speed
- **Scalable**: Works with directories containing thousands of files

## Error Handling

- **Graceful degradation**: Falls back to stream parsing if format-specific parsing fails
- **Partial results**: Continues processing even if some files fail
- **Verbose mode**: Use `-v` for detailed error messages

## Exit Codes

- `0`: Success, keys found
- `1`: No keys found or error occurred

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass: `python -m pytest`
5. Submit a pull request

## License

This project is open source. See LICENSE file for details.

## Changelog

### v0.2.0
- **KEY-FOCUSED REDESIGN**: Tool now focuses on finding specific keys and their values
- **Values shown by default**: No need for --show-values flag anymore
- **Enhanced key search**: New -k/--key option for specific key lookup
- **Exact matching**: --exact-match option for precise key matching (no regex)
- **Improved UX**: Better error messages and help examples focused on key search
- **Backwards compatible**: All existing functionality preserved

### v0.1.3
- Added comprehensive CLI interface
- Multi-format support (JSON, YAML, INI, TOML, XML, Properties)
- Pattern matching with regex support
- Multiple output formats (text, JSON, CSV)
- Directory and recursive processing
- Enhanced stream-based parsing
- Comprehensive test suite