# fkv - Find Key-Value pairs

A powerful command-line tool for extracting and searching key-value pairs across multiple file formats. The `fkv` tool intelligently detects file formats and extracts keys using both format-specific parsers and stream-based pattern matching.

## Features

- 🔍 **Multi-format support**: JSON, YAML, INI, TOML, XML, Properties, and more
- 🧠 **Smart format detection**: Automatically detects file formats based on content and extension
- 🎯 **Pattern matching**: Search for keys using regex patterns
- 📁 **Directory processing**: Process single files, directories, or recursive directory trees
- 📤 **Multiple output formats**: Plain text, JSON, or CSV output
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
# Extract all keys from a JSON file
fkv config.json

# Find keys matching a pattern
fkv -p "api.*" config.json --show-values

# Process multiple file formats
fkv config.json settings.yaml app.ini

# Recursive directory search
fkv -r /path/to/configs --show-files

# Read from stdin
cat config.json | fkv --show-values

# Output as JSON or CSV
fkv config.json -o json
fkv config.json -o csv --show-values
```

## Usage

```
fkv [OPTIONS] [FILES...]

Arguments:
  FILES                 Files to process (default: stdin)

Options:
  -p, --pattern TEXT    Regex pattern to match keys
  -f, --format          Force specific input format (json|yaml|ini|toml|xml|properties|auto)
  -o, --output          Output format (text|json|csv)
  -c, --case-sensitive  Case-sensitive pattern matching
  -r, --recursive       Recursively process directories
  -v, --verbose         Verbose output
  --show-values         Show values in addition to keys
  --show-files          Show file names in output
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
api_key
database
database.host
database.port
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
api_key
database
database.host
database.port
servers
servers[0].name
servers[0].url
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
# Extract all keys from a file
fkv config.json

# Show both keys and values
fkv config.json --show-values

# Show file names (useful when processing multiple files)
fkv *.json --show-files
```

### Pattern Matching

```bash
# Find all API-related keys
fkv config.json -p "api.*"

# Find all database configuration keys
fkv config.json -p ".*database.*" --show-values

# Case-insensitive search
fkv config.json -p "API.*" --case-sensitive
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

### v0.1.3
- Added comprehensive CLI interface
- Multi-format support (JSON, YAML, INI, TOML, XML, Properties)
- Pattern matching with regex support
- Multiple output formats (text, JSON, CSV)
- Directory and recursive processing
- Enhanced stream-based parsing
- Comprehensive test suite