from pydantic import BaseModel
from typing import List, get_origin, Dict, Optional,Tuple
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
#DEFAULT_MODEL = "google/gemini-2.0-flash-lite-001"
DEFAULT_MODEL = "cognitivecomputations/dolphin-mistral-24b-venice-edition:free" # free model for dev purpose
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# ----- helper functions
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


def has_field(llm_response: dict, dotted_key: str) -> bool:

    llm_response_text = llm_response["choices"][0]["message"]["content"]
    # check if a JSON data has all fields given as a dotted key
    keys = dotted_key.split(".")
    current = llm_response_text
    for k in keys:
        if not isinstance(current, dict) or k not in current:
            return False
        current = current[k]
    return True


# ---- process/validate llm repsonses
def extract_json(llm_response:str)->Dict|None:
    # Extract json objects in the llm_response
    results = []
    start = -1
    depth = 0

    for i, ch in enumerate(llm_response):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start != -1:
                candidate = llm_response[start:i+1]
                try:
                    results.append(json.loads(candidate))
                except json.JSONDecodeError:
                    pass
                start = -1 

    return results


# quick test (Case 1-4)
# text1 = 'Some text' #no json
# text2 = 'Some text before {"name": "Alice", "age": 25, "hobby":{"first":1, "second":2}}' # 1 json
# text3 = 'Some text before {"name": "Alice", "age": 25, "hobby":{"' # incomplete json
# text3 = 'Some text before {"name": "Alice", "age": 25, "hobby":{"first":1, "second":2}} and {"hi":1}' #2 json
# result = extract_json(text1)
# print(result) 
#     


# ------ Cache
success_cache: Dict[Tuple[str, int], Tuple[Dict, float]] = {}
# Negative cache: (model, prompt_hash) -> (error_info, ts)
negative_cache: Dict[Tuple[str, int], Tuple[Dict, float]] = {}
# Simple in-memory cache: (model, prompt) -> (value, timestamp)
cache: Dict[tuple, tuple] = {}

# ---- llm functions
def _prompt_key(model: str, prompt: str) -> Tuple[str, int]:
    # Use a stable hash to avoid storing giant strings as keys
    return (model, hash(prompt))

def _now() -> float:
    return time.time()

def _not_expired(ts: float, ttl: int) -> bool:
    return (_now() - ts) < ttl

async def get_success_cache(model: str, prompt: str, ttl: int = 86400) -> Optional[Dict]:
    """Return cached successful response if not expired."""
    key = _prompt_key(model, prompt)
    if key in success_cache:
        value, ts = success_cache[key]
        if _not_expired(ts, ttl):
            return value
        # Expired, delete
        del success_cache[key]
    return None


def save_success_cache(model: str, prompt: str, value: Dict) -> None:
    """Save successful response."""
    success_cache[_prompt_key(model, prompt)] = (value, _now())
    # On success, clear any negative cache for the same key
    negative_cache.pop(_prompt_key(model, prompt), None)

async def get_negative_cache(model: str, prompt: str, ttl: int = 30) -> Optional[Dict]:
    """Return cached failure metadata if not expired."""
    key = _prompt_key(model, prompt)
    if key in negative_cache:
        info, ts = negative_cache[key]
        if _not_expired(ts, ttl):
            return info
        del negative_cache[key]
    return None


def save_negative_cache(model: str, prompt: str, error_info: Dict) -> None:
    """Save failure metadata after exhausting retries."""
    negative_cache[_prompt_key(model, prompt)] = (error_info, _now())


async def check_cache(model: str, prompt: str, default_response: Dict,
                      success_ttl: int, negative_ttl: int,
                      respect_negative_cache: bool, probe_on_negative: bool) -> Optional[Dict]:
    """Return cached response (success or negative fallback) if applicable, else None."""
    # success cache
    cached = await get_success_cache(model, prompt, ttl=success_ttl)
    if cached:
        return cached

    # negative cache
    if respect_negative_cache:
        neg = await get_negative_cache(model, prompt, ttl=negative_ttl)
        if neg and not probe_on_negative:
            return {
                "choices": [
                    {"message": {"role": "assistant", "content": default_response.get("text", "[FALLBACK]")}}
                ],
                "_meta": {
                    "is_fallback": True,
                    "is_default_response": False,
                    "is_error": neg.get("error"),
#                    "attempts": 0,
                    "cached_at": neg.get("ts"),
                    "retry_at": neg.get("ts") + negative_ttl if neg.get("ts") else None,
                },
            }
        elif neg and probe_on_negative:
            await asyncio.sleep(random.uniform(0, 0.3))
    return None



async def call_llm(
    prompt: str,
    default_response: Dict,
    api_key: str = OPENROUTER_API_KEY,
    model: str = DEFAULT_MODEL,
#    max_attempt: int = DEFAULT_MAX_ATTEMPT,
    timeout: int = DEFAULT_TIMEOUT,
    success_ttl: int = 86400,
    negative_ttl: int = 30,
    respect_negative_cache: bool = True,
    probe_on_negative: bool = False,
) -> Dict:
    """Unified response: always dict with choices + _meta."""

    # Step 1. Try cache first
    cached = await check_cache(model, prompt, default_response,
                               success_ttl, negative_ttl,
                               respect_negative_cache, probe_on_negative)
    if cached:
        return cached

    # Step 2. Make API call with retries
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": [{"role": "user", "content": prompt}]}

    last_err, last_status, last_text = None, None, None

    async with httpx.AsyncClient(timeout=timeout) as client:
#        for i in range(1, max_attempt + 1):
        try:
            resp = await client.post(url, headers=headers, json=payload)

            if resp.status_code in (429,) or (500 <= resp.status_code < 600):
                # if i < max_attempt:
                #     sleep_s = (2 ** (i - 1)) + random.uniform(0, 0.5)
                #     await asyncio.sleep(sleep_s)
                #     continue
                resp.raise_for_status()

            resp.raise_for_status()
            raw = resp.json()
            wrapped = {
                "choices": raw.get("choices", []),
                "_meta": {"is_fallback": False, "is_default_response": False, "error": None, 
                          #"attempts": i, 
                          "cached_at": _now()},
            }
            save_success_cache(model, prompt, wrapped)
            return wrapped

        except (httpx.TimeoutException, httpx.RequestError) as e:
            last_err = e
            # if i < max_attempt:
            #     await asyncio.sleep((2 ** (i - 1)) + random.uniform(0, 0.5))
            #     continue
        except httpx.HTTPStatusError as e:
            last_err = e
            last_status = e.response.status_code if e.response else None
            try:
                last_text = e.response.text if e.response else None
            except Exception:
                last_text = None
            if last_status and last_status != 429 and not (500 <= last_status < 600):
                break
            # if i < max_attempt:
            #     await asyncio.sleep((2 ** (i - 1)) + random.uniform(0, 0.5))
            #     continue

    # Step 3. All attempts failed → save negative cache + return fallback
    neg_info = {"ts": _now(), "error": str(last_err) or f"status={last_status}, body={last_text}"}
    save_negative_cache(model, prompt, neg_info)
    return {
        "choices": [
            {"message": {"role": "assistant", "content": default_response.get("text", "[FALLBACK]")}}
        ],
        "_meta": {
            "is_fallback": True,
            "is_default_response": True,
            "is_error": neg_info["error"],
#            "attempts": max_attempt,
            "cached_at": neg_info["ts"],
            "retry_at": neg_info["ts"] + negative_ttl,
        },
    }