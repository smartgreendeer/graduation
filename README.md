# Student Helper App

## Overview

The Student Helper App is a web application designed to assist students with various tasks such as document text extraction, question and answer generation, document summarization, quiz generation, sentiment analysis, data visualization, and text translation. The app leverages Streamlit for the front-end interface and Google Generative AI for content generation.

## Features

1. **Document Text Extraction**:
   - Supports PDF and EPUB files.
   - Extracts text content from uploaded documents and allows conversion to TXT format for easy download.

2. **Document Q&A**:
   - Upload a document and ask questions about its content.
   - Generates answers using Google Generative AI.

3. **Document Summarization**:
   - Summarize the content of uploaded documents in bullet points.

4. **Quiz Generation**:
   - Generate multiple-choice questions and answers based on the content of uploaded documents.

5. **Sentiment Analysis**:
   - Analyze the sentiment of provided text and categorize it as positive, negative, or neutral.

6. **Data Visualization**:
   - Upload CSV files and visualize data using bar, line, or scatter plots.

7. **Text Translation**:
   - Translate text into the desired target language.

## Setup and Installation

### Prerequisites

- Python 3.7 or higher
- [Streamlit](https://streamlit.io/)
- [Google Generative AI](https://cloud.google.com/generative-ai) API key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/student-helper-app.git
   cd student-helper-app

Create a virtual environment
python3 -m venv venv
source venv/bin/activate

install required packages
pip install -r requirements.txt

create an env file for the api_key
GOOGLE_API_KEY=your_google_api_key

Run the streamlit app:
streamlit run chatbot.py
 
 it will run on port http://localhost:8501
