"""
Streamlit application for managing follow-up questions with multi-user experiments.
"""
import streamlit as st
import os
from dotenv import load_dotenv
from database import DatabaseManager
from ai_service import AIService
from models import Prompt, Question, Answer, User, Experiment, ExperimentCase, CaseResult

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Follow-up Questions Manager",
    page_icon="❓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize services
@st.cache_resource
def init_services():
    """Initialize database and AI services."""
    try:
        db = DatabaseManager()
        ai = AIService()
        return db, ai
    except Exception as e:
        st.error(f"Service initialization error: {str(e)}")
        raise e

def create_default_users(db: DatabaseManager):
    """Create 5 default users for testing."""
    default_users = [
        ("Alice Johnson", "alice@example.com"),
        ("Bob Smith", "bob@example.com"),
        ("Carol Davis", "carol@example.com"),
        ("David Wilson", "david@example.com"),
        ("Eva Brown", "eva@example.com")
    ]

    created_count = 0
    for name, email in default_users:
        # Check if user already exists
        existing_users = db.get_all_users()
        if not any(user.name == name for user in existing_users):
            user = db.create_user(name, email)
            if user:
                created_count += 1

    if created_count > 0:
        st.success(f"Created {created_count} default users!")
        st.rerun()
    else:
        st.info("All default users already exist.")

def main():
    """Main application function."""
    st.title("❓ Multi-User Follow-up Questions Manager")
    st.markdown("Create prompts, manage users, collect answers, and run experiments with AI-powered follow-up questions.")

    # Initialize services
    try:
        db, ai = init_services()
    except Exception as e:
        st.error(f"Failed to initialize services: {str(e)}")
        st.info("Please check your environment variables and database connection.")
        return

    # Sidebar for navigation with buttons instead of dropdown
    st.sidebar.title("🧭 Navigation")
    st.sidebar.markdown("---")

    # Initialize session state for page navigation
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Manage Prompts"

    # Navigation buttons
    if st.sidebar.button("📝 Manage Prompts", use_container_width=True):
        st.session_state.current_page = "Manage Prompts"

    if st.sidebar.button("❓ Manage Questions", use_container_width=True):
        st.session_state.current_page = "Manage Questions"

    if st.sidebar.button("👥 Manage Users", use_container_width=True):
        st.session_state.current_page = "Manage Users"

    if st.sidebar.button("💬 Manage Cases", use_container_width=True):
        st.session_state.current_page = "Manage Cases"

    if st.sidebar.button("🧪 Experiments", use_container_width=True):
        st.session_state.current_page = "Experiments"

    if st.sidebar.button("📊 Results", use_container_width=True):
        st.session_state.current_page = "Results"

    st.sidebar.markdown("---")

    # Route to appropriate page
    if st.session_state.current_page == "Manage Prompts":
        manage_prompts_page(db)
    elif st.session_state.current_page == "Manage Questions":
        manage_questions_page(db)
    elif st.session_state.current_page == "Manage Users":
        manage_users_page(db)
    elif st.session_state.current_page == "Manage Cases":
        manage_cases_page(db)
    elif st.session_state.current_page == "Experiments":
        experiments_page(db, ai)
    elif st.session_state.current_page == "Results":
        results_page(db)

def manage_prompts_page(db: DatabaseManager):
    """Page for managing prompts."""
    st.header("📝 Manage Prompts")
    
    # Create new prompt section
    st.subheader("Create New Prompt")
    with st.form("create_prompt_form"):
        title = st.text_input("Prompt Title", placeholder="Enter a descriptive title for your prompt")
        content = st.text_area("Prompt Content", placeholder="Enter the main prompt or context", height=150)

        # AI Configuration
        st.write("**AI Configuration:**")
        col1, col2 = st.columns(2)
        with col1:
            model = st.selectbox(
                "AI Model",
                options=["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
                index=0,
                help="Select the AI model to use for this prompt"
            )
        with col2:
            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                step=0.1,
                help="Controls randomness: 0.0 = deterministic, 1.0 = very creative"
            )

        if st.form_submit_button("Create Prompt"):
            if title and content:
                prompt = db.create_prompt(title, content, model, temperature)
                if prompt:
                    st.success(f"Prompt '{title}' created successfully!")
                    st.rerun()
            else:
                st.error("Please fill in both title and content.")
    
    st.divider()
    
    # Display existing prompts
    st.subheader("Existing Prompts")
    prompts = db.get_all_prompts()
    
    if not prompts:
        st.info("No prompts found. Create your first prompt above!")
        return
    
    for prompt in prompts:
        with st.expander(f"📄 {prompt.title}", expanded=False):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.write("**Content:**")
                st.write(prompt.content)
                st.write(f"**AI Model:** {prompt.model}")
                st.write(f"**Temperature:** {prompt.temperature}")
                st.caption(f"Created: {prompt.created_at}")

            with col2:
                if st.button(f"Edit", key=f"edit_{prompt.id}"):
                    st.session_state[f"editing_{prompt.id}"] = True

                if st.button(f"Delete", key=f"delete_{prompt.id}", type="secondary"):
                    if db.delete_prompt(prompt.id):
                        st.success("Prompt deleted successfully!")
                        st.rerun()
            
            # Edit form (shown when edit button is clicked)
            if st.session_state.get(f"editing_{prompt.id}", False):
                with st.form(f"edit_prompt_form_{prompt.id}"):
                    new_title = st.text_input("Title", value=prompt.title)
                    new_content = st.text_area("Content", value=prompt.content, height=100)

                    # AI Configuration for editing
                    st.write("**AI Configuration:**")
                    col1, col2 = st.columns(2)
                    with col1:
                        # add gemini-2.5-flash-preview-04-17, gemini-2.5-flash-preview-04-17, gemini-2.5-flash-preview-05-20
                        options = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.5-flash-preview-04-17", "gemini-2.5-flash-preview-04-17", "gemini-2.5-flash-preview-05-20"]
                        new_model = st.selectbox(
                            "AI Model",
                            options=options,
                            index=options.index(prompt.model) if prompt.model in options else 0,
                            help="Select the AI model to use for this prompt"
                        )
                    with col2:
                        new_temperature = st.slider(
                            "Temperature",
                            min_value=0.0,
                            max_value=1.0,
                            value=float(prompt.temperature),
                            step=0.1,
                            help="Controls randomness: 0.0 = deterministic, 1.0 = very creative"
                        )

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Save Changes"):
                            if db.update_prompt(prompt.id, new_title, new_content, new_model, new_temperature):
                                st.success("Prompt updated successfully!")
                                st.session_state[f"editing_{prompt.id}"] = False
                                st.rerun()

                    with col2:
                        if st.form_submit_button("Cancel"):
                            st.session_state[f"editing_{prompt.id}"] = False
                            st.rerun()

def manage_questions_page(db: DatabaseManager):
    """Page for managing questions (without answers)."""
    st.header("❓ Manage Questions")

    # Select prompt
    prompts = db.get_all_prompts()
    if not prompts:
        st.warning("No prompts found. Please create a prompt first.")
        return

    prompt_options = {f"{p.title}": p for p in prompts}
    selected_prompt_title = st.selectbox("Select a Prompt:", list(prompt_options.keys()))
    selected_prompt = prompt_options[selected_prompt_title]

    st.info(f"**Selected Prompt:** {selected_prompt.content}")

    # Add new question
    st.subheader("Add New Question")
    with st.form("add_question_form"):
        question_text = st.text_area("Question Text", placeholder="Enter your question here", height=100)

        if st.form_submit_button("Add Question"):
            if question_text:
                question = db.create_question(selected_prompt.id, question_text)
                if question:
                    st.success("Question added successfully!")
                    st.rerun()
            else:
                st.error("Please enter a question.")

    st.divider()

    # Display existing questions
    st.subheader("Existing Questions")
    questions = db.get_questions_by_prompt(selected_prompt.id)

    if not questions:
        st.info("No questions found for this prompt. Add some questions above!")
        return

    for i, question in enumerate(questions):
        with st.expander(f"Question {i+1}: {question.question_text[:50]}...", expanded=False):
            st.write(f"**Question:** {question.question_text}")
            st.caption(f"Created: {question.created_at}")

            # Show how many users have answered this question
            answers = db.get_answers_by_question(question.id)
            st.info(f"📊 {len(answers)} user(s) have answered this question")

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button(f"Edit Question", key=f"edit_q_{question.id}"):
                    st.session_state[f"editing_q_{question.id}"] = True

            with col2:
                if st.button(f"Delete Question", key=f"del_q_{question.id}", type="secondary"):
                    if db.delete_question(question.id):
                        st.success("Question deleted!")
                        st.rerun()

            # Edit form (shown when edit button is clicked)
            if st.session_state.get(f"editing_q_{question.id}", False):
                with st.form(f"edit_question_form_{question.id}"):
                    new_question_text = st.text_area("Question Text", value=question.question_text, height=100)

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Save Changes"):
                            # Note: We would need to add an update_question method to DatabaseManager
                            st.info("Question editing not yet implemented")
                            st.session_state[f"editing_q_{question.id}"] = False

                    with col2:
                        if st.form_submit_button("Cancel"):
                            st.session_state[f"editing_q_{question.id}"] = False
                            st.rerun()

def manage_users_page(db: DatabaseManager):
    """Page for managing users."""
    st.header("👥 Manage Users")

    # Quick setup section
    st.subheader("Quick Setup")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Create 5 Default Users", type="primary"):
            create_default_users(db)

    with col2:
        if st.button("🗑️ Clear All Users", type="secondary"):
            users = db.get_all_users()
            for user in users:
                db.delete_user(user.id)
            st.success("All users cleared!")
            st.rerun()

    st.divider()

    # Create new user section
    st.subheader("Add New User")
    with st.form("create_user_form"):
        name = st.text_input("User Name", placeholder="Enter user's name")
        email = st.text_input("Email (optional)", placeholder="Enter user's email")

        if st.form_submit_button("Add User"):
            if name:
                user = db.create_user(name, email if email else None)
                if user:
                    st.success(f"User '{name}' added successfully!")
                    st.rerun()
            else:
                st.error("Please enter a user name.")

    st.divider()

    # Display existing users
    st.subheader("Existing Users")
    users = db.get_all_users()

    if not users:
        st.info("No users found. Add some users above!")
        return

    for user in users:
        with st.expander(f"👤 {user.name}", expanded=False):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.write(f"**Name:** {user.name}")
                if user.email:
                    st.write(f"**Email:** {user.email}")
                st.caption(f"Created: {user.created_at}")

                # Show user's answer count
                # We'll need to add a method to count answers by user
                st.info("📊 Answer statistics will be shown here")

            with col2:
                if st.button(f"Delete", key=f"delete_user_{user.id}", type="secondary"):
                    if db.delete_user(user.id):
                        st.success("User deleted successfully!")
                        st.rerun()

def manage_cases_page(db: DatabaseManager):
    """Page for managing question-answer cases from multiple users."""
    st.header("💬 Manage Cases (Question-Answer Pairs)")

    # Select prompt
    prompts = db.get_all_prompts()
    if not prompts:
        st.warning("No prompts found. Please create a prompt first.")
        return

    prompt_options = {f"{p.title}": p for p in prompts}
    selected_prompt_title = st.selectbox("Select a Prompt:", list(prompt_options.keys()))
    selected_prompt = prompt_options[selected_prompt_title]

    st.info(f"**Selected Prompt:** {selected_prompt.content}")

    # Get questions for the prompt
    questions = db.get_questions_by_prompt(selected_prompt.id)
    if not questions:
        st.warning("No questions found for this prompt. Please add some questions first.")
        return

    # Get users
    users = db.get_all_users()
    if not users:
        st.warning("No users found. Please add some users first.")
        return

    st.subheader("Answer Questions by User")

    # Use selectbox instead of tabs to avoid the JavaScript error
    selected_user_name = st.selectbox(
        "Select User to Answer Questions:",
        options=[user.name for user in users],
        key="selected_user_for_answers"
    )

    # Find the selected user
    selected_user = next(user for user in users if user.name == selected_user_name)

    st.info(f"**Answering as:** {selected_user.name}")

    # Display questions for the selected user
    for j, question in enumerate(questions):
        with st.expander(f"Question {j+1}: {question.question_text[:50]}...", expanded=True):
            st.write(f"**Question:** {question.question_text}")

            # Get existing answer for this user and question
            existing_answer = db.get_answer_by_question_and_user(question.id, selected_user.id)
            answer_text = existing_answer.answer_text if existing_answer else ""

            # Answer input
            new_answer = st.text_area(
                f"Answer from {selected_user.name}:",
                value=answer_text,
                key=f"answer_{question.id}_{selected_user.id}",
                height=100,
                placeholder="Enter answer here..."
            )

            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button(f"Save Answer", key=f"save_{question.id}_{selected_user.id}"):
                    if new_answer.strip():
                        answer = db.create_or_update_answer(question.id, selected_user.id, new_answer)
                        if answer:
                            st.success("Answer saved!")
                            st.rerun()
                    else:
                        st.error("Please enter an answer.")

            with col2:
                # Show answer status for all users for this question
                st.write("**Answer Status for All Users:**")
                for user in users:
                    user_answer = db.get_answer_by_question_and_user(question.id, user.id)
                    status = "✅ Answered" if user_answer and user_answer.answer_text.strip() else "❌ Not answered"
                    st.caption(f"{user.name}: {status}")

def experiments_page(db: DatabaseManager, ai: AIService):
    """Page for creating and running experiments."""
    st.header("🧪 Experiments")

    # Select prompt
    prompts = db.get_all_prompts()
    if not prompts:
        st.warning("No prompts found. Please create a prompt first.")
        return

    prompt_options = {f"{p.title}": p for p in prompts}
    selected_prompt_title = st.selectbox("Select a Prompt:", list(prompt_options.keys()))
    selected_prompt = prompt_options[selected_prompt_title]

    st.info(f"**Selected Prompt:** {selected_prompt.content}")
    st.info(f"**AI Settings:** Model: {selected_prompt.model}, Temperature: {selected_prompt.temperature}")

    # Create new experiment section
    st.subheader("Create New Experiment")
    with st.form("create_experiment_form"):
        exp_name = st.text_input("Experiment Name", placeholder="Enter experiment name")
        exp_description = st.text_area("Description", placeholder="Describe this experiment", height=100)

        if st.form_submit_button("Create Experiment"):
            if exp_name:
                experiment = db.create_experiment(exp_name, exp_description, selected_prompt.id)
                if experiment:
                    st.success(f"Experiment '{exp_name}' created successfully!")
                    st.rerun()
            else:
                st.error("Please enter an experiment name.")

    st.divider()

    # Display existing experiments for this prompt
    st.subheader("Existing Experiments")
    experiments = db.get_experiments_by_prompt(selected_prompt.id)

    if not experiments:
        st.info("No experiments found for this prompt. Create one above!")
        return

    for experiment in experiments:
        with st.expander(f"🧪 {experiment.name}", expanded=False):
            st.write(f"**Description:** {experiment.description}")
            st.caption(f"Created: {experiment.created_at}")

            # Get questions and users for case selection
            questions = db.get_questions_by_prompt(selected_prompt.id)
            users = db.get_all_users()

            if not questions:
                st.warning("No questions found for this prompt.")
                continue

            if not users:
                st.warning("No users found. Please add users first.")
                continue

            # Show case selection interface
            st.write("**Select Cases to Include in Experiment:**")

            # Get existing cases for this experiment
            existing_cases = db.get_experiment_cases(experiment.id)
            existing_case_keys = {(case.question_id, case.user_id): case for case in existing_cases}

            # Create a grid for case selection
            for i, question in enumerate(questions):
                st.write(f"**Question {i+1}:** {question.question_text[:100]}...")

                cols = st.columns(len(users))
                for j, user in enumerate(users):
                    with cols[j]:
                        case_key = (question.id, user.id)
                        existing_case = existing_case_keys.get(case_key)

                        # Check if user has answered this question
                        answer = db.get_answer_by_question_and_user(question.id, user.id)
                        has_answer = answer and answer.answer_text.strip()

                        if has_answer:
                            # Checkbox for case selection
                            is_selected = existing_case.is_selected if existing_case else True
                            selected = st.checkbox(
                                f"{user.name}",
                                value=is_selected,
                                key=f"case_{experiment.id}_{question.id}_{user.id}",
                                help=f"Include {user.name}'s answer to this question"
                            )

                            # Create or update case if selection changed
                            if existing_case:
                                if selected != existing_case.is_selected:
                                    db.update_experiment_case_selection(existing_case.id, selected)
                            else:
                                if selected:
                                    db.create_experiment_case(experiment.id, question.id, user.id, selected)
                        else:
                            st.write(f"❌ {user.name}")
                            st.caption("No answer")

            st.divider()

            # Run experiment button
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button(f"🚀 Run Experiment", key=f"run_{experiment.id}", type="primary"):
                    run_experiment(db, ai, experiment, selected_prompt)

            with col2:
                if st.button(f"🗑️ Delete Experiment", key=f"del_exp_{experiment.id}", type="secondary"):
                    if db.delete_experiment(experiment.id):
                        st.success("Experiment deleted!")
                        st.rerun()

def run_experiment(db: DatabaseManager, ai: AIService, experiment: Experiment, prompt: Prompt):
    """Run an experiment to generate follow-up questions for selected cases."""
    st.write(f"🚀 Running experiment: **{experiment.name}**")

    # Get selected cases with their data
    case_results = db.get_selected_experiment_cases_with_data(experiment.id)

    if not case_results:
        st.warning("No selected cases found for this experiment.")
        return

    progress_bar = st.progress(0)
    status_text = st.empty()

    total_cases = len(case_results)

    for i, case_result in enumerate(case_results):
        status_text.text(f"Generating follow-ups for case {i+1} of {total_cases}...")

        # Clear existing follow-ups for this answer
        db.clear_followups_by_answer(case_result.answer.id)

        # Generate new follow-up using the prompt as system instruction with its model and temperature settings
        followup_data = ai.generate_followup_questions(
            prompt_context=prompt.content,
            question=case_result.question.question_text,
            answer=case_result.answer.answer_text,
            model=prompt.model,
            temperature=prompt.temperature
        )

        # Save follow-up to database if generation was successful
        if followup_data and 'question' in followup_data:
            db.create_followup_question(
                case_result.answer.id,
                followup_data['question'],
                followup_data.get('reason')
            )

        progress_bar.progress((i + 1) / total_cases)

    status_text.text("✅ Experiment completed!")
    st.success(f"Generated follow-up questions for {total_cases} selected cases!")

    # Auto-refresh to show results
    st.rerun()

def results_page(db: DatabaseManager):
    """Page for viewing experiment results and follow-up questions."""
    st.header("📊 Results")

    # Select prompt
    prompts = db.get_all_prompts()
    if not prompts:
        st.warning("No prompts found. Please create a prompt first.")
        return

    prompt_options = {f"{p.title}": p for p in prompts}
    selected_prompt_title = st.selectbox("Select a Prompt:", list(prompt_options.keys()))
    selected_prompt = prompt_options[selected_prompt_title]

    st.info(f"**Selected Prompt:** {selected_prompt.content}")
    st.info(f"**AI Settings:** Model: {selected_prompt.model}, Temperature: {selected_prompt.temperature}")

    # Select experiment
    experiments = db.get_experiments_by_prompt(selected_prompt.id)
    if not experiments:
        st.warning("No experiments found for this prompt. Please create an experiment first.")
        return

    exp_options = {f"{exp.name}": exp for exp in experiments}
    selected_exp_name = st.selectbox("Select an Experiment:", list(exp_options.keys()))
    selected_experiment = exp_options[selected_exp_name]

    st.info(f"**Selected Experiment:** {selected_experiment.description}")

    # Get experiment results
    case_results = db.get_selected_experiment_cases_with_data(selected_experiment.id)

    if not case_results:
        st.warning("No results found for this experiment. Please run the experiment first.")
        return

    st.subheader("Experiment Results")

    # Group results by user
    results_by_user = {}
    for case_result in case_results:
        user_id = case_result.user.id
        if user_id not in results_by_user:
            results_by_user[user_id] = {
                'user': case_result.user,
                'cases': []
            }
        results_by_user[user_id]['cases'].append(case_result)

    # Display results grouped by user
    for i, (user_id, user_data) in enumerate(results_by_user.items()):
        st.markdown(f"### 👤 {user_data['user'].name}")

        # Show all questions answered by this user
        for case_result in user_data['cases']:
            with st.expander(f"❓ {case_result.question.question_text}", expanded=True):
                st.markdown(f"**💬 Answer:** {case_result.answer.answer_text}")

                if case_result.followup_questions:
                    st.markdown("**🤖 AI-Generated Follow-up Question:**")
                    for j, followup in enumerate(case_result.followup_questions, 1):
                        st.markdown(f"**❓ Question:** {followup.followup_text}")
                        if followup.reason:
                            st.markdown(f"**💡 Reason:** {followup.reason}")
                        else:
                            st.markdown("**💡 Reason:** Not provided")
                else:
                    st.info("No follow-up questions generated yet.")

        st.divider()

    # Summary statistics
    st.subheader("📈 Summary")
    total_users = len(results_by_user)
    total_questions = len(set(case.question.id for case in case_results))
    total_cases = len(case_results)
    total_followups = sum(len(case.followup_questions) for case in case_results)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Users", total_users)
    with col2:
        st.metric("Questions", total_questions)
    with col3:
        st.metric("Total Cases", total_cases)
    with col4:
        st.metric("Follow-ups Generated", total_followups)

if __name__ == "__main__":
    main()
