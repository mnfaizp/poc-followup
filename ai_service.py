"""
AI service for generating follow-up questions using Google Gemini API.
"""
import os
import google.generativeai as genai
from typing import List, Optional, Dict, Any
import streamlit as st
import json


class AIService:
    """Handles AI operations using Google Gemini API."""

    def __init__(self, default_model: str = 'gemini-2.0-flash', default_temperature: float = 0.7):
        """Initialize Gemini AI client."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            st.error("GEMINI_API_KEY not found in environment variables")
            return

        genai.configure(api_key=api_key)
        self.default_model = default_model
        self.default_temperature = default_temperature
    
    def generate_followup_questions(self, prompt_context: str, question: str, answer: str,
                                  model: Optional[str] = None, temperature: Optional[float] = None) -> Dict[str, str]:
        """
        Generate a single follow-up question with reason based on the prompt context, original question, and user's answer.

        Args:
            prompt_context: The original prompt/context (used as system instruction)
            question: The original question
            answer: The user's answer
            model: AI model to use (defaults to default_model)
            temperature: Temperature for generation (defaults to default_temperature)

        Returns:
            Dictionary with 'question' and 'reason' keys, or empty dict if generation fails
        """
        try:
            # Use prompt_context directly as system instruction
            system_instruction = prompt_context

            # Use provided model and temperature or defaults
            model_name = model or self.default_model
            temp = temperature or self.default_temperature

            # Create model with system instruction and generation config
            generation_config = genai.types.GenerationConfig(
                temperature=temp,
                max_output_tokens=1000,
            )

            model_with_system = genai.GenerativeModel(
                model_name,
                system_instruction=system_instruction,
                generation_config=generation_config
            )

            # Construct the content prompt
            content_prompt = f"""
                Original Question: {question}

                User's Answer: {answer}

                Please generate exactly 1 thoughtful follow-up question based on the user's answer above, along with a clear reason explaining why this follow-up question is needed.

                Format your response as a JSON object with exactly these two fields:
                {{
                    "question": "Your follow-up question here?",
                    "reason": "Explanation of why this follow-up question is needed"
                }}

                Make sure the question ends with a question mark and the reason is a clear, concise explanation. Even no question is generated, please provide a reason.
            """

            response = model_with_system.generate_content(content_prompt)

            if response.text:
                # Parse the JSON response
                return self._parse_structured_response(response.text)
            else:
                st.warning("No response generated from AI service")
                return {}

        except Exception as e:
            st.error(f"Error generating follow-up questions: {str(e)}")
            return {}
    
    def _parse_structured_response(self, response_text: str) -> Dict[str, str]:
        """
        Parse the AI response to extract question and reason from JSON format.

        Args:
            response_text: Raw response from Gemini (should be JSON)

        Returns:
            Dictionary with 'question' and 'reason' keys, or empty dict if parsing fails
        """
        try:
            # Clean up the response text - remove any markdown formatting
            cleaned_text = response_text.strip()
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]
            cleaned_text = cleaned_text.strip()

            # Parse JSON
            parsed = json.loads(cleaned_text)

            # Validate required fields
            if isinstance(parsed, dict) and 'question' in parsed and 'reason' in parsed:
                question = parsed['question'].strip()
                reason = parsed['reason'].strip()

                # Ensure question ends with question mark
                if question and not question.endswith('?'):
                    question += '?'

                return {
                    'question': question,
                    'reason': reason
                }
            else:
                st.warning("AI response missing required fields (question, reason)")
                return {}

        except json.JSONDecodeError as e:
            st.warning(f"Failed to parse AI response as JSON: {str(e)}")
            # Fallback: try to extract question and reason from text
            return self._fallback_parse_response(response_text)
        except Exception as e:
            st.warning(f"Error parsing AI response: {str(e)}")
            return {}

    def _fallback_parse_response(self, response_text: str) -> Dict[str, str]:
        """
        Fallback parser for when JSON parsing fails.

        Args:
            response_text: Raw response text

        Returns:
            Dictionary with 'question' and 'reason' keys, or empty dict
        """
        try:
            lines = response_text.strip().split('\n')
            question = ""
            reason = ""

            for line in lines:
                line = line.strip()
                if line.endswith('?'):
                    question = line
                elif line and not line.startswith('{') and not line.startswith('}'):
                    if not reason:
                        reason = line

            if question and reason:
                return {'question': question, 'reason': reason}
            else:
                return {}

        except Exception:
            return {}
    
    def generate_batch_followups(self, question_answer_pairs: List[dict], prompt_context: str,
                               model: Optional[str] = None, temperature: Optional[float] = None) -> dict:
        """
        Generate follow-up questions for multiple question-answer pairs.

        Args:
            question_answer_pairs: List of dicts with 'question_id', 'question_text', 'answer_text'
            prompt_context: The original prompt context
            model: AI model to use (defaults to default_model)
            temperature: Temperature for generation (defaults to default_temperature)

        Returns:
            Dictionary mapping question_id to dict with 'question' and 'reason'
        """
        results = {}

        for pair in question_answer_pairs:
            if pair.get('answer_text') and pair['answer_text'].strip():
                followup_data = self.generate_followup_questions(
                    prompt_context=prompt_context,
                    question=pair['question_text'],
                    answer=pair['answer_text'],
                    model=model,
                    temperature=temperature
                )
                results[pair['question_id']] = followup_data
            else:
                results[pair['question_id']] = {}

        return results
