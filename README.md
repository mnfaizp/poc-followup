# Multi-User Follow-up Questions Manager

A Streamlit application for managing follow-up questions with multi-user support, experiments, and AI-powered question generation using Google Gemini API and Supabase backend.

## Features

### Core Features
- **Prompt Management**: Create, edit, and store reusable prompts that serve as system instructions for AI
- **Question Management**: Add and organize questions associated with prompts
- **Multi-User Support**: Manage multiple users who can provide answers to the same questions
- **Case Management**: Collect answers from different users for the same questions
- **Experiment System**: Create experiments to test different combinations of prompts, questions, and user responses
- **AI-Powered Follow-ups**: Generate intelligent follow-up questions using Google Gemini with:
  - **Single Question + Reason**: Each answer generates exactly 1 follow-up question with an explanation of why it's needed
  - **Direct Prompt Usage**: Prompts are used directly as AI system instructions without additional wrapper text
  - **Configurable AI Settings**: Support for different AI models and temperature settings
- **Results Analysis**: View and analyze experiment results with comprehensive statistics

### New Multi-User Flow
1. **Prompt Creation**: Create prompts that will be used as system instructions for AI
2. **Question Creation**: Add questions to prompts
3. **User Management**: Create and manage multiple users (supports quick setup with 5 default users)
4. **Case Collection**: Collect answers from multiple users for each question
5. **Experiment Configuration**: Create experiments and select which user-question combinations to include
6. **Experiment Execution**: Run experiments to generate follow-up questions for selected cases
7. **Results Viewing**: Analyze results showing all user responses and their AI-generated follow-ups

## Prerequisites

- Python 3.8+
- Supabase account and project
- Google AI Studio account (for Gemini API key)

## Installation

1. **Clone or download the project files**

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   - Copy `.env.example` to `.env`
   - Fill in your credentials:
     ```
     SUPABASE_URL=your_supabase_project_url
     SUPABASE_KEY=your_supabase_anon_key
     GEMINI_API_KEY=your_gemini_api_key
     AUTH_USERNAME=admin
     AUTH_PASSWORD=your_secure_password
     ```

## Database Setup

1. **Create a Supabase project** at [supabase.com](https://supabase.com)

2. **Run the database schema**:
   - Go to your Supabase dashboard
   - Navigate to SQL Editor
   - Copy and paste the contents of `database_schema.sql`
   - Execute the SQL to create the required tables

3. **Get your credentials**:
   - **Supabase URL**: Found in Project Settings > API
   - **Supabase Anon Key**: Found in Project Settings > API
   - **Gemini API Key**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Authentication

The application includes secure authentication to protect access:

1. **Set up authentication credentials** in your `.env` file:
   ```
   AUTH_USERNAME=admin
   AUTH_PASSWORD=your_secure_password
   ```

2. **Login required**: Users must authenticate before accessing any features
3. **Session management**: Authentication persists during the session
4. **Logout option**: Available in the sidebar when logged in

## Usage

1. **Start the application**:
   ```bash
   streamlit run app.py
   ```

2. **Login**: Enter your username and password on the login screen

3. **Navigate through the application using sidebar buttons**:
   - **📝 Manage Prompts**: Create and edit reusable prompts that serve as AI system instructions
   - **❓ Manage Questions**: Add questions to prompts (no answers here)
   - **👥 Manage Users**: Create and manage users who will provide answers
   - **💬 Manage Cases**: Collect answers from different users for each question
   - **🧪 Experiments**: Create experiments, select cases, and run AI follow-up generation
   - **📊 Results**: View experiment results with all user responses and follow-ups

## Application Flow

### Quick Start
1. **Create a Prompt**: Start by creating a prompt that will guide the AI's behavior
2. **Add Questions**: Add specific questions related to your prompt
3. **Set Up Users**: Use "Create 5 Default Users" button or add custom users
4. **Collect Answers**: Go to "Manage Cases" and collect answers from each user for each question
5. **Create Experiment**: Set up an experiment and select which user-question combinations to include
6. **Run Experiment**: Execute the experiment to generate AI follow-up questions
7. **View Results**: Analyze the results showing all responses and generated follow-ups

### Detailed Workflow
1. **Prompt Creation**: Create prompts that provide context and instructions for the AI
2. **Question Management**: Add questions that will be answered by multiple users
3. **User Setup**: Create users who will provide different perspectives on the same questions
4. **Case Collection**: Gather answers from each user for each question (creating cases)
5. **Experiment Design**: Create experiments to test specific combinations of prompts, questions, and users
6. **AI Generation**: Run experiments to generate follow-up questions using the prompt as system instruction
7. **Analysis**: Review results to see how different users' answers lead to different follow-up questions

## File Structure

```
├── app.py                 # Main Streamlit application with multi-user interface
├── auth.py               # Authentication module for secure access
├── database.py           # Supabase database operations with new multi-user methods
├── ai_service.py         # Google Gemini AI integration with system instructions
├── models.py             # Data models including User, Experiment, ExperimentCase
├── requirements.txt      # Python dependencies
├── database_schema.sql   # Database setup SQL with new tables
├── test_new_features.py  # Test script for new functionality
├── .env.example         # Environment variables template
└── README.md            # This file
```

## Database Schema

The application uses the following main tables:
- **prompts**: Store reusable prompts that serve as AI system instructions
- **questions**: Questions associated with prompts
- **users**: Multiple users who can provide answers
- **answers**: User answers to questions (includes user_id)
- **followup_questions**: AI-generated follow-up questions with reasons
- **experiments**: Experiment configurations
- **experiment_cases**: Links experiments with specific question-user combinations

## Troubleshooting

### Common Issues

1. **Authentication errors**:
   - Ensure AUTH_USERNAME and AUTH_PASSWORD are set in your `.env` file
   - Check that credentials match exactly (case-sensitive)
   - Restart the application after changing authentication settings

2. **"GEMINI_API_KEY not found"**:
   - Ensure your `.env` file exists and contains the correct API key
   - Restart the Streamlit application after adding environment variables

3. **Database connection errors**:
   - Verify your Supabase URL and key are correct
   - Ensure the database schema has been properly set up

4. **AI generation fails**:
   - Check your Gemini API key is valid and has quota remaining
   - Ensure you have internet connectivity

### Getting API Keys

- **Google Gemini API**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Supabase**: Create a project at [supabase.com](https://supabase.com)

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the application.

## License

This project is open source and available under the MIT License.
