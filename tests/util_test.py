import asyncio
from pydantic import BaseModel
from typing import List, get_origin, Dict, Optional,Tuple
import os, sys
import asyncio

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from core.utils.utils import schema_str, field_names, has_all_fields, extract_json, check_type_List, check_type
from schemas.write import AIReview


# ---- schema_str test
print(" ")
print("*** schema_str test")
aireview_schema = schema_str(AIReview)
print(aireview_schema)


# ---- field_names
print(" ")
print("*** field_names test")
aireview_fieldnames = field_names(AIReview)
print(aireview_fieldnames)


# ---- has_field
print(" ")
print("*** has_field test")
json_example1 = {
    "overallScore":1,
    "scores": {
        "taskResponse": 5,
        "coherenceCohesion": 6,
        "lexicalResource": 2,
        "grammaticalAccuracy": 1
    },
    "strengths": ["st1 "],
    "improvements": ["imp 1"],
    "suggestions": ["suggestion1", "suggestion 2"]
}
print("* When the json has ALL fields in the list")
print(has_all_fields(json_example1, aireview_fieldnames))
print("* When the json has ALL fields in the list + extra")
json_example1["extra"] = "extra"
print(has_all_fields(json_example1, aireview_fieldnames))

json_example2 = {
    "overallScore":1,
    "scores": {
        "taskResponse": 5,
        "coherenceCohesion": 6,
        "lexicalResource": 2,
        "grammaticalAccuracy": 1
    },
    "strengths": ["st1 "],
    "improvements": ["imp 1"]
#    "suggestions": ["suggestion1", "suggestion 2"] # missing field
}
print("* When the json doesn't have all fields in the list")
print(has_all_fields(json_example2, aireview_fieldnames))

print("* empty json")
print(has_all_fields({}, aireview_fieldnames))

print("* empty list json")
print(has_all_fields(json_example2, []))


print("* both input empty")
print(has_all_fields({}, []))
#




# ---- extract_json quick test (Case 1-4)
print(" ")
print("*** extract_json test")

text1 = 'Some text' #no json
print(extract_json(text1)) 

text2 = 'Some text before {"name": "Alice", "age": 25, "hobby":{"first":1, "second":2}}' # 1 json
print(extract_json(text2)) 

text3 = 'Some text before {"name": "Alice", "age": 25, "hobby":{"' # incomplete json
print(extract_json(text3)) 

text4 = 'Some text before {"name": "Alice", "age": 25, "hobby":{"first":1, "second":2}} and {"hi":1}' #2 json
print(extract_json(text4)) 
    

print(type([1,2,3]) ==list)
print(type([1,2,3]) ==List[int])

print(type([1,2,3]))


# ---- Example ----
print("")
print("*** Check type with List")
print(check_type_List(["a", "b", "c"], "List[str]"))   # ✅ True
print(check_type_List([1, 2, 3], "List[int]"))         # ✅ True
print(check_type_List([1, "b", 3], "List[int]"))       # ❌ False
print(check_type_List("hello", "str"))                 # ✅ True