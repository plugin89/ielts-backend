from pydantic import BaseModel
from typing import List, get_origin, Dict, Optional,Tuple, Any
from typing import get_args, get_origin, List
import ast
import requests
import json
import os
import re
import time
import random
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv() 

# ----- global constant
DEFAULT_MAX_ATTEMPT = 5
DEFAULT_TIMEOUT = 20 # 20 sec
DEFAULT_MODEL = "nousresearch/deephermes-3-llama-3-8b-preview:free"
#DEFAULT_MODEL = "cognitivecomputations/dolphin-mistral-24b-venice-edition:free" # free model for dev purpose
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# ----- helper functions
def schema_str(class_model: type[BaseModel], indent: int = 0) -> str:
    # Given a class model, return JSON str - to use it for llm calls
    result = "{\n"
    for name, field in class_model.__annotations__.items():
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


def field_names(class_model: type[BaseModel], prefix: str = "") -> List[str]:
    # Given a class model, make a list of field names as dotted keys.
    names = []
    for name, field in class_model.__annotations__.items():
        origin = get_origin(field)
        if origin is list:
            names.append(prefix + name)
        elif isinstance(field, type) and issubclass(field, BaseModel):
            names.append(prefix + name)
            names.extend(field_names(field, prefix + name + "."))     # subfields are written as 'superfield.subfield'
        else:
            names.append(prefix + name)
    return names


# ------ key checker
def has_field(llm_response_json: dict, dotted_key: str) -> bool:
    # check if a JSON data has the field given as a dotted key (extracted from the schema)

    if dotted_key == None:
        return True
    elif llm_response_json == {}:
        return False

    keys = dotted_key.split(".")
    current = llm_response_json
    for k in keys:
        if not isinstance(current, dict) or k not in current:
            return False
        current = current[k]
    return True


def has_all_fields(llm_response_json:dict, list_dotted_keys: List[str]) -> bool:
    # Handle edge cases (either of them is empty)
    if list_dotted_keys == []:
        return True # even if llmm_response_json =={}, it is true
    elif llm_response_json == {}:
        return False
    
    result_bool = True
    for dotted_key in list_dotted_keys:
        result_bool = result_bool and has_field(llm_response_json, dotted_key)
    
    return result_bool



def check_type_List(obj, type_str: str) -> bool:
    # Parse the string into a Python expression (e.g. "List[str]" -> List[str])
    try:
        parsed_type = eval(type_str, {"List": List, "str": str, "int": int, "float": float, "bool": bool})
    except Exception:
        raise ValueError(f"Unsupported type string: {type_str}")

    origin = get_origin(parsed_type)
    args = get_args(parsed_type)

    # If it's not a parameterized type (like just 'list')
    if origin is None:
        return isinstance(obj, parsed_type)

    # If it's List[T]
    if origin is list and len(args) == 1:
        elem_type = args[0]
        return isinstance(obj, list) and all(isinstance(x, elem_type) for x in obj)

    return False



# TODO: Add type check later.


def check_type(value:Any, type_str: str) -> bool:
    # TODO: Need to rewrite it. - LLM response will be in all str. List checking is not in the same level with the others. 
    try:
        # handling "List" type
        if type_str[:4] == "List":
            # TODO: UPDATE THIS PART
            # For List, just get the str (if exists) in the List["here"], and
            # (1) check if the str is starting with [ ends with ] and, 
            # (2) process the str + check the type using the str.

            return check_type_List(value, type_str)
        
        if type_str == "int":
            int(value)
        elif type_str == "float":
            float(value)
        elif type_str == "bool":
            bool(value)
        elif type_str == "str":
            str(value)
        elif type_str == "list":
            type(value) == list
        else:
            return True
        return True
    except (ValueError, TypeError):
        return False





#llm_response_text = llm_response["choices"][0]["message"]["content"]


# ---- process/validate llm repsonses
def extract_json(llm_response:str)->List|None:
    # Extract json objects in the llm_response
    results = []
    start = -1
    depth = 0

    for ind, character in enumerate(llm_response):
        if character == "{":
            if depth == 0:
                start = ind
            depth += 1
        elif character == "}":
            depth -= 1
            if depth == 0 and start != -1:
                candidate = llm_response[start:ind+1]
                try:
                    results.append(json.loads(candidate))
                except json.JSONDecodeError:
                    pass
                start = -1 

    return results




async def call_llm_without_cache(
    prompt: str,
    default_response: Dict,
    api_key: str = OPENROUTER_API_KEY,
    model: str = DEFAULT_MODEL,
    timeout = 30
) -> Dict:
    # TODO: max_token setting

    # Step 2. Make API call
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": [{"role": "user", "content": prompt}]}


    err = None
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.post(url, headers=headers, json=payload)

            if response.status_code in (429,) or (500 <= response.status_code < 600):
                # if i < max_attempt:
                #     sleep_s = (2 ** (i - 1)) + random.uniform(0, 0.5)
                #     await asyncio.sleep(sleep_s)
                #     continue
                response.raise_for_status()

            response.raise_for_status()
            data = response.json()
            response_json = extract_json(data["choices"][0]["message"]["content"]) # extract_json returns a list, but we only take the first one for now.
            if response_json:
                response_json = response_json[0]
            else:
                response_json = default_response
            return response_json


        except (httpx.TimeoutException, httpx.RequestError) as e:
            err = e
        except httpx.HTTPStatusError as e:
            err = e

    # if failed
    return default_response