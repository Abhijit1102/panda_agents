# src/quiz_generator.py
import os
import re
import streamlit as st
from langchain_openai import ChatOpenAI
import atexit

def quiz_generator_app():
    st.title("📝 Document-based Quiz Generator with LangChain")

    # Create folder for temp files
    os.makedirs("public", exist_ok=True)

    # Cleanup temporary files on exit
    def cleanup_files():
        for file in os.listdir("public"):
            if file.startswith("temp_"):
                os.remove(os.path.join("public", file))
    atexit.register(cleanup_files)

    # Initialize session state
    if "uploaded_file" not in st.session_state:
        st.session_state.uploaded_file = None
    if "questions" not in st.session_state:
        st.session_state.questions = {}
    if "user_answers" not in st.session_state:
        st.session_state.user_answers = {}

    # File uploader (accept only .txt)
    uploaded_file = st.file_uploader(
        "📂 Upload a text document (.txt) to generate a quiz",
        type=["txt"]
    )

    if uploaded_file is not None:
        st.session_state.uploaded_file = uploaded_file

    # Process uploaded file
    if st.session_state.uploaded_file:
        temp_file_path = f"./public/temp_{st.session_state.uploaded_file.name}"
        if not os.path.exists(temp_file_path):
            with open(temp_file_path, "wb") as f:
                f.write(st.session_state.uploaded_file.getbuffer())

        # Read text
        with open(temp_file_path, "r", encoding="utf-8") as f:
            text = f.read()

        st.success("✅ File loaded successfully!")

        # Generate questions if not already generated
        if not st.session_state.questions:
            st.subheader("🤖 Generating Quiz...")
            llm = ChatOpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                temperature=0
            )

            prompt = f"""
You are a teacher. Generate a quiz of 5 multiple-choice questions (with 4 options each)
based on the following content. Provide the correct answer for each question.

Content: {text}

Format:
Q1: ...
a) ...
b) ...
c) ...
d) ...
Answer: ...
"""

            with st.spinner("Generating questions... 🤔"):
                response = llm.invoke(prompt)
                quiz_text = response.content.strip()

            # Parse quiz into structured dictionary
            questions = {}
            q_num = None
            for line in quiz_text.split("\n"):
                line = line.strip()
                # Match question (handles optional ** or *)
                if match := re.match(r"\*?\*?Q(\d+):\s*(.*)", line):
                    q_num = f"Q{match.group(1)}"
                    questions[q_num] = {"question": match.group(2), "options": {}, "answer": ""}
                # Match options a), b), c), d)
                elif re.match(r"[abcd]\)", line) and q_num:
                    option_letter = line[0]
                    questions[q_num]["options"][option_letter] = line[2:].strip()
                # Match answer line
                elif q_num:
                    match = re.match(r"\*?\*?Answer:\*?\*?\s*(.*)", line)
                    if match:
                        questions[q_num]["answer"] = match.group(1).strip().split(")")[0]


            st.session_state.questions = questions

    # Display quiz
    if st.session_state.questions:
        st.subheader("📝 Quiz")
        for q_num, q_data in st.session_state.questions.items():
            # Use previous answer if exists
            default_option = st.session_state.user_answers.get(q_num, list(q_data["options"].keys())[0])
            st.session_state.user_answers[q_num] = st.radio(
                q_data["question"],
                list(q_data["options"].keys()),
                index=list(q_data["options"].keys()).index(default_option),
                key=q_num
            )

        # Submit button
        if st.button("Submit Quiz"):
            score = 0
            st.subheader("📊 Results")
            for q_num, q_data in st.session_state.questions.items():
                correct_answer = q_data["answer"]
                user_answer = st.session_state.user_answers[q_num]
                if user_answer.lower() == correct_answer.lower():
                    score += 1
                    st.success(f"{q_data['question']} ✅ Correct!")
                else:
                    st.error(f"{q_data['question']} ❌ Wrong! Correct answer: {correct_answer})")
            st.info(f"Your score: {score}/{len(st.session_state.questions)}")
