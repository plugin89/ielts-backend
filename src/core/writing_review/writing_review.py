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

import asyncio
from pydantic import BaseModel
from typing import List, get_origin, Dict, Optional,Tuple
import os, sys
import asyncio

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from core.utils.utils import call_llm_without_cache, has_all_fields
from schemas.write import WritingInput, AIReview


# ----- Global variables
# TODO: Will be updated to catch the list of class attributes (using util functions)
REVIEW_SCORE_ITEMS = ["taskResponse", "coherenceCohesion", "lexicalResource", "grammaticalAccuracy"]
REVIEW_FEEDBACK_ITEMS = ["strengths", "improvements", "suggestions"]

DEFAULT_REVIEW = {
    "chain_of_thought": "Failed",
    "feedback": ["No feedback."]
}

# TODO: The item description pipeline.
REVIEW_ITEM_JSON = {
    "taskResponse": {
        "scoring_criteria": {
            "description": "How well you answer the question, develop your ideas, and support them with explanations and examples.",
            "score_standards": "# IELTS Writing Task Response Band Descriptors (0–9) \n\n - **Band 9**: Fully addresses all parts of the task.\n\tPresents a clear, fully developed position with strong support.  \n\n - **Band 8**: Fully addresses the task appropriately.\n\tIdeas are clear, relevant, and well-extended with minor lapses.   \n\n - **Band 7**: Covers all parts of the task.\n\tPosition is clear, ideas are developed, but sometimes over-generalized or lacking detail.  \n\n - **Band 6**: Addresses the task, but development may be unclear or repetitive.\n\tArguments may be only partly supported or lack depth.   \n\n - **Band 5**: Only partially addresses the task.\n\tIdeas are limited, repetitive, or not well-focused.  \n\n- **Band 4**: Attempts the task but minimally.\n\tArguments are unclear, irrelevant, or poorly supported.  \n\n- **Band 3**: Barely addresses the task.\n\tVery few ideas, often irrelevant or hard to follow.  \n\n - **Band 2**: Content is barely related to the task.\n\tVery little relevant message.  \n\n - **Band 1**: Only a few isolated words or memorized phrases.\n\tNo real attempt to respond. \n\n - **Band 0**: Did not attempt the task.\n\tWrote in another language or off-topic entirely."
        },
    },
    "coherenceCohesion": {
        "scoring_criteria": {
            "description": "How logically your ideas are organized and how smoothly they are connected using linking words and paragraphing.",
            "score_standards": "## Coherence & Cohesion \n\n - **Band 9**: Ideas flow logically and effortlessly.\n\tCohesive devices are used naturally and effectively; paragraphing is skilfully managed.  \n\n - **Band 8**: Logically sequenced ideas with well-managed cohesion.\n\tOccasional lapses may occur but paragraphing is appropriate.  \n\n - **Band 7**: Clear progression of ideas.\n\tCohesive devices are used flexibly but with some over/under use.  \n\n - **Band 6**: Overall coherence is clear but cohesion may be faulty or mechanical.\n\tParagraphing may not always be logical.  \n\n - **Band 5**: Organisation is evident but not wholly logical.\n\tOveruse/underuse of cohesive devices; referencing may be inaccurate.  \n\n - **Band 4**: Poor organisation, ideas lack progression.\n\tCohesive devices are limited, repetitive, or inaccurate.  \n\n - **Band 3**: No clear organisation.\n\tMinimal or faulty use of cohesion; ideas difficult to follow.  \n\n - **Band 2**: Very little evidence of organisation.\n\tCohesion almost absent.  \n\n - **Band 1**: No organisation or cohesion.\n\tIsolated words only.  \n\n - **Band 0**: Did not attempt the task.\n\tNo meaningful writing."
        }
    },
    "lexicalResource": {
        "scoring_criteria": {
            "description": "The range, accuracy, and appropriacy of your vocabulary, including less common words and collocations.",
            "score_standards": "## Lexical Resource \n\n - **Band 9**: Wide range of vocabulary used precisely and naturally.\n\tVery rare minor errors.  \n\n - **Band 8**: Wide and flexible use of vocabulary.\n\tOccasional inaccuracies in word choice/collocation.  \n\n - **Band 7**: Sufficient range to allow flexibility and precision.\n\tSome less common items are used, though errors inappropriacies occur.  \n\n - **Band 6**: Adequate vocabulary but limited flexibility.\n\tErrors in word choice, spelling, or collocation occur but meaning is clear.  \n\n - **Band 5**: Limited vocabulary.\n\tFrequent repetition and noticeable errors in word choice.  \n\n - **Band 4**: Very basic vocabulary, often repetitive.\n\tErrors may impede meaning.  \n\n - **Band 3**: Inadequate vocabulary with frequent errors.\n\tMeaning often unclear.  \n\n - **Band 2**: Extremely limited vocabulary.\n\tVery few recognisable words.  \n\n - **Band 1**: Only isolated words or memorised phrases.  \n\n - **Band 0**: No English words used."
        },
    },
    "grammaticalAccuracy": {
        "scoring_criteria": {
            "description": "The variety and correctness of your sentence structures, grammar, and punctuation.",
            "score_standards": "## Grammatical Range & Accuracy \n\n - **Band 9**: Wide range of sentence structures.\n\tAccurate, flexible use; errors are extremely rare.  \n\n - **Band 8**: Wide range of structures used accurately.\n\tMost sentences error-free; occasional slips.  \n\n - **Band 7**: Variety of complex structures with good control.\n\tFrequent error-free sentences, but some errors persist.  \n\n - **Band 6**: Mix of simple and complex sentences.\n\tErrors occur but rarely impede communication.  \n\n - **Band 5**: Limited range of structures.\n\tComplex sentences attempted but often faulty; frequent errors.  \n\n - **Band 4**: Very limited sentence forms.\n\tFrequent grammatical errors may impede meaning.  \n\n - **Band 3**: Errors predominate in grammar and punctuation.\n\tMeaning is often unclear.  \n\n - **Band 2**: Almost no control of grammar.\n\tOnly a few words or memorised patterns correct.  \n\n - **Band 1**: No evidence of sentence forms.\n\tOnly isolated words.  \n\n - **Band 0**: Did not attempt the task."
        }
    },
    "strengths": "Identify and list the strengths of the writing.",
    "improvements": "Identify and list the areas for improvement in the writing.",
    "suggestions": "Provide actionable suggestions for improving the writing."
}


# ------------- Processing single review item
# Types of review: Score, Feedback
# They have different prompt and json structure

async def get_one_writing_score_item(
        user_writing_input: WritingInput, 
        review_item_score: str, 
        default_response) -> dict:
    # TODO: max_attempt - currently just one time attempt.
    if review_item_score in REVIEW_SCORE_ITEMS:
        # When the review item is a score item. 

        score_prompt = f"""
You are an IELTS Writing Evaluation Expert. Your role is to evaluate essays strictly based on the **official IELTS Writing Band Descriptors** (Task Achievement/Response, Coherence & Cohesion, Lexical Resource, Grammatical Range & Accuracy).  

# Instructions
1. First, identify whether the essay is **Task 1** or **Task 2**.  
2. Assess the essay in detail only under the given review item indicated in the Evaluation Details section below. (For example, if the criteria is grammar, you only care about grammar, not other aspects)  
3. For each criterion, provide:  
   - **Band Score (0–9)**: A realistic score according to IELTS standards.  

---

# Evaluation Details
- **Task Identification**: {user_writing_input.questionType}
- **Review Item**: {review_item_score}
- **Review Item Description**: {REVIEW_ITEM_JSON[review_item_score]["scoring_criteria"]["description"]}
- **Scoring Standards**:
{REVIEW_ITEM_JSON[review_item_score]["scoring_criteria"]["score_standards"]}

---

# User Essay
- **Topic**: {user_writing_input.topic}
- **Essay**:
{user_writing_input.user_writing}

---

# Output Format
- Output your evaluation results in json format as below.
{{
    "chain_of_thought": str, # give 2-3 sentence reasons for the score value based on the scoring standards
    "value": float
}}.
Do not include anything else.
        """

        llm_response = await call_llm_without_cache(score_prompt, default_response)
        if has_all_fields(llm_response, ["chain_of_thought", "value"]):
            return llm_response
        else:
            default_response        
    else:
        return default_response



async def get_one_writing_feedback(
        user_writing_input, 
        review_item_feedback, 
        ai_score_results, 
        default_review = DEFAULT_REVIEW):
    # TODO: This writing feedback function is depending on the review scores we get from the previous step.
    # Will need to decide the right input/output
    if review_item_feedback  in REVIEW_FEEDBACK_ITEMS:
        # when the review item is a feedback item
        review_prompt = f"""
You are an IELTS Writing Evaluation Expert. Your role is to give users feedback based on the **official IELTS Writing Band Descriptors** (Task Achievement/Response, Coherence & Cohesion, Lexical Resource, Grammatical Range & Accuracy).  

# Instructions
1. First, identify whether the essay is **Task 1** or **Task 2**.  
2. Based on the score results and the essay provided below, give detailed feedback about the user's {review_item_feedback}.

---

# Evaluation Details
- **Task Identification**: {user_writing_input.questionType}
- **Review Item**: {review_item_feedback}
- **Review Item Description**: {REVIEW_ITEM_JSON[review_item_feedback]}

---

# User Essay
- **Topic**: {user_writing_input.topic}
- **Essay**:
{user_writing_input.user_writing}

# Score Results
- **Score evaluation:
{ai_score_results}

---

# Output Format
- Output your evaluation results in json format as below.
{{
    "chain_of_thought": str,
    "feedback": [str] # List of 2-3 specific feedback points for the review item.
}}
Do not include anything else.
"""
        llm_response = await call_llm_without_cache(review_prompt, default_review)
        if has_all_fields(llm_response, ["chain_of_thought", "feedback"]):
            return llm_response
        else:
            default_review        
    else:
        return default_review




def get_overall_score(
        ai_score_results: Optional[Dict[str, Dict[str, object]]] = None,
        fallback: Optional[float] = None,
) -> Optional[float]:
    def _normalise(value: Optional[float]) -> Optional[float]:
        if value is None:
            return None
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return None
        numeric = max(0.0, min(numeric, 9.0))
        return round(numeric * 2) / 2

    if not isinstance(ai_score_results, dict):
        return _normalise(fallback)

    score_values: List[float] = []
    for key in REVIEW_SCORE_ITEMS:
        item = ai_score_results.get(key)
        candidate = item.get("value") if isinstance(item, dict) else item
        try:
            score_values.append(float(candidate))
        except (TypeError, ValueError):
            continue

    if not score_values:
        return _normalise(fallback)

    average_score = sum(score_values) / len(score_values)
    return _normalise(average_score)



# ---------- Main review function to do all review
async def get_writing_review(
        user_writing_input: WritingInput, 
        review_score_items = REVIEW_SCORE_ITEMS,
        review_feedback_items = REVIEW_FEEDBACK_ITEMS) -> AIReview:
    # get_writing_review produce an AIReview
    # Currently only 4 scoring functions are implemented
    default_response_score = {
        "chain_of_thought": "Failed",
        "value": 0
    }

    # Cocurrent call for individual score items
    scoring_tasks = [
        get_one_writing_score_item(user_writing_input, review_score_item, default_response_score)
        for review_score_item in review_score_items
    ]

    scoring_task_results = await asyncio.gather(*scoring_tasks)
    ai_evaluation = dict(zip(review_score_items, [result["value"] for result in scoring_task_results]))

#    ai_evaluation = dict(zip(review_score_items, scoring_task_results["value"]))
    print("++++", scoring_task_results)
    print("evaluation:", ai_evaluation)


    feedback_tasks = [
        get_one_writing_feedback(user_writing_input, review_item_feedback, scoring_task_results) for review_item_feedback in review_feedback_items
    ]

    feedback_task_results = await asyncio.gather(*feedback_tasks)



    # formatting the review results into an AIReview object

    evaluation_results = {
        "overallScore": get_overall_score(ai_evaluation, fallback=list(ai_evaluation.values())[0]),
        "scores": ai_evaluation,
        "strengths": feedback_task_results[0]["feedback"],
        "improvements": feedback_task_results[1]["feedback"],
        "suggestions": feedback_task_results[2]["feedback"],
    }

    print(" +++++ final evaluation results:")
    print(evaluation_results)

    return evaluation_results
