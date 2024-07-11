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


load_dotenv()


genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
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
    model = model
    prompt = f"Analyze the sentiment of the following text and categorize it as positive, negative, or neutral. Provide a brief explanation for your categorization:\n\n{text}"
    response = model.generate_content(prompt)
    return response.text

def translate_text(text, target_language):
    model = model
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

st.title("'👩‍🎓Student Helper👨‍🎓")

st.sidebar.title("Student aid")
name = st.text_input("hey you? help to be of help  to you \n please, input your name?")

st.write(f"Welcome, {name} thank you for choosing us as your to go to student helper")
feature = st.sidebar.selectbox("Choose a feature that you require as student", ["Document Q&A", "Summarization", "Quiz Generation", "Sentiment Analysis", "Data Visualization", "Translator"])

if feature == "Document Q&A" or feature == "Summarization" or feature == "Quiz Generation":
    uploaded_file = st.file_uploader("Upload a file📁:", type=["txt", "pdf"])

    if uploaded_file is not None:
        file_content = read_file_content(uploaded_file)
        
        if file_content:
            st.success("File uploaded successfully✅!")
            
            if feature == "Document Q&A":
                user_question = st.text_input("Ask a question about the file uploaded📁:")
                if user_question:
                    response = get_gemini_response(user_question, file_content, mode="qa")
                    st.write("Gemini's response:")
                    st.write(response)
                    save_and_download(response, "qa_response.txt")
            
            elif feature == "Summarization":
                if st.button("Summarize Document"):
                    summary = get_gemini_response("", file_content, mode="summarize")
                    st.write("Summary of the file")
                    st.write(summary)
                    save_and_download(summary, "summary.txt")
            
            elif feature == "Quiz Generation":
                if st.button("Generate Quiz"):
                    quiz = get_gemini_response("", file_content, mode="quiz")
                    st.write("Quiz generated from the file📁:")
                    st.write(quiz)
                    save_and_download(quiz, "quiz.txt")

elif feature == "Sentiment Analysis":
    text_for_analysis = st.text_area("Enter text for sentiment analysis:")
    if st.button("Analyze Sentiment"):
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
            translation = translate_text(text_to_translate, target_language)
            st.write("Translation:")
            st.write(translation)
            save_and_download(translation, "translation.txt")
        else:
            st.error("Please fill out all fields")

st.sidebar.markdown("""
## How to use:
1. Choose a feature from the sidebar
2. Follow the instructions for each feature
3. Get answers you require
4. Download the results as a text file
5. Incase your document is in epub visit the other pages and convert it to txt format for easy aiding of the you
""")
