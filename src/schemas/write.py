from pydantic import BaseModel
from typing import List

# Note: pydantic converts json_data into a class obj automatically
# ex. writing_input = WritingInput(**json_data)

# ----- input data class (from frontend)
class WritingInput(BaseModel):
    content: str
    questionId: str
    wordCount: int
    timespent: int
    questionType: str 
    wordlimit: int = -1
    timelimit: int = -1 


# ----- subclasses
class Score(BaseModel):
    taskResponse: float
    coherenceCohesion: float
    lexicalResource: float
    grammaticalAccuracy: float

    @field_validator("*")
    @classmethod
    def validate_scores(cls, v: float) -> float:
        # clamp v to 0-9
        v = max(0, min(v, 9))

        # formatting the score. each score has to be .0 or .5
        if v * 2 != int(v * 2):
            raise ValueError("Scores must be in .0 or .5 steps (e.g. 6.0, 6.5)")
        return round(v, 1)


# ----- AIReview class - LLM has to follow this schema.
class AIReview(BaseModel):
    overallScore: float
    scores: Score
    strengths: List[str]
    improvements: List[str]
    suggestions: List[str]

    @field_validator("overallScore")
    @classmethod
    def validate_overall_score(cls, v: float):
        # clamp v to 0-9
        v = max(0, min(v, 9))

        # formatting the score. each score has to be .0 or .5
        if v * 2 != int(v * 2):
            raise ValueError("overallScore must be in .0 or .5 steps (e.g. 7.0, 7.5)")
        return round(v, 1)

# Sample AI review obj
# {
#  "overallScore": 7.5,
#  "scores": {
#  "taskResponse": 7.0,
#  "coherenceCohesion": 8.0,
#  "lexicalResource": 7.5,
#  "grammaticalAccuracy": 7.0
#  },
#  "strengths": [
#  "Clear structure with good paragraph organization",
#  "Appropriate use of linking words and transitions"
#  ],
#  "improvements": [
#  "Could benefit from more specific examples",
#  "Some sentences could be more concise"
#  ],
#  "suggestions": [
#  "Practice writing topic sentences",
#  "Work on paraphrasing skills"
#  ]
#  }

