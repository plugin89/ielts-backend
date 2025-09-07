from fastapi import APIRouter
#from src.core.db import db
from src.schemas.write import WritingInput, AIReview

write = APIRouter(prefix="/write", tags=["write"])

@write.post("/review")
async def get_review(writing_input: WritingInput) -> AIReview:
    # getting a writing input and sending an AI review
    
    # static review score (sample). TODO: To be replaced with an actual ai review process.
    aireview = {
        "overallScore": 7.5,
        "scores": {
            "taskResponse": 7.0,
            "coherenceCohesion": 8.0,
            "lexicalResource": 7.5,
            "grammaticalAccuracy": 7.0
        },
        "strengths": [
            "Clear structure with good paragraph organization",
            "Appropriate use of linking words and transitions"
        ],
        "improvements": [
            "Could benefit from more specific examples",
            "Some sentences could be more concise"
        ],
        "suggestions": [
            "Practice writing topic sentences",
            "Work on paraphrasing skills"
        ]
        }
    return aireview

