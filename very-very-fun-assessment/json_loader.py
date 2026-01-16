def load_json(file_path):
    """
    Load data from a JSON file.
    
    Args:
        file_path (str): Path to the JSON file.
        
    Returns:
        dict or list: Parsed JSON data.
    """
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        return parse_json(content)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return None

def parse_json(s):
    """
    Parse JSON string manually.
    """
    tokens = tokenize(s)
    if not tokens:
        raise ValueError("Empty JSON")
    result, _ = parse_value(tokens, 0)
    return result

def tokenize(s):
    """
    Simple tokenizer for JSON.
    """
    tokens = []
    i = 0
    while i < len(s):
        if s[i].isspace():
            i += 1
            continue
        if s[i] in '{}[],:':
            tokens.append(s[i])
            i += 1
        elif s[i] == '"':
            start = i
            i += 1
            while i < len(s) and s[i] != '"':
                if s[i] == '\\':
                    i += 2
                else:
                    i += 1
            if i >= len(s):
                raise ValueError("Unclosed string")
            tokens.append(s[start:i+1])
            i += 1
        elif s[i].isdigit() or s[i] == '-':
            start = i
            while i < len(s) and (s[i].isdigit() or s[i] in '.-eE'):
                i += 1
            tokens.append(s[start:i])
        elif s.startswith('true', i):
            tokens.append('true')
            i += 4
        elif s.startswith('false', i):
            tokens.append('false')
            i += 5
        elif s.startswith('null', i):
            tokens.append('null')
            i += 4
        else:
            raise ValueError(f"Invalid character: {s[i]}")
    return tokens

def parse_value(tokens, index):
    token = tokens[index]
    if token == '{':
        return parse_object(tokens, index)
    elif token == '[':
        return parse_array(tokens, index)
    elif token.startswith('"'):
        return token[1:-1], index + 1  # Remove quotes
    elif token == 'true':
        return True, index + 1
    elif token == 'false':
        return False, index + 1
    elif token == 'null':
        return None, index + 1
    else:
        # Number
        try:
            if '.' in token or 'e' in token.lower():
                return float(token), index + 1
            else:
                return int(token), index + 1
        except ValueError:
            raise ValueError(f"Invalid number: {token}")

def parse_object(tokens, index):
    obj = {}
    i = index + 1  # Skip '{'
    while i < len(tokens) and tokens[i] != '}':
        if tokens[i].startswith('"'):
            key = tokens[i][1:-1]
        else:
            raise ValueError("Expected string key")
        i += 1
        if tokens[i] != ':':
            raise ValueError("Expected ':'")
        i += 1
        value, i = parse_value(tokens, i)
        obj[key] = value
        if tokens[i] == ',':
            i += 1
    if i >= len(tokens) or tokens[i] != '}':
        raise ValueError("Unclosed object")
    return obj, i + 1

def parse_array(tokens, index):
    arr = []
    i = index + 1  # Skip '['
    while i < len(tokens) and tokens[i] != ']':
        value, i = parse_value(tokens, i)
        arr.append(value)
        if tokens[i] == ',':
            i += 1
    if i >= len(tokens) or tokens[i] != ']':
        raise ValueError("Unclosed array")
    return arr, i + 1

def dump_json(data, file_path):
    """
    Save data to a JSON file by manually serializing.
    
    Args:
        data: Data to save (dict or list).
        file_path (str): Path to save the JSON file.
    """
    try:
        json_str = _to_json_string(data)
        with open(file_path, 'w') as f:
            f.write(json_str)
    except Exception as e:
        print(f"Error saving JSON: {e}")

def _to_json_string(obj, indent=4, level=0):
    """
    Convert Python object to JSON string.
    Supports dict, list, str, int, float, bool, None.
    """
    indent_str = ' ' * (indent * level)
    next_indent_str = ' ' * (indent * (level + 1))
    
    if isinstance(obj, dict):
        if not obj:
            return '{}'
        items = []
        for k, v in obj.items():
            items.append(f'{next_indent_str}"{k}": {_to_json_string(v, indent, level + 1)}')
        return '{\n' + ',\n'.join(items) + f'\n{indent_str}}}'
    elif isinstance(obj, list):
        if not obj:
            return '[]'
        items = [_to_json_string(item, indent, level + 1) for item in obj]
        return '[\n' + ',\n'.join(f'{next_indent_str}{item}' for item in items) + f'\n{indent_str}]'
    elif isinstance(obj, str):
        # Escape quotes and backslashes
        escaped = obj.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t')
        return f'"{escaped}"'
    elif isinstance(obj, bool):
        return 'true' if obj else 'false'
    elif obj is None:
        return 'null'
    elif isinstance(obj, (int, float)):
        return str(obj)
    else:
        raise TypeError(f"Unsupported type: {type(obj)}")

# Add other JSON-related functions if needed, like json.dumps, json.loads
def loads_json(json_string):
    """
    Parse JSON string.
    
    Args:
        json_string (str): JSON string.
        
    Returns:
        dict or list: Parsed data.
    """
    try:
        return parse_json(json_string)
    except Exception as e:
        print(f"Error parsing JSON string: {e}")
        return None

def dumps_json(data):
    """
    Convert data to JSON string.
    
    Args:
        data: Data to convert.
        
    Returns:
        str: JSON string.
    """
    try:
        return _to_json_string(data)
    except Exception as e:
        print(f"Error converting to JSON string: {e}")
        return None