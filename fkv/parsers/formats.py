import json
import re
import configparser
from typing import Optional, Dict, Any, Callable
from pathlib import Path


def detect_format(content: str, file_extension: Optional[str] = None) -> str:
    """Detect the file format based on content and extension."""
    
    # First try by file extension
    if file_extension:
        ext = file_extension.lower().lstrip('.')
        if ext in ['json']:
            return 'json'
        elif ext in ['yaml', 'yml']:
            return 'yaml'
        elif ext in ['ini', 'cfg', 'conf']:
            return 'ini'
        elif ext in ['toml']:
            return 'toml'
        elif ext in ['xml']:
            return 'xml'
        elif ext in ['properties', 'props']:
            return 'properties'
    
    # Try to detect by content
    content_stripped = content.strip()
    
    # JSON detection
    if (content_stripped.startswith('{') and content_stripped.endswith('}')) or \
       (content_stripped.startswith('[') and content_stripped.endswith(']')):
        try:
            json.loads(content)
            return 'json'
        except json.JSONDecodeError:
            pass
    
    # XML detection
    if content_stripped.startswith('<') and content_stripped.endswith('>'):
        return 'xml'
    
    # YAML detection (basic heuristics)
    lines = content.split('\n')
    yaml_indicators = 0
    for line in lines[:10]:  # Check first 10 lines
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if ':' in line and not line.startswith('[') and not line.startswith('{'):
            yaml_indicators += 1
        if line.startswith('- '):
            yaml_indicators += 2
    
    if yaml_indicators >= 2:
        return 'yaml'
    
    # INI detection (check first to distinguish from properties)
    ini_indicators = 0
    has_sections = False
    for line in lines[:10]:
        line = line.strip()
        if not line or line.startswith('#') or line.startswith(';'):
            continue
        if line.startswith('[') and line.endswith(']'):
            ini_indicators += 3
            has_sections = True
        if '=' in line and not line.startswith('['):
            ini_indicators += 1
    
    if has_sections and ini_indicators >= 3:
        return 'ini'
    
    # Properties detection (no sections, just key=value pairs)
    props_indicators = 0
    for line in lines[:10]:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' in line or ':' in line:
            props_indicators += 1
    
    if props_indicators >= 2 and not has_sections:
        return 'properties'
    
    # TOML detection
    if any('[' in line and ']' in line for line in lines[:5]):
        return 'toml'
    
    return 'auto'


def parse_json(content: str) -> Dict[str, Any]:
    """Parse JSON content."""
    return json.loads(content)


def parse_yaml(content: str) -> Dict[str, Any]:
    """Parse YAML content."""
    try:
        import yaml
        return yaml.safe_load(content)
    except ImportError:
        raise ImportError("PyYAML is required for YAML support. Install with: pip install PyYAML")


def parse_ini(content: str) -> Dict[str, Any]:
    """Parse INI content."""
    parser = configparser.ConfigParser()
    parser.read_string(content)
    
    result = {}
    for section_name in parser.sections():
        section = {}
        for key, value in parser.items(section_name):
            # Try to convert to appropriate types
            section[key] = _convert_value(value)
        result[section_name] = section
    
    return result


def parse_toml(content: str) -> Dict[str, Any]:
    """Parse TOML content."""
    try:
        import tomllib
        return tomllib.loads(content)
    except ImportError:
        try:
            import toml
            return toml.loads(content)
        except ImportError:
            raise ImportError("tomllib (Python 3.11+) or toml is required for TOML support. Install with: pip install toml")


def parse_xml(content: str) -> Dict[str, Any]:
    """Parse XML content into a dictionary."""
    try:
        import xml.etree.ElementTree as ET
        root = ET.fromstring(content)
        return _xml_to_dict(root)
    except ImportError:
        raise ImportError("xml.etree.ElementTree is required for XML support")


def parse_properties(content: str) -> Dict[str, Any]:
    """Parse Java-style properties content."""
    result = {}
    for line in content.split('\n'):
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('!'):
            continue
        
        # Handle both = and : as separators
        if '=' in line:
            key, value = line.split('=', 1)
        elif ':' in line:
            key, value = line.split(':', 1)
        else:
            continue
        
        key = key.strip()
        value = value.strip()
        
        # Handle nested keys (dot notation)
        keys = key.split('.')
        current = result
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = _convert_value(value)
    
    return result


def _convert_value(value: str) -> Any:
    """Convert string value to appropriate Python type."""
    value = value.strip()
    
    # Remove quotes if present
    if (value.startswith('"') and value.endswith('"')) or \
       (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    
    # Boolean conversion
    if value.lower() in ('true', 'yes', 'on', '1'):
        return True
    elif value.lower() in ('false', 'no', 'off', '0'):
        return False
    
    # Number conversion
    try:
        if '.' in value:
            return float(value)
        else:
            return int(value)
    except ValueError:
        pass
    
    return value


def _xml_to_dict(element) -> Dict[str, Any]:
    """Convert XML element to dictionary."""
    result = {}
    
    # Add attributes
    if element.attrib:
        result.update(element.attrib)
    
    # Add text content
    if element.text and element.text.strip():
        if len(element) == 0:  # No children
            return _convert_value(element.text.strip())
        else:
            result['_text'] = element.text.strip()
    
    # Add children
    children = {}
    for child in element:
        child_data = _xml_to_dict(child)
        if child.tag in children:
            if not isinstance(children[child.tag], list):
                children[child.tag] = [children[child.tag]]
            children[child.tag].append(child_data)
        else:
            children[child.tag] = child_data
    
    result.update(children)
    return result


def get_parser_for_format(file_format: str) -> Optional[Callable[[str], Dict[str, Any]]]:
    """Get the appropriate parser function for a file format."""
    parsers = {
        'json': parse_json,
        'yaml': parse_yaml,
        'ini': parse_ini,
        'toml': parse_toml,
        'xml': parse_xml,
        'properties': parse_properties,
    }
    
    return parsers.get(file_format)