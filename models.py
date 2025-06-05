"""
Data models for the follow-up questions application.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class Prompt:
    """Model for prompts that can be reused across multiple questions."""
    id: Optional[int] = None
    title: str = ""
    content: str = ""
    model: str = "gemini-2.0-flash"
    temperature: float = 0.7
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Question:
    """Model for questions associated with prompts."""
    id: Optional[int] = None
    prompt_id: int = 0
    question_text: str = ""
    created_at: Optional[datetime] = None


@dataclass
class User:
    """Model for users who provide answers."""
    id: Optional[int] = None
    name: str = ""
    email: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class Answer:
    """Model for user answers to questions."""
    id: Optional[int] = None
    question_id: int = 0
    user_id: int = 0
    answer_text: str = ""
    created_at: Optional[datetime] = None


@dataclass
class FollowupQuestion:
    """Model for AI-generated follow-up questions."""
    id: Optional[int] = None
    answer_id: int = 0
    followup_text: str = ""
    reason: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class Experiment:
    """Model for experiments that test different prompt-question combinations."""
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    prompt_id: int = 0
    created_at: Optional[datetime] = None


@dataclass
class ExperimentCase:
    """Model for individual cases within an experiment."""
    id: Optional[int] = None
    experiment_id: int = 0
    question_id: int = 0
    user_id: int = 0
    is_selected: bool = True
    created_at: Optional[datetime] = None


@dataclass
class QuestionAnswerPair:
    """Combined model for displaying question-answer pairs with follow-ups."""
    question: Question
    answer: Optional[Answer] = None
    user: Optional[User] = None
    followup_questions: List[FollowupQuestion] = None

    def __post_init__(self):
        if self.followup_questions is None:
            self.followup_questions = []


@dataclass
class CaseResult:
    """Model for experiment case results with all related data."""
    case: ExperimentCase
    question: Question
    answer: Answer
    user: User
    followup_questions: List[FollowupQuestion] = None

    def __post_init__(self):
        if self.followup_questions is None:
            self.followup_questions = []
