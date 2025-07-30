import argparse
import sys
import json
import re
from pathlib import Path
from typing import Optional, List, Dict, Any, Union, Iterator, Tuple
from fkv.parsers.key import keys
from fkv.parsers.primatives import textstream, bytestream
from fkv.parsers.formats import detect_format, get_parser_for_format
from fkv.formatters import format_output


def find_keys_in_stream(stream, search_pattern: Optional[str] = None, 
                       case_sensitive: bool = True) -> Iterator[Tuple[str, int]]:
    """Extract keys from a stream, optionally filtering by pattern."""
    for key, offset in keys(stream):
        if search_pattern:
            pattern = search_pattern if case_sensitive else search_pattern.lower()
            key_to_check = key if case_sensitive else key.lower()
            
            if re.search(pattern, key_to_check):
                yield key, offset
        else:
            yield key, offset


def find_keys_in_text(text: str, file_format: Optional[str] = None,
                     search_pattern: Optional[str] = None,
                     case_sensitive: bool = True) -> List[Dict[str, Any]]:
    """Extract keys from text content with format-specific parsing."""
    results = []
    
    if not file_format or file_format == 'auto':
        file_format = detect_format(text)
    
    # Try format-specific parser first
    parser = get_parser_for_format(file_format)
    if parser and file_format != 'auto':
        try:
            parsed_data = parser(text)
            keys_found = extract_keys_from_data(parsed_data, search_pattern, case_sensitive)
            for key, value in keys_found:
                results.append({
                    'key': key,
                    'value': value,
                    'format': file_format,
                    'offset': None  # Format-specific parsers don't track offset
                })
            # If format-specific parsing worked, return those results
            if results:
                return results
        except Exception as e:
            # Fallback to stream parsing if format-specific parsing fails
            pass
    
    # Use stream-based parsing as fallback
    from io import StringIO
    stream = textstream(StringIO(text))
    for key, offset in find_keys_in_stream(stream, search_pattern, case_sensitive):
        results.append({
            'key': key,
            'value': None,  # Stream parser doesn't extract values
            'format': 'stream',
            'offset': offset
        })
    
    return results


def extract_keys_from_data(data: Any, search_pattern: Optional[str] = None,
                          case_sensitive: bool = True, prefix: str = "") -> List[Tuple[str, Any]]:
    """Recursively extract keys from parsed data structures."""
    results = []
    
    if isinstance(data, dict):
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            # Check if key matches pattern
            if not search_pattern or matches_pattern(full_key, search_pattern, case_sensitive):
                results.append((full_key, value))
            
            # Recursively process nested structures
            if isinstance(value, (dict, list)):
                results.extend(extract_keys_from_data(value, search_pattern, case_sensitive, full_key))
    
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, (dict, list)):
                item_prefix = f"{prefix}[{i}]"
                results.extend(extract_keys_from_data(item, search_pattern, case_sensitive, item_prefix))
    
    return results


def matches_pattern(text: str, pattern: str, case_sensitive: bool = True) -> bool:
    """Check if text matches the given pattern."""
    if not pattern:
        return True
    
    pattern_text = pattern if case_sensitive else pattern.lower()
    text_to_check = text if case_sensitive else text.lower()
    
    try:
        return bool(re.search(pattern_text, text_to_check))
    except re.error:
        # If regex fails, fall back to simple substring matching
        return pattern_text in text_to_check


def process_file(file_path: Path, args) -> List[Dict[str, Any]]:
    """Process a single file and extract keys."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        file_format = args.format or detect_format(content, file_path.suffix)
        results = find_keys_in_text(content, file_format, args.pattern, args.case_sensitive)
        
        # Add file path to results
        for result in results:
            result['file'] = str(file_path)
        
        return results
    
    except Exception as e:
        if args.verbose:
            print(f"Error processing {file_path}: {e}", file=sys.stderr)
        return []


def process_input(args) -> List[Dict[str, Any]]:
    """Process input files or stdin."""
    results = []
    
    if args.files:
        for file_path in args.files:
            path = Path(file_path)
            if path.is_file():
                results.extend(process_file(path, args))
            elif path.is_dir() and args.recursive:
                for file_obj in path.rglob('*'):
                    if file_obj.is_file():
                        results.extend(process_file(file_obj, args))
            elif path.is_dir():
                for file_obj in path.iterdir():
                    if file_obj.is_file():
                        results.extend(process_file(file_obj, args))
    else:
        # Read from stdin
        content = sys.stdin.read()
        results = find_keys_in_text(content, args.format, args.pattern, args.case_sensitive)
        for result in results:
            result['file'] = '<stdin>'
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description='Find key-value pairs in various file formats',
        epilog='''Examples:
  fkv file.json                          # Extract all keys from JSON file
  fkv -p "api.*" file.yaml              # Find keys matching pattern
  fkv -f json -o csv data.txt           # Force JSON format, output as CSV
  cat config.ini | fkv                  # Read from stdin
  fkv -r directory/                     # Recursively process directory
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('files', nargs='*', help='Files to process (default: stdin)')
    parser.add_argument('-p', '--pattern', help='Regex pattern to match keys')
    parser.add_argument('-f', '--format', 
                       choices=['json', 'yaml', 'ini', 'toml', 'xml', 'properties', 'auto'],
                       default='auto', help='Force specific input format')
    parser.add_argument('-o', '--output', 
                       choices=['text', 'json', 'csv'], default='text',
                       help='Output format')
    parser.add_argument('-c', '--case-sensitive', action='store_true',
                       help='Case-sensitive pattern matching')
    parser.add_argument('-r', '--recursive', action='store_true',
                       help='Recursively process directories')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    parser.add_argument('--show-values', action='store_true',
                       help='Show values in addition to keys')
    parser.add_argument('--show-files', action='store_true',
                       help='Show file names in output')
    
    args = parser.parse_args()
    
    try:
        results = process_input(args)
        
        if not results:
            if args.verbose:
                print("No keys found", file=sys.stderr)
            sys.exit(1)
        
        output = format_output(results, args.output, args)
        print(output)
        
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as e:
        if args.verbose:
            raise
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()



