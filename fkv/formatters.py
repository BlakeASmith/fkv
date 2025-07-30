import json
import csv
from io import StringIO
from typing import List, Dict, Any


def format_output(results: List[Dict[str, Any]], output_format: str, args) -> str:
    """Format the results according to the specified output format."""
    
    if output_format == 'json':
        return format_json(results)
    elif output_format == 'csv':
        return format_csv(results, args)
    else:  # default to text
        return format_text(results, args)


def format_text(results: List[Dict[str, Any]], args) -> str:
    """Format results as plain text."""
    lines = []
    
    for result in results:
        parts = []
        
        # Add file name if requested and available
        if args.show_files and result.get('file'):
            parts.append(f"{result['file']}:")
        
        # Add key
        parts.append(result['key'])
        
        # Add value if requested and available
        if args.show_values and result.get('value') is not None:
            value_str = _format_value(result['value'])
            parts.append(f"= {value_str}")
        
        # Add offset if available (for stream parsing)
        if result.get('offset') is not None:
            parts.append(f"(offset: {result['offset']})")
        
        lines.append(' '.join(parts))
    
    return '\n'.join(lines)


def format_json(results: List[Dict[str, Any]]) -> str:
    """Format results as JSON."""
    # Convert results to a more JSON-friendly format
    formatted_results = []
    
    for result in results:
        formatted_result = {
            'key': result['key'],
        }
        
        if result.get('value') is not None:
            formatted_result['value'] = result['value']
        
        if result.get('file'):
            formatted_result['file'] = result['file']
        
        if result.get('format'):
            formatted_result['format'] = result['format']
        
        if result.get('offset') is not None:
            formatted_result['offset'] = result['offset']
        
        formatted_results.append(formatted_result)
    
    return json.dumps(formatted_results, indent=2, default=str)


def format_csv(results: List[Dict[str, Any]], args) -> str:
    """Format results as CSV."""
    output = StringIO()
    
    # Determine columns based on available data
    columns = ['key']
    
    if any(r.get('value') is not None for r in results):
        columns.append('value')
    
    if args.show_files or any(r.get('file') for r in results):
        columns.append('file')
    
    if any(r.get('format') for r in results):
        columns.append('format')
    
    if any(r.get('offset') is not None for r in results):
        columns.append('offset')
    
    writer = csv.DictWriter(output, fieldnames=columns)
    writer.writeheader()
    
    for result in results:
        row = {'key': result['key']}
        
        if 'value' in columns and result.get('value') is not None:
            row['value'] = _format_value(result['value'])
        
        if 'file' in columns:
            row['file'] = result.get('file', '')
        
        if 'format' in columns:
            row['format'] = result.get('format', '')
        
        if 'offset' in columns and result.get('offset') is not None:
            row['offset'] = result['offset']
        
        writer.writerow(row)
    
    return output.getvalue().strip()


def _format_value(value: Any) -> str:
    """Format a value for display."""
    if isinstance(value, (dict, list)):
        return json.dumps(value, separators=(',', ':'))
    elif isinstance(value, str):
        return value
    else:
        return str(value)