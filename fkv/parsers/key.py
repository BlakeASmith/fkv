from itertools import takewhile
import re
from fkv.parsers.primatives import LookaheadIterator


KEY_START = '"\''
KEY_END = '"\''
SEPARATORS = ':='
SEPARATOR_DISTANCE = 10
UNQUOTED_KEY_PATTERN = re.compile(r'[a-zA-Z_][a-zA-Z0-9_.-]*')


def keys(stream: LookaheadIterator[str]):
    """Extract keys from a character stream."""
    buffer = ""
    
    for c in stream:
        buffer += c
        
        # Keep buffer to a reasonable size
        if len(buffer) > 100:
            buffer = buffer[-50:]  # Keep last 50 chars
        
        # Check for quoted keys
        if c in KEY_START:
            key = ''.join(takewhile(lambda x: x not in KEY_END, stream))
            if key:  # Only proceed if we found a non-empty key
                after = stream.lookahead(SEPARATOR_DISTANCE)
                if any(_c in SEPARATORS for _c in after):
                    yield key, stream.offset - len(key) - 1
        
        # Check for unquoted keys
        elif c.isalpha() or c == '_':
            # Look backwards to see if we're starting a key
            lookback = stream.lookbehind(1)
            if not lookback or lookback[0] in ' \t\n\r{[,':
                # Potential start of unquoted key
                key_start_pos = stream.offset - 1
                key_chars = [c]
                
                # Continue reading the key
                for next_c in stream.lookahead(20):  # Look ahead up to 20 chars
                    if re.match(r'[a-zA-Z0-9_.-]', next_c):
                        key_chars.append(next_c)
                    else:
                        break
                
                potential_key = ''.join(key_chars)
                
                # Check if there's a separator after the key
                remaining_lookahead = stream.lookahead(min(20, len(key_chars) + SEPARATOR_DISTANCE))
                key_end_idx = len(key_chars)
                
                # Look for separator after key
                separator_found = False
                for i in range(key_end_idx, len(remaining_lookahead)):
                    char = remaining_lookahead[i]
                    if char in SEPARATORS:
                        separator_found = True
                        break
                    elif char not in ' \t':  # Skip whitespace
                        break
                
                if separator_found and len(potential_key) > 1:
                    # Actually consume the key characters
                    for _ in range(len(key_chars) - 1):
                        next(stream)  # Consume the characters we looked ahead
                    yield potential_key, key_start_pos


def extract_keys_simple_patterns(text: str):
    """Extract keys using simple regex patterns for various formats."""
    patterns = [
        # JSON-style: "key": or 'key':
        (r'"([^"]+)"\s*:', 'json'),
        (r"'([^']+)'\s*:", 'json'),
        
        # Properties/INI style: key = value or key: value
        (r'^([a-zA-Z_][a-zA-Z0-9_.-]*)\s*[=:]', 'properties'),
        
        # YAML style: key: value (without quotes)
        (r'^(\s*)([a-zA-Z_][a-zA-Z0-9_.-]*)\s*:', 'yaml'),
        
        # XML attributes: attr="value"
        (r'([a-zA-Z_][a-zA-Z0-9_.-]*)\s*=\s*"[^"]*"', 'xml_attr'),
        
        # TOML style: key = value
        (r'^([a-zA-Z_][a-zA-Z0-9_.-]*)\s*=', 'toml'),
    ]
    
    results = []
    lines = text.split('\n')
    
    for line_num, line in enumerate(lines):
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('//'):
            continue
            
        for pattern, format_type in patterns:
            matches = re.finditer(pattern, line, re.MULTILINE)
            for match in matches:
                key = match.group(1) if match.lastindex >= 1 else match.group(0)
                # For YAML, we might have indentation in group 1
                if format_type == 'yaml' and match.lastindex >= 2:
                    key = match.group(2)
                
                if key and len(key) > 0:
                    results.append((key, line_num * 80 + match.start()))  # Approximate offset
    
    return results



    

