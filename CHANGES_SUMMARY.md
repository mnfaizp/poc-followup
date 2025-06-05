# Changes Summary: Updated AI Follow-up System

## Overview
The AI service has been updated to meet the new requirements:
- Return only 1 followup question with 1 reason
- Use prompts directly as system instructions
- Support configurable AI model and temperature settings from prompts table
- Group results by user instead of by question

## Key Changes Made

### 1. AI Service Updates (`ai_service.py`)

#### Method Signature Changes
- `generate_followup_questions()` now returns `Dict[str, str]` instead of `List[str]`
- Added optional `model` and `temperature` parameters
- Removed `num_questions` parameter (always generates 1 question)

#### System Instruction Changes
- Prompts are now used directly as system instructions without wrapper text
- Removed the hardcoded "You are an expert interviewer..." wrapper
- The `prompt_context` parameter is passed directly to `system_instruction`

#### Response Format Changes
- AI now returns structured JSON with `question` and `reason` fields
- Added robust JSON parsing with fallback handling
- Ensures questions end with question marks

#### Configuration Support
- Added `default_model` and `default_temperature` to constructor
- Support for per-request model and temperature overrides
- Uses Gemini's `GenerationConfig` for temperature control

### 2. Database Schema Updates

#### New Columns
- Added `reason TEXT` column to `followup_questions` table
- Added `model VARCHAR(100)` column to `prompts` table (default: 'gemini-2.0-flash')
- Added `temperature DECIMAL(3,2)` column to `prompts` table (default: 0.7)
- Updated `database_schema.sql` for new installations
- Created `database_migration.sql` for existing databases

#### Model Updates (`models.py`)
- Added `reason: Optional[str] = None` field to `FollowupQuestion` class
- Added `model: str = "gemini-2.0-flash"` field to `Prompt` class
- Added `temperature: float = 0.7` field to `Prompt` class

#### Database Operations (`database.py`)
- Updated `create_followup_question()` to accept optional `reason` parameter
- Updated `get_followups_by_answer()` to return reason field
- Updated `create_prompt()` to accept `model` and `temperature` parameters
- Updated `update_prompt()` to accept `model` and `temperature` parameters
- Updated `get_all_prompts()` to return model and temperature fields
- All database operations now handle the new fields properly

### 3. Application Updates (`app.py`)

#### Experiment Execution
- Updated experiment runner to handle new AI service response format
- Now extracts `question` and `reason` from AI response dictionary
- Passes reason to database when creating followup questions
- Uses model and temperature settings from the selected prompt

#### Results Display
- **Changed grouping from questions to users**: Results are now organized by user instead of by question
- Updated results page to show both questions and reasons
- Changed "Questions" to "Question" (singular) in UI
- Added reason display with "💡 Reason:" label
- Shows AI model and temperature settings used for the prompt

#### Prompt Management UI
- Added model selection dropdown (gemini-2.0-flash, gemini-1.5-flash, gemini-1.5-pro)
- Added temperature slider (0.0 to 1.0) with help text
- Updated prompt display to show current AI settings
- Updated edit form to allow changing model and temperature
- Shows AI settings in experiments and results pages

### 4. Documentation Updates

#### README.md
- Updated feature descriptions to reflect new capabilities
- Added information about single question + reason format
- Documented direct prompt usage and configurable AI settings

#### Migration Support
- Created `database_migration.sql` for existing users
- Added `test_updated_features.py` to verify all changes work correctly

## Technical Details

### AI Response Format
```json
{
    "question": "Your follow-up question here?",
    "reason": "Explanation of why this follow-up question is needed"
}
```

### Database Schema Additions
```sql
-- Add reason column to followup_questions table
ALTER TABLE followup_questions
ADD COLUMN IF NOT EXISTS reason TEXT;

-- Add model and temperature columns to prompts table
ALTER TABLE prompts
ADD COLUMN IF NOT EXISTS model VARCHAR(100) DEFAULT 'gemini-2.0-flash';

ALTER TABLE prompts
ADD COLUMN IF NOT EXISTS temperature DECIMAL(3,2) DEFAULT 0.7;
```

### New AI Service Usage
```python
# Old usage
followups = ai.generate_followup_questions(prompt, question, answer)
for followup_text in followups:
    db.create_followup_question(answer_id, followup_text)

# New usage with prompt-specific settings
followup_data = ai.generate_followup_questions(
    prompt_context=prompt.content,
    question=question,
    answer=answer,
    model=prompt.model,
    temperature=prompt.temperature
)
if followup_data and 'question' in followup_data:
    db.create_followup_question(
        answer_id,
        followup_data['question'],
        followup_data.get('reason')
    )
```

### New Prompt Creation
```python
# Create prompt with AI settings
prompt = db.create_prompt(
    title="Interview Assistant",
    content="You are an expert interviewer...",
    model="gemini-1.5-flash",
    temperature=0.8
)
```

## Migration Steps for Existing Users

1. **Update Database Schema**:
   ```sql
   -- Run this in your Supabase SQL editor
   ALTER TABLE followup_questions
   ADD COLUMN IF NOT EXISTS reason TEXT;

   ALTER TABLE prompts
   ADD COLUMN IF NOT EXISTS model VARCHAR(100) DEFAULT 'gemini-2.0-flash';

   ALTER TABLE prompts
   ADD COLUMN IF NOT EXISTS temperature DECIMAL(3,2) DEFAULT 0.7;
   ```

2. **Update Code**: The application code has been updated automatically

3. **Test**: Run `python test_new_changes.py` to verify everything works

## Benefits of Changes

1. **Focused Output**: Each answer now generates exactly 1 targeted follow-up question
2. **Transparency**: Users can see why each follow-up question was generated
3. **Direct Control**: Prompts work exactly as written without AI wrapper text
4. **Flexible AI Configuration**: Model and temperature can be configured per prompt
5. **Better Organization**: Results grouped by user for easier analysis
6. **Improved UX**: Clear display of AI settings and user-centric result view
7. **Prompt-Specific Settings**: Each prompt can use different AI models and creativity levels

## Backward Compatibility

- Existing data remains intact
- New `reason` field is optional and defaults to `NULL`
- New `model` and `temperature` fields have sensible defaults
- Old followup questions without reasons will display "Not provided"
- Existing prompts will automatically get default AI settings
- All existing functionality continues to work

## Testing

Run the test suite to verify all changes:
```bash
python test_new_changes.py
```

All tests should pass, confirming:
- ✅ Models updated correctly with new fields
- ✅ AI service method signatures are correct
- ✅ Database operations handle new fields
- ✅ All files compile successfully
- ✅ Prompt configuration works
- ✅ User-grouped results functionality
