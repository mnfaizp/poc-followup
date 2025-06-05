"""
Database operations using Supabase for the follow-up questions application.
"""
import os
from typing import List, Optional, Dict, Any
from supabase import create_client, Client
from models import Prompt, Question, Answer, FollowupQuestion, User, Experiment, ExperimentCase, CaseResult
import streamlit as st


class DatabaseManager:
    """Manages all database operations with Supabase."""

    def __init__(self):
        """Initialize Supabase client."""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

        try:
            self.supabase: Client = create_client(supabase_url, supabase_key)
        except Exception as e:
            raise Exception(f"Failed to initialize Supabase client: {str(e)}")
    
    # Prompt operations
    def create_prompt(self, title: str, content: str, model: str = "gemini-2.0-flash", temperature: float = 0.7) -> Optional[Prompt]:
        """Create a new prompt."""
        try:
            result = self.supabase.table("prompts").insert({
                "title": title,
                "content": content,
                "model": model,
                "temperature": temperature
            }).execute()

            if result.data:
                data = result.data[0]
                return Prompt(
                    id=data["id"],
                    title=data["title"],
                    content=data["content"],
                    model=data.get("model", "gemini-2.0-flash"),
                    temperature=float(data.get("temperature", 0.7)),
                    created_at=data["created_at"],
                    updated_at=data["updated_at"]
                )
        except Exception as e:
            st.error(f"Error creating prompt: {str(e)}")
        return None
    
    def get_all_prompts(self) -> List[Prompt]:
        """Get all prompts."""
        try:
            result = self.supabase.table("prompts").select("*").order("created_at", desc=True).execute()

            prompts = []
            for data in result.data:
                prompts.append(Prompt(
                    id=data["id"],
                    title=data["title"],
                    content=data["content"],
                    model=data.get("model", "gemini-2.0-flash"),
                    temperature=float(data.get("temperature", 0.7)),
                    created_at=data["created_at"],
                    updated_at=data["updated_at"]
                ))
            return prompts
        except Exception as e:
            st.error(f"Error fetching prompts: {str(e)}")
            return []
    
    def update_prompt(self, prompt_id: int, title: str, content: str, model: str = "gemini-2.0-flash", temperature: float = 0.7) -> bool:
        """Update an existing prompt."""
        try:
            result = self.supabase.table("prompts").update({
                "title": title,
                "content": content,
                "model": model,
                "temperature": temperature
            }).eq("id", prompt_id).execute()

            return len(result.data) > 0
        except Exception as e:
            st.error(f"Error updating prompt: {str(e)}")
            return False
    
    def delete_prompt(self, prompt_id: int) -> bool:
        """Delete a prompt and all associated data."""
        try:
            # Delete in order: followup_questions -> answers -> questions -> prompt
            questions = self.get_questions_by_prompt(prompt_id)
            for question in questions:
                answers = self.get_answers_by_question(question.id)
                for answer in answers:
                    self.supabase.table("followup_questions").delete().eq("answer_id", answer.id).execute()
                self.supabase.table("answers").delete().eq("question_id", question.id).execute()
            
            self.supabase.table("questions").delete().eq("prompt_id", prompt_id).execute()
            result = self.supabase.table("prompts").delete().eq("id", prompt_id).execute()
            
            return len(result.data) > 0
        except Exception as e:
            st.error(f"Error deleting prompt: {str(e)}")
            return False

    # Question operations
    def create_question(self, prompt_id: int, question_text: str) -> Optional[Question]:
        """Create a new question for a prompt."""
        try:
            result = self.supabase.table("questions").insert({
                "prompt_id": prompt_id,
                "question_text": question_text
            }).execute()

            if result.data:
                data = result.data[0]
                return Question(
                    id=data["id"],
                    prompt_id=data["prompt_id"],
                    question_text=data["question_text"],
                    created_at=data["created_at"]
                )
        except Exception as e:
            st.error(f"Error creating question: {str(e)}")
        return None

    def get_questions_by_prompt(self, prompt_id: int) -> List[Question]:
        """Get all questions for a specific prompt."""
        try:
            result = self.supabase.table("questions").select("*").eq("prompt_id", prompt_id).order("created_at").execute()

            questions = []
            for data in result.data:
                questions.append(Question(
                    id=data["id"],
                    prompt_id=data["prompt_id"],
                    question_text=data["question_text"],
                    created_at=data["created_at"]
                ))
            return questions
        except Exception as e:
            st.error(f"Error fetching questions: {str(e)}")
            return []

    def delete_question(self, question_id: int) -> bool:
        """Delete a question and all associated answers and follow-ups."""
        try:
            # Delete followup_questions -> answers -> question
            answers = self.get_answers_by_question(question_id)
            for answer in answers:
                self.supabase.table("followup_questions").delete().eq("answer_id", answer.id).execute()

            self.supabase.table("answers").delete().eq("question_id", question_id).execute()
            result = self.supabase.table("questions").delete().eq("id", question_id).execute()

            return len(result.data) > 0
        except Exception as e:
            st.error(f"Error deleting question: {str(e)}")
            return False

    # Answer operations
    def create_or_update_answer(self, question_id: int, user_id: int, answer_text: str) -> Optional[Answer]:
        """Create a new answer or update existing answer for a question and user."""
        try:
            # Check if answer already exists for this question and user
            existing = self.supabase.table("answers").select("*").eq("question_id", question_id).eq("user_id", user_id).execute()

            if existing.data:
                # Update existing answer
                result = self.supabase.table("answers").update({
                    "answer_text": answer_text
                }).eq("question_id", question_id).eq("user_id", user_id).execute()
            else:
                # Create new answer
                result = self.supabase.table("answers").insert({
                    "question_id": question_id,
                    "user_id": user_id,
                    "answer_text": answer_text
                }).execute()

            if result.data:
                data = result.data[0]
                return Answer(
                    id=data["id"],
                    question_id=data["question_id"],
                    user_id=data["user_id"],
                    answer_text=data["answer_text"],
                    created_at=data["created_at"]
                )
        except Exception as e:
            st.error(f"Error creating/updating answer: {str(e)}")
        return None

    def get_answers_by_question(self, question_id: int) -> List[Answer]:
        """Get all answers for a specific question."""
        try:
            result = self.supabase.table("answers").select("*").eq("question_id", question_id).execute()

            answers = []
            for data in result.data:
                answers.append(Answer(
                    id=data["id"],
                    question_id=data["question_id"],
                    user_id=data["user_id"],
                    answer_text=data["answer_text"],
                    created_at=data["created_at"]
                ))
            return answers
        except Exception as e:
            st.error(f"Error fetching answers: {str(e)}")
            return []

    def get_answer_by_question_and_user(self, question_id: int, user_id: int) -> Optional[Answer]:
        """Get the answer for a specific question and user."""
        try:
            result = self.supabase.table("answers").select("*").eq("question_id", question_id).eq("user_id", user_id).execute()

            if result.data:
                data = result.data[0]
                return Answer(
                    id=data["id"],
                    question_id=data["question_id"],
                    user_id=data["user_id"],
                    answer_text=data["answer_text"],
                    created_at=data["created_at"]
                )
        except Exception as e:
            st.error(f"Error fetching answer: {str(e)}")
        return None

    def get_answer_by_question(self, question_id: int) -> Optional[Answer]:
        """Get the first answer for a specific question (for backward compatibility)."""
        answers = self.get_answers_by_question(question_id)
        return answers[0] if answers else None

    # Follow-up question operations
    def create_followup_question(self, answer_id: int, followup_text: str, reason: Optional[str] = None) -> Optional[FollowupQuestion]:
        """Create a new follow-up question for an answer."""
        try:
            result = self.supabase.table("followup_questions").insert({
                "answer_id": answer_id,
                "followup_text": followup_text,
                "reason": reason
            }).execute()

            if result.data:
                data = result.data[0]
                return FollowupQuestion(
                    id=data["id"],
                    answer_id=data["answer_id"],
                    followup_text=data["followup_text"],
                    reason=data.get("reason"),
                    created_at=data["created_at"]
                )
        except Exception as e:
            st.error(f"Error creating follow-up question: {str(e)}")
        return None

    def get_followups_by_answer(self, answer_id: int) -> List[FollowupQuestion]:
        """Get all follow-up questions for a specific answer."""
        try:
            result = self.supabase.table("followup_questions").select("*").eq("answer_id", answer_id).order("created_at").execute()

            followups = []
            for data in result.data:
                followups.append(FollowupQuestion(
                    id=data["id"],
                    answer_id=data["answer_id"],
                    followup_text=data["followup_text"],
                    reason=data.get("reason"),
                    created_at=data["created_at"]
                ))
            return followups
        except Exception as e:
            st.error(f"Error fetching follow-up questions: {str(e)}")
            return []

    def clear_followups_by_answer(self, answer_id: int) -> bool:
        """Clear all existing follow-up questions for an answer."""
        try:
            result = self.supabase.table("followup_questions").delete().eq("answer_id", answer_id).execute()
            return True
        except Exception as e:
            st.error(f"Error clearing follow-up questions: {str(e)}")
            return False

    # User operations
    def create_user(self, name: str, email: Optional[str] = None) -> Optional[User]:
        """Create a new user."""
        try:
            result = self.supabase.table("users").insert({
                "name": name,
                "email": email
            }).execute()

            if result.data:
                data = result.data[0]
                return User(
                    id=data["id"],
                    name=data["name"],
                    email=data["email"],
                    created_at=data["created_at"]
                )
        except Exception as e:
            st.error(f"Error creating user: {str(e)}")
        return None

    def get_all_users(self) -> List[User]:
        """Get all users."""
        try:
            result = self.supabase.table("users").select("*").order("name").execute()

            users = []
            for data in result.data:
                users.append(User(
                    id=data["id"],
                    name=data["name"],
                    email=data["email"],
                    created_at=data["created_at"]
                ))
            return users
        except Exception as e:
            st.error(f"Error fetching users: {str(e)}")
            return []

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by ID."""
        try:
            result = self.supabase.table("users").select("*").eq("id", user_id).execute()

            if result.data:
                data = result.data[0]
                return User(
                    id=data["id"],
                    name=data["name"],
                    email=data["email"],
                    created_at=data["created_at"]
                )
        except Exception as e:
            st.error(f"Error fetching user: {str(e)}")
        return None

    def delete_user(self, user_id: int) -> bool:
        """Delete a user and all associated data."""
        try:
            result = self.supabase.table("users").delete().eq("id", user_id).execute()
            return len(result.data) > 0
        except Exception as e:
            st.error(f"Error deleting user: {str(e)}")
            return False

    # Experiment operations
    def create_experiment(self, name: str, description: str, prompt_id: int) -> Optional[Experiment]:
        """Create a new experiment."""
        try:
            result = self.supabase.table("experiments").insert({
                "name": name,
                "description": description,
                "prompt_id": prompt_id
            }).execute()

            if result.data:
                data = result.data[0]
                return Experiment(
                    id=data["id"],
                    name=data["name"],
                    description=data["description"],
                    prompt_id=data["prompt_id"],
                    created_at=data["created_at"]
                )
        except Exception as e:
            st.error(f"Error creating experiment: {str(e)}")
        return None

    def get_all_experiments(self) -> List[Experiment]:
        """Get all experiments."""
        try:
            result = self.supabase.table("experiments").select("*").order("created_at", desc=True).execute()

            experiments = []
            for data in result.data:
                experiments.append(Experiment(
                    id=data["id"],
                    name=data["name"],
                    description=data["description"],
                    prompt_id=data["prompt_id"],
                    created_at=data["created_at"]
                ))
            return experiments
        except Exception as e:
            st.error(f"Error fetching experiments: {str(e)}")
            return []

    def get_experiments_by_prompt(self, prompt_id: int) -> List[Experiment]:
        """Get all experiments for a specific prompt."""
        try:
            result = self.supabase.table("experiments").select("*").eq("prompt_id", prompt_id).order("created_at", desc=True).execute()

            experiments = []
            for data in result.data:
                experiments.append(Experiment(
                    id=data["id"],
                    name=data["name"],
                    description=data["description"],
                    prompt_id=data["prompt_id"],
                    created_at=data["created_at"]
                ))
            return experiments
        except Exception as e:
            st.error(f"Error fetching experiments: {str(e)}")
            return []

    def delete_experiment(self, experiment_id: int) -> bool:
        """Delete an experiment and all associated cases."""
        try:
            result = self.supabase.table("experiments").delete().eq("id", experiment_id).execute()
            return len(result.data) > 0
        except Exception as e:
            st.error(f"Error deleting experiment: {str(e)}")
            return False

    # Experiment Case operations
    def create_experiment_case(self, experiment_id: int, question_id: int, user_id: int, is_selected: bool = True) -> Optional[ExperimentCase]:
        """Create a new experiment case."""
        try:
            result = self.supabase.table("experiment_cases").insert({
                "experiment_id": experiment_id,
                "question_id": question_id,
                "user_id": user_id,
                "is_selected": is_selected
            }).execute()

            if result.data:
                data = result.data[0]
                return ExperimentCase(
                    id=data["id"],
                    experiment_id=data["experiment_id"],
                    question_id=data["question_id"],
                    user_id=data["user_id"],
                    is_selected=data["is_selected"],
                    created_at=data["created_at"]
                )
        except Exception as e:
            st.error(f"Error creating experiment case: {str(e)}")
        return None

    def get_experiment_cases(self, experiment_id: int) -> List[ExperimentCase]:
        """Get all cases for an experiment."""
        try:
            result = self.supabase.table("experiment_cases").select("*").eq("experiment_id", experiment_id).execute()

            cases = []
            for data in result.data:
                cases.append(ExperimentCase(
                    id=data["id"],
                    experiment_id=data["experiment_id"],
                    question_id=data["question_id"],
                    user_id=data["user_id"],
                    is_selected=data["is_selected"],
                    created_at=data["created_at"]
                ))
            return cases
        except Exception as e:
            st.error(f"Error fetching experiment cases: {str(e)}")
            return []

    def update_experiment_case_selection(self, case_id: int, is_selected: bool) -> bool:
        """Update the selection status of an experiment case."""
        try:
            result = self.supabase.table("experiment_cases").update({
                "is_selected": is_selected
            }).eq("id", case_id).execute()

            return len(result.data) > 0
        except Exception as e:
            st.error(f"Error updating experiment case: {str(e)}")
            return False

    def get_selected_experiment_cases_with_data(self, experiment_id: int) -> List[CaseResult]:
        """Get all selected experiment cases with their related data."""
        try:
            # Get selected cases
            cases_result = self.supabase.table("experiment_cases").select("*").eq("experiment_id", experiment_id).eq("is_selected", True).execute()

            case_results = []
            for case_data in cases_result.data:
                case = ExperimentCase(
                    id=case_data["id"],
                    experiment_id=case_data["experiment_id"],
                    question_id=case_data["question_id"],
                    user_id=case_data["user_id"],
                    is_selected=case_data["is_selected"],
                    created_at=case_data["created_at"]
                )

                # Get question
                question_result = self.supabase.table("questions").select("*").eq("id", case.question_id).execute()
                if not question_result.data:
                    continue

                question_data = question_result.data[0]
                question = Question(
                    id=question_data["id"],
                    prompt_id=question_data["prompt_id"],
                    question_text=question_data["question_text"],
                    created_at=question_data["created_at"]
                )

                # Get user
                user = self.get_user_by_id(case.user_id)
                if not user:
                    continue

                # Get answer
                answer = self.get_answer_by_question_and_user(case.question_id, case.user_id)
                if not answer:
                    continue

                # Get follow-up questions
                followups = self.get_followups_by_answer(answer.id)

                case_results.append(CaseResult(
                    case=case,
                    question=question,
                    answer=answer,
                    user=user,
                    followup_questions=followups
                ))

            return case_results
        except Exception as e:
            st.error(f"Error fetching experiment case data: {str(e)}")
            return []
