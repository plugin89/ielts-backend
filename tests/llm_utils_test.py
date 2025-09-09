from src.core.utils import *
import asyncio
from pydantic import BaseModel
from typing import List, get_origin, Dict, Optional,Tuple
import os, sys
import asyncio

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src", "core"))
from utils import call_llm

# Testing cachea
default_response = {"text": "default"}

async def test_success():
    # First call: no cache → will hit API (simulate success).
    r1 = await call_llm("hello", default_response)
    print("First call:", r1)
    print("")

    # Second call: within TTL → should return cached response immediately.
    r2 = await call_llm("hello", default_response)
    print("Second call (cached):", r2)
    print("")

asyncio.run(test_success())

print("")
async def test_negative():
    bad_default = {"text": "default"}

    # First call: will try up to max_attempt times, all fail → fallback + negative cache stored
    r1 = await call_llm("bad prompt", bad_default, api_key = "")
    print("First fail call:", r1)
    print("")

    # Second call: happens right after, within negative TTL → should short-circuit immediately
    r2 = await call_llm("bad prompt", bad_default, api_key ="")
    print("Second fail call (negative cache hit):", r2)
    print("")

asyncio.run(test_negative())

