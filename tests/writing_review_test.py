import asyncio
from pydantic import BaseModel
from typing import List, get_origin, Dict, Optional,Tuple
import os, sys
import asyncio

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from core.utils.utils import schema_str, field_names, has_all_fields, extract_json, check_type_List, check_type
from schemas.write import AIReview, WritingInput
from core.writing_review.writing_review import get_one_writing_score_item, get_writing_review



sample = {
    "user_writing": "It is true that some criminals commit crimes again after they have been punished. While there are several reasons for this alarming trend, some effective measures can be taken by governments to tackle this problem.\n\nThere are two main reasons for re-offenders. Firstly, the prison system can make the situation worse. Criminals put together in prison and they make friends with other offenders. While they are locked up in prison, they do not have much to do there, and they would exchange information about what they have done before they came to the prison or they may plan crimes with other inmates. Secondly, offenders often do not have any other means of earning money. They are poor, uneducated and lacking skills needed to maintain a job. Also, a criminal record makes finding a job difficult as people usually avoid hiring ex-convict.\n\nTo solve this problem, governments should focus on rehabilitation of criminals rather than punishment. Above all, prisons need vocational training which makes inmates to prepare for life outside the prison. They can learn practical skills such as computer programming, car maintenance and graphic design. In this way, they can be hired for a position that requires this certain knowledge and skills. Community service is another way to reform offenders. Rather than being locked up in prison with other inmates, offenders can help society and become useful to their local community, and these activities would eliminate the negative influence that prisons can have.\n\nIn conclusion, it is true the re-offenders are one of the problems in our community; it can be solved by focusing rehabilitation rather than punishment itself.",
    "questionId": "",
    "topic": "Why do criminals commit another offence after being punished?",
    "wordCount": 0,
    "timespent": 0,
    "questionType": "Task2"
}

user_writing_input = WritingInput(**sample)

asyncio.run(get_writing_review(user_writing_input))


## llm_response data
# data = {
#     "id": "gen-1758412350-npBQOvAo8iVlbnXKIoBB",
#     "provider": "Venice",
#     "model": "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
#     "object": "chat.completion",
#     "created": 1758412350,
#     "choices": [
#         {
#             "logprobs": None,
#             "finish_reason": "stop",
#             "native_finish_reason": "stop",
#             "index": 0,
#             "message": {
#                 "role": "assistant",
#                 "content": '```json\n{\n    "chain_of_thought": "The essay fully addresses the task by providing reasons for why criminals commit offenses again after being punished and suggesting solutions. The introduction clearly states the main problem and the main body develops two reasons: the negative influence of prisons and the lack of skills and job opportunities. The essay then provides two effective measures: rehabilitation through vocational training and community service. The conclusion effectively summates the main points, reinforcing the need for rehabilitation over punishment. The ideas are clear, relevant, and well-extended, with good explanation and support, which aligns with the description of a Band 8 response.",\n    "value": 8.0\n}\n```',
#                 "refusal": None,
#                 "reasoning": None,
#             },
#         }
#     ],
#     "usage": {"prompt_tokens": 1690, "completion_tokens": 140, "total_tokens": 1830},
# }


# sample1= [{'chain_of_thought': 'The essay fully addresses the task by providing reasons for why criminals commit offenses again after being punished and suggesting solutions. The introduction clearly states the main problem and the main body develops two reasons: the negative influence of prisons and the lack of skills and job opportunities. The essay then provides two effective measures: rehabilitation through vocational training and community service. The conclusion effectively summates the main points, reinforcing the need for rehabilitation over punishment. The ideas are clear, relevant, and well-extended, with good explanation and support, which aligns with the description of a Band 8 response.', 'value': 8.0}]

# print("")
# print('data["choices"][0]["message"]["content"] gives :')
# print(data["choices"][0]["message"]["content"])
# print(extract_json(data["choices"][0]["message"]["content"]))
# #response_json = extract_json(data["choices"][0]["message"]["content"])
