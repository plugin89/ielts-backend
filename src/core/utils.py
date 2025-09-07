from pydantic import BaseModel
from typing import List, get_origin

def schema_str(model: type[BaseModel], indent: int = 0) -> str:
    # Given a class model, return JSON str - to use it for llm calls
    result = "{\n"
    for name, field in model.__annotations__.items():
        origin = get_origin(field)
        if origin is list:
            result += " " * (indent + 2) + f'"{name}": [str],\n'
        elif isinstance(field, type) and issubclass(field, BaseModel):
            result += " " * (indent + 2) + f'"{name}": ' + schema_str(field, indent + 2) + ",\n"
        else:
            result += " " * (indent + 2) + f'"{name}": {field.__name__},\n'
    result = result.rstrip(",\n") + "\n"
    result += " " * indent + "}"
    return result


def field_names(model: type[BaseModel], prefix: str = "") -> List[str]:
    # Given a class model, make a list of field names as dotted keys.
    names = []
    for name, field in model.__annotations__.items():
        origin = get_origin(field)
        if origin is list:
            names.append(prefix + name)
        elif isinstance(field, type) and issubclass(field, BaseModel):
            names.append(prefix + name)
            names.extend(field_names(field, prefix + name + "."))     # subfields are written as 'superfield.subfield'
        else:
            names.append(prefix + name)
    return names


def has_field(data: dict, dotted_key: str) -> bool:
    # check if a JSON data has all fields given as a dotted key
    keys = dotted_key.split(".")
    current = data
    for k in keys:
        if not isinstance(current, dict) or k not in current:
            return False
        current = current[k]
    return True
