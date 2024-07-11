import streamlit as st
import google.generativeai as genai
import os
import tempfile
import PyPDF2
import io
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from dotenv import load_dotenv
import time
from google.api_core import exceptions as google_exceptions


load_dotenv()


#genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
genai.configure(api_key="AIzaSyCBQxXktqsuZcJBhqep8iX-_NtbFgf8CzI")

model = genai.GenerativeModel('gemini-pro')


st.set_page_config(page_title="Student Helper", page_icon="👨‍🎓")

def read_file_content(uploaded_file):
    if uploaded_file.type == "text/plain":
        return uploaded_file.getvalue().decode("utf-8")
    elif uploaded_file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.getvalue()))
        return "\n".join(page.extract_text() for page in pdf_reader.pages)
    else:
        st.error("Unsupported file type. Please upload a .txt or .pdf file.")
        return None

def get_gemini_response(input_text, file_content, mode="qa"):
    model = genai.GenerativeModel('gemini-pro')
    if mode == "qa":
        prompt = f"Based on the following content:\n\n{file_content}\n\nAnswer this question: {input_text}"
    elif mode == "summarize":
        prompt = f"Summarize the following content in bullet points:\n\n{file_content}"
    elif mode == "quiz":
        prompt = f"Based on the following content, generate 5 multiple-choice questions with answers:\n\n{file_content}"
    response = model.generate_content(prompt)
    return response.text

def analyze_sentiment(text):
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"Analyze the sentiment of the following text and categorize it as positive, negative, or neutral. Provide a brief explanation for your categorization:\n\n{text}"
    response = model.generate_content(prompt)
    return response.text

def translate_text(text, target_language):
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"Translate the following text to {target_language}:\n\n{text}"
    response = model.generate_content(prompt)
    return response.text

def save_and_download(content, filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    with open(filename, "r", encoding="utf-8") as f:
        st.download_button(
            label="Download Result",
            data=f.read(),
            file_name=filename,
            mime="text/plain"
        )

def generate_quiz(file_content):
    prompt = f"Based on the following content, generate 15 multiple-choice questions. For each question, provide 4 options (A, B, C, D) and indicate the correct answer. Format each question as follows:\n\nQ1. Question text\nA) Option A\nB) Option B\nC) Option C\nD) Option D\nCorrect Answer: X\n\nContent:\n{file_content}"
    response = model.generate_content(prompt)
    return response.text

def generate_qui(content):
    max_retries = 3
    retry_delay = 5  # seconds

    for attempt in range(max_retries):
        try:
            if content.startswith("Generate a quiz about"):
                prompt = f"""{content}. Generate 15 multiple-choice questions. 
                For each question, provide 4 options (A, B, C, D) and indicate the correct answer. 
                Format each question as follows:

                Question: [Question text]
                A) [Option A]
                B) [Option B]
                C) [Option C]
                D) [Option D]
                Correct Answer: [A/B/C/D]

                Repeat this format for all 15 questions."""
            else:
                prompt = f"""Based on the following content, generate 15 multiple-choice questions. 
                For each question, provide 4 options (A, B, C, D) and indicate the correct answer. 
                Format each question as follows:

                Question: [Question text]
                A) [Option A]
                B) [Option B]
                C) [Option C]
                D) [Option D]
                Correct Answer: [A/B/C/D]

                Repeat this format for all 15 questions.

                Content:
                {content[:1000]}..."""

            response = model.generate_content(prompt)
            return response.text
        except google_exceptions.ResourceExhausted:
            st.warning(f"Rate limit reached. Retrying in {retry_delay} seconds... (attempt {attempt + 1})")
            time.sleep(retry_delay)
        except Exception as e:
            st.error(f"An error occurred while generating the quiz: {str(e)}")
            return None

    st.error("All attempts to generate quiz failed.")
    return None

    return None  # If all retries fail

def parse_quiz(quiz_text):
    questions = []
    current_question = None
    for line in quiz_text.split('\n'):
        line = line.strip()
        if line.startswith('Q'):
            if current_question:
                questions.append(current_question)
            current_question = {'text': line[3:], 'options': {}}  # Initialize 'options' here
        elif line.startswith(('A)', 'B)', 'C)', 'D)')) and current_question is not None:
            option_letter, option_text = line.split(')', 1)
            current_question['options'][option_letter.strip()] = option_text.strip()
        elif line.startswith('Correct Answer:') and current_question is not None:
            current_question['correct'] = line.split(':')[1].strip()

    if current_question:
        questions.append(current_question)

    # Validate that we have 15 complete questions
    if len(questions) == 15 and all(len(q['options']) == 4 and 'correct' in q for q in questions):
        return questions
    else:
        return None

def chatbot_response(user_input):
    prompt = f"User: {user_input}\nAssistant: "
    response = model.generate_content(prompt)
    return response.text

st.title("'👩‍🎓Student Helper👨‍🎓")
st.sidebar.title("Student aid")
name = st.sidebar.text_input("Hey you! Help us to be of help to you.\nPlease, input your name:")

if name:
    st.sidebar.write(f"Welcome, {name}! Thank you for choosing us as your go-to student helper.")
feature = st.sidebar.selectbox("Choose a feature that you require as student", ["Document Q&A", "Summarization", "Quiz Generation", "Sentiment Analysis", "Data Visualization", "Translator", "Interactive Quiz", "General Chatbot"])

if feature == "Document Q&A" or feature == "Summarization" or feature == "Quiz Generation" or feature == "Interactive Quiz":
    uploaded_file = st.file_uploader("Upload a file📁:", type=["txt", "pdf"])

    if uploaded_file is not None:
        file_content = read_file_content(uploaded_file)
        
        if file_content:
            st.success("File uploaded successfully✅!")
            
            if feature == "Document Q&A":
                user_question = st.text_input("Ask a question about the file uploaded📁:")
                if user_question:
                    with st.spinner("Generating response..."):
                            response = get_gemini_response(user_question, file_content, mode="qa")
                    st.write("Student helper response:")
                    st.write(response)
                    save_and_download(response, "qa_response.txt")
            
            elif feature == "Summarization":
                if st.button("Summarize Document"):
                    with st.spinner("Generating summary..."):
                        summary = get_gemini_response("", file_content, mode="summarize")
                    st.write("Summary of the file")
                    st.write(summary)
                    save_and_download(summary, "summary.txt")
            
            if feature == "Interactive Quiz":
                st.write("Interactive Quiz")
                
                quiz_source = st.radio("Choose quiz source:", ["Upload File", "Generate from Subject"])
                
                if quiz_source == "Upload File":
                    uploaded_file = uploaded_file
                    if uploaded_file is not None:
                        file_content = read_file_content(uploaded_file)
                        if file_content:
                            st.success(f"File '{uploaded_file.name}' uploaded and read successfully✅!")
                        else:
                            st.error("Failed to read file content. Please try again.")
                            file_content = None
                    else:
                        file_content = None
                else:
                    subject = st.text_input("Enter a subject for the quiz:")
                    file_content = f"Generate a quiz about {subject}" if subject else None

                if st.button("Generate Quiz") and file_content:
                    with st.spinner("Generating quiz..."):
                        quiz = generate_qui(file_content)
                    if quiz:
                        st.session_state.quiz = quiz.split('\n\n')  # Split questions into a list
                        st.session_state.current_question = 0
                        st.session_state.score = 0
                        st.session_state.quiz_completed = False
                        st.success("Quiz generated successfully!")
                    else:
                        st.error("Failed to generate quiz. Please try again.")

                if 'quiz' in st.session_state and not st.session_state.get('quiz_completed', False):
                    question_block = st.session_state.quiz[st.session_state.current_question]
                    question_lines = question_block.split('\n')
                    
                    st.write(f"Question {st.session_state.current_question + 1}:")
                    st.write(question_lines[0].replace("Question: ", ""))
                    
                    options = question_lines[1:5]
                    user_answer = st.radio("Select your answer:", options, format_func=lambda x: x)
                    
                    if st.button("Submit Answer"):
                        correct_answer = question_lines[-1].replace("Correct Answer: ", "")
                        if user_answer.startswith(correct_answer):
                            st.success("Correct!")
                            st.session_state.score += 1
                        else:
                            st.error(f"Incorrect. The correct answer was {correct_answer}")
                        
                        st.session_state.current_question += 1
                        
                        if st.session_state.current_question >= len(st.session_state.quiz):
                            st.session_state.quiz_completed = True
                        
                        st.experimental_rerun()

                if 'quiz' in st.session_state and st.session_state.get('quiz_completed', False):
                    total_questions = len(st.session_state.quiz)
                    score = st.session_state.score
                    percentage = (score / total_questions) * 100

                    st.write(f"Quiz completed!")
                    st.write(f"Your score: {score}/{total_questions}")
                    st.write(f"Percentage: {percentage:.2f}%")

                    # Provide feedback based on the percentage
                    if percentage >= 90:
                        st.success("Excellent work! You've mastered this topic!")
                    elif percentage >= 70:
                        st.success("Great job! You have a good understanding of the material.")
                    elif percentage >= 50:
                        st.warning("Good effort! There's room for improvement. Keep studying!")
                    else:
                        st.error("You might need to review this topic more. Don't give up!")

                    if st.button("Start New Quiz"):
                        for key in list(st.session_state.keys()):
                            if key in ['quiz', 'current_question', 'score', 'quiz_completed']:
                                del st.session_state[key]
                        st.experimental_rerun()
            
            elif feature == "Quiz Generation":
                if st.button("Generate Quiz"):
                    with st.spinner("Generating quiz..."):
                        quiz = get_gemini_response("", file_content, mode="quiz")
                    st.write("Quiz generated from the file📁:")
                    st.write(quiz)
                    save_and_download(quiz, "quiz.txt")

elif feature == "Sentiment Analysis":
    text_for_analysis = st.text_area("Enter text for sentiment analysis:")
    if st.button("Analyze Sentiment"):
        with st.spinner("Generating sentiment..."):
            sentiment = analyze_sentiment(text_for_analysis)
        st.write("Sentiment analysis")
        st.write(sentiment)
        save_and_download(sentiment, "sentiment_analysis.txt")

elif feature == "Data Visualization":
    st.write("Upload a CSV file to visualize data")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        st.write("Data Preview:")
        st.write(data.head())
        
        st.write("Select columns for visualization:")
        x_column = st.selectbox("X-axis", data.columns)
        y_column = st.selectbox("Y-axis", data.columns)
        
        chart_type = st.radio("Select chart type", ["Bar", "Line", "Scatter"])
        
        fig, ax = plt.subplots()
        if chart_type == "Bar":
            data.plot(kind="bar", x=x_column, y=y_column, ax=ax)
        elif chart_type == "Line":
            data.plot(kind="line", x=x_column, y=y_column, ax=ax)
        else:
            data.plot(kind="scatter", x=x_column, y=y_column, ax=ax)
        
        plt.title(f"{chart_type} Chart: {y_column} vs {x_column}")
        plt.xlabel(x_column)
        plt.ylabel(y_column)
        st.pyplot(fig)
        
        plot_description = f"Chart Type: {chart_type}\nX-axis: {x_column}\nY-axis: {y_column}"
        save_and_download(plot_description, "plot_description.txt")

elif feature == "Translator":
    st.write("Enter text to translate:")
    text_to_translate = st.text_area("please \n Type your text that you want to translate")
    target_language = st.text_input("Input language you require:")
    
    if st.button("Translate"):
        if text_to_translate and target_language:
            with st.spinner("Translating text..."):
                translation = translate_text(text_to_translate, target_language)
            st.write("Translation:")
            st.write(translation)
            save_and_download(translation, "translation.txt")
        else:
            st.error("Please fill out all fields")

elif feature == "General Chatbot":
    st.write("Chat with our general-purpose AI assistant:")
    user_input = st.text_input("You:")
    if user_input:
        response = chatbot_response(user_input)
        st.write("AI Assistant:")
        st.write(response)

st.sidebar.markdown("""
## How to use:
1. Choose a feature from the sidebar
2. Follow the instructions for each feature
3. Get answers you require
4. Download the results as a text file
5. Incase your document is in epub visit the other pages and convert it to txt format for easy aiding of the you
""")
