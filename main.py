import streamlit as st
import json
import os
from datetime import date, time # Import for type hints if needed, str conversion is used
import time as python_time # For getting current timestamps

# Initialize session state variables if they don't exist
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
# Replace generated_quiz with all_quizzes_data
if 'all_quizzes_data' not in st.session_state:
    st.session_state.all_quizzes_data = [] # Initialize as empty list
if 'quiz_file_path' not in st.session_state:
    st.session_state.quiz_file_path = "quiz_data.json"
if 'quiz_submissions_file_path' not in st.session_state: # New session state for submissions
    st.session_state.quiz_submissions_file_path = "quiz_submissions.json"

DEFAULT_PASSWORD = "studywithpao"

# --- Helper Functions ---
def generate_dummy_mcqs(num_questions):
    """Generates a list of dummy multiple-choice questions."""
    quiz_questions = []
    for i in range(1, num_questions + 1):
        quiz_questions.append({
            "question_text": f"This is dummy question {i}. What is the placeholder answer?",
            "options": {
                "A": f"Option A for Q{i}",
                "B": f"Option B for Q{i} (Correct)",
                "C": f"Option C for Q{i}",
                "D": f"Option D for Q{i}"
            },
            "correct_answer": "B"
        })
    return quiz_questions

def save_all_quizzes(quizzes_list, filepath):
    """Saves the list of quiz objects to a JSON file."""
    try:
        with open(filepath, 'w') as f:
            json.dump(quizzes_list, f, indent=4)
        return True
    except Exception as e:
        st.error(f"Error saving quizzes to file: {e}")
        return False

def load_all_quizzes(filepath):
    """Loads a list of quiz objects from a JSON file."""
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                else: # Handle case where file might exist but not be a list (e.g. old format)
                    st.warning("Quiz data file is not in the expected format. Starting with an empty quiz list.")
                    return []
        except json.JSONDecodeError:
            st.error(f"Error decoding JSON from {filepath}. File might be corrupted. Starting with an empty quiz list.")
            return []
        except Exception as e:
            st.error(f"Error loading quizzes from file: {e}. Starting with an empty quiz list.")
            return []
    return [] # Return empty list if file doesn't exist

# --- Helper Functions for Submissions ---
def save_all_submissions(submissions_list, filepath):
    """Saves the list of submission objects to a JSON file."""
    try:
        with open(filepath, 'w') as f:
            json.dump(submissions_list, f, indent=4)
        return True
    except Exception as e:
        st.error(f"Error saving submissions to file: {e}")
        return False

def load_all_submissions(filepath):
    """Loads a list of submission objects from a JSON file."""
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                else:
                    st.warning(f"Submissions file {filepath} is not in the expected list format. Starting fresh.")
                    return [] 
        except json.JSONDecodeError:
            st.error(f"Error decoding JSON from {filepath}. File might be corrupted. Starting with an empty submissions list.")
            return []
        except Exception as e:
            st.error(f"Error loading submissions from file: {e}. Starting with an empty submissions list.")
            return []
    return []

# --- UI Logic ---

# Login Page
if not st.session_state.logged_in:
    st.title("Login Portal")
    role_choice = st.selectbox("Select your role", ("Admin", "Student"))
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if not password:
            st.warning("Please enter a password.")
        elif password == DEFAULT_PASSWORD:
            st.session_state.logged_in = True
            st.session_state.user_role = role_choice
            if st.session_state.user_role == "Admin":
                # Load all quizzes when admin logs in
                raw_quizzes_data = load_all_quizzes(st.session_state.quiz_file_path)
                # Filter out quizzes that don't have a title, as they are likely malformed
                # or represent empty entries in the quiz_data.json file.
                st.session_state.all_quizzes_data = [
                    quiz for quiz in raw_quizzes_data if quiz.get("title")
                ]
                
                # Notify user if some entries were filtered out
                if raw_quizzes_data and len(raw_quizzes_data) > len(st.session_state.all_quizzes_data):
                    st.toast(
                        "Note: Some entries in the quiz data file were incomplete (e.g., missing a title) and have not been displayed.", 
                        icon="⚠️"
                    )
            st.rerun()
        else:
            st.error("Invalid password. Please try again.")
else:
    # Logged-in User View
    st.success(f"Logged in as {st.session_state.user_role}")

    if st.session_state.user_role == "Admin":
        st.subheader("Admin Dashboard: Manage Quizzes")

        # Form for creating a new quiz
        with st.form("new_quiz_form"):
            st.write("Create New Quiz")
            quiz_title = st.text_input("Quiz Title*")
            uploaded_file = st.file_uploader("Upload a file to generate quiz from (optional, content not used yet)")
            
            num_questions_default = 20
            num_questions = st.number_input("Number of questions to generate", min_value=1, value=num_questions_default)
            quiz_duration = st.number_input("Quiz duration (minutes)", min_value=1, value=10)
            quiz_start_date = st.date_input("Quiz Start Date", value=date.today())
            quiz_start_time = st.time_input("Quiz Start Time", value=time(9,0))
            
            submitted_generate = st.form_submit_button("Generate and Save Quiz")

            if submitted_generate:
                if not quiz_title:
                    st.warning("Quiz Title is required.")
                elif uploaded_file is None: # For now, let's make file upload mandatory for generation
                    st.warning("Please upload a file to base the quiz on.")
                else:
                    st.info(f"Generating quiz titled '{quiz_title}' with {num_questions} questions from '{uploaded_file.name}', duration {quiz_duration} mins, starting {quiz_start_date} at {quiz_start_time}.")
                    
                    new_quiz_questions = generate_dummy_mcqs(num_questions)
                    new_quiz_data = {
                        "title": quiz_title,
                        "questions": new_quiz_questions,
                        "duration": quiz_duration,
                        "start_date": str(quiz_start_date), # Store as string
                        "start_time": str(quiz_start_time), # Store as string
                        "source_file": uploaded_file.name
                    }
                    
                    st.session_state.all_quizzes_data.append(new_quiz_data)
                    if save_all_quizzes(st.session_state.all_quizzes_data, st.session_state.quiz_file_path):
                        st.success(f"Quiz '{quiz_title}' generated and saved successfully!")
                        st.rerun() # Rerun to update the display of quizzes
                    else:
                        # Error is handled by save_all_quizzes, but we might want to remove the added quiz if save fails
                        st.session_state.all_quizzes_data.pop() # Remove the last added quiz if save failed
                        st.error("Failed to save the new quiz. Please check logs.")

        st.markdown("---")
        st.subheader("Available Quizzes")
        if st.session_state.all_quizzes_data:
            for index, quiz_item in enumerate(st.session_state.all_quizzes_data):
                expander_title = f"{quiz_item.get('title', 'Untitled Quiz')} (Questions: {len(quiz_item.get('questions', []))}, Duration: {quiz_item.get('duration', 'N/A')} mins)"
                with st.expander(expander_title):
                    st.markdown(f"**Start Date:** {quiz_item.get('start_date', 'N/A')}")
                    st.markdown(f"**Start Time:** {quiz_item.get('start_time', 'N/A')}")
                    if 'source_file' in quiz_item:
                        st.markdown(f"**Source File:** {quiz_item.get('source_file')}")
                    
                    st.markdown("**Questions:**")
                    if quiz_item.get('questions'):
                        for i, q in enumerate(quiz_item['questions']):
                            st.markdown(f"**Q{i+1}: {q['question_text']}**")
                            for option, text in q['options'].items():
                                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{option}. {text}")
                            # st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;*Correct Answer: {q['correct_answer']}*")
                            st.markdown("---")
                    else:
                        st.write("No questions found for this quiz.")
        else:
            st.info("No quizzes have been created yet. Use the form above to generate a new quiz.")

        st.markdown("---")
        st.subheader("Student Submissions & Notifications")
        all_submissions = load_all_submissions(st.session_state.quiz_submissions_file_path)

        if all_submissions:
            # Sort by submission time, newest first
            sorted_submissions = sorted(all_submissions, key=lambda x: x.get('submission_timestamp', 0), reverse=True)
            for sub in sorted_submissions:
                st.info(
                    f"Student '{sub.get('student_id', 'Unknown')}' completed quiz: '{sub.get('quiz_title', 'Untitled')}' "
                    f"on {sub.get('submission_time_str', 'N/A')}. "
                    f"Score: {sub.get('score', 'N/A')}/{sub.get('total_questions', 'N/A')}."
                )
        else:
            st.info("No student submissions yet.")


    elif st.session_state.user_role == "Student":
        st.subheader("Student Dashboard: Available Quizzes")

        if not st.session_state.all_quizzes_data:
            raw_quizzes_data = load_all_quizzes(st.session_state.quiz_file_path)
            st.session_state.all_quizzes_data = [
                quiz for quiz in raw_quizzes_data if quiz.get("title")
            ]

        today = date.today()
        available_quizzes_for_student = []
        if st.session_state.all_quizzes_data:
            for quiz_item in st.session_state.all_quizzes_data:
                quiz_start_date_str = quiz_item.get("start_date")
                if quiz_start_date_str:
                    try:
                        quiz_start_date_obj = date.fromisoformat(quiz_start_date_str)
                        if quiz_start_date_obj <= today:
                            available_quizzes_for_student.append(quiz_item)
                    except ValueError:
                        pass # Silently skip quizzes with malformed dates

        if available_quizzes_for_student:
            for quiz_data in available_quizzes_for_student:
                # Create a unique identifier for each quiz based on its title (or index if titles aren't unique)
                # For simplicity, assuming titles are unique enough for keys here.
                # A more robust solution might use a generated ID for each quiz.
                quiz_title_safe = quiz_data.get('title', 'untitled').replace(' ', '_').lower()
                quiz_id = f"quiz_{quiz_title_safe}" # Using a simplified ID

                status_key = f"{quiz_id}_status"
                start_time_key = f"{quiz_id}_start_timestamp"
                answers_key = f"{quiz_id}_answers"
                score_key = f"{quiz_id}_score" # For storing student's score for this quiz attempt
                total_q_key = f"{quiz_id}_total_questions" # For storing total questions for this quiz attempt


                # Initialize status if not present
                st.session_state.setdefault(status_key, 'not_started')
                quiz_status = st.session_state[status_key]

                expander_title = f"{quiz_data.get('title', 'Untitled Quiz')} (Duration: {quiz_data.get('duration', 'N/A')} mins, Starts: {quiz_data.get('start_date', 'N/A')})"
                # Keep expander open if quiz is in progress
                with st.expander(expander_title, expanded=(quiz_status == 'in_progress')):
                    st.markdown(f"**Quiz Details:**")
                    st.markdown(f"- **Duration:** {quiz_data.get('duration', 'N/A')} minutes")
                    st.markdown(f"- **Start Date:** {quiz_data.get('start_date', 'N/A')}")
                    st.markdown(f"- **Start Time:** {quiz_data.get('start_time', 'N/A')}")
                    st.markdown("---")

                    if quiz_status == 'not_started':
                        if st.button("Start Quiz", key=f"start_{quiz_id}"):
                            st.session_state[status_key] = 'in_progress'
                            st.session_state[start_time_key] = python_time.time() # Record current time as float
                            st.rerun()
                    
                    elif quiz_status == 'in_progress':
                        actual_quiz_start_time = st.session_state.get(start_time_key, python_time.time())
                        quiz_duration_minutes = quiz_data.get('duration', 0)
                        quiz_duration_seconds = quiz_duration_minutes * 60
                        
                        elapsed_seconds = python_time.time() - actual_quiz_start_time
                        remaining_seconds = quiz_duration_seconds - elapsed_seconds

                        if remaining_seconds <= 0:
                            st.session_state[status_key] = 'timed_out'
                            # Optionally save any answers collected so far if needed
                            st.error("Time's up! The quiz duration has expired.")
                            st.rerun()
                        else:
                            mins, secs = divmod(int(remaining_seconds), 60)
                            timer_placeholder = st.empty()
                            timer_placeholder.info(f"Time Remaining: {mins:02d}:{secs:02d}")
                            
                            # To make the timer update, we need to rerun the script periodically.
                            # This is a simple way; for smoother timers, JavaScript is better.
                            python_time.sleep(1) # Sleep for 1 second

                            with st.form(key=f"form_{quiz_id}"):
                                student_answers = {}
                                if quiz_data.get('questions'):
                                    st.markdown("**Questions:**")
                                    for q_num, q_data in enumerate(quiz_data['questions']):
                                        st.markdown(f"**Q{q_num+1}: {q_data['question_text']}**")
                                        options_dict = q_data['options']
                                        option_keys = list(options_dict.keys())
                                        selected_option_key = st.radio(
                                            label="Your answer:",
                                            options=option_keys,
                                            format_func=lambda opt_key: f"{opt_key}. {options_dict[opt_key]}",
                                            key=f"radio_{quiz_id}_q_{q_num}"
                                        )
                                        student_answers[q_num] = selected_option_key
                                
                                submitted_quiz = st.form_submit_button("Submit Answers")
                                
                                if submitted_quiz:
                                    st.session_state[answers_key] = student_answers
                                    st.session_state[status_key] = 'submitted'
                                    
                                    # Calculate score
                                    score = 0
                                    total_questions = 0
                                    if quiz_data.get('questions'):
                                        total_questions = len(quiz_data['questions'])
                                        for q_idx, q_info in enumerate(quiz_data['questions']):
                                            submitted_ans_key = student_answers.get(q_idx) # q_idx is 0-based
                                            correct_ans_key = q_info.get('correct_answer')
                                            if submitted_ans_key == correct_ans_key:
                                                score += 1
                                    
                                    st.session_state[score_key] = score
                                    st.session_state[total_q_key] = total_questions

                                    submission_record = {
                                        "quiz_title": quiz_data.get('title'),
                                        "quiz_id": quiz_id,
                                        "student_id": "Student", # Placeholder - needs actual student identification if app expands
                                        "answers": student_answers, # Optional: for detailed review later
                                        "score": score,
                                        "total_questions": total_questions,
                                        "submission_timestamp": python_time.time(), 
                                        "submission_time_str": python_time.strftime("%Y-%m-%d %H:%M:%S", python_time.localtime(python_time.time()))
                                    }

                                    current_submissions = load_all_submissions(st.session_state.quiz_submissions_file_path)
                                    current_submissions.append(submission_record)
                                    save_all_submissions(current_submissions, st.session_state.quiz_submissions_file_path)
                                    
                                    timer_placeholder.empty() # Clear the timer display
                                    st.success(f"Quiz '{quiz_data.get('title')}' submitted! Your score: {score}/{total_questions}")
                                    st.balloons()
                                    st.rerun()
                            # Rerun to update timer if not submitted
                            if st.session_state[status_key] == 'in_progress':
                                st.rerun() 

                    elif quiz_status == 'submitted':
                        st.success(f"Quiz '{quiz_data.get('title')}' has been submitted.")
                        
                        display_score = st.session_state.get(score_key, "N/A")
                        display_total_q = st.session_state.get(total_q_key, "N/A")
                        if display_score != "N/A":
                            st.markdown(f"**Your Score: {display_score}/{display_total_q}**")

                        st.markdown("**Your Submitted Answers:**")
                        submitted_ans = st.session_state.get(answers_key, {})
                        if quiz_data.get('questions') and submitted_ans:
                            for q_num, ans_key in submitted_ans.items():
                                question_text = quiz_data['questions'][q_num]['question_text']
                                answer_text = quiz_data['questions'][q_num]['options'][ans_key]
                                st.write(f"Q{q_num+1}: {question_text} \n  Your answer: {ans_key}. {answer_text}")
                        else:
                            st.write("No answers were recorded or questions found.")
                    
                    elif quiz_status == 'timed_out':
                        st.error("Time's up! This quiz was not submitted in time.")
                        # Optionally display any answers captured before timeout if implemented

        else:
            st.info("No quizzes are currently available for you to take. Please check back later.")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.all_quizzes_data = [] # Clear quizzes on logout
        # Clear student-specific quiz states on logout to avoid issues if another student logs in
        # This is a simple approach; a more robust one would namespace these by student ID.
        for key in list(st.session_state.keys()):
            if key.startswith("quiz_") and ("_status" in key or "_start_timestamp" in key or "_answers" in key or "_score" in key or "_total_questions" in key) :
                del st.session_state[key]
        st.rerun()