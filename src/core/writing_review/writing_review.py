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

import asyncio
from pydantic import BaseModel
from typing import List, get_origin, Dict, Optional,Tuple
import os, sys
import asyncio

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from core.utils.utils import call_llm


load_dotenv() 

ITEM_JSON = {
    "taskResponse": {
        "scoring_criteria": "...",
    },
    "coherenceCohesion": {
        "scoring_criteria": "...",
    },
    "lexicalResource": {
        "scoring_criteria": "...",
    },
    "grammaticalAccuracy": {
        "scoring_criteria": "...",
    },
    "strengths": {
        "Identify and list the strengths of the writing."
    },
    "improvements": {
        "Identify and list the areas for improvement in the writing."
    },
    "suggestions": {
        "Provide actionable suggestions for improving the writing."
    }
}

async def get_writing_review(user_writing: str, review_item: str = []) -> dict:
    if review_item == []:
        return response
    default_response = {"text": "default"}
    response = await call_llm(prompt, default_response)
    return response