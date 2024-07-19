import streamlit as st #for gui
import PyPDF2 #for reading and extracting text from pdf files
import ebooklib #handling EPUB files in the first script
from ebooklib import epub
import os #joins with the operating system
import tempfile
import re
import requests

# Function to extract text from PDF files
def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    num_pages = len(pdf_reader.pages)
    text = ""
    for page_num in range(num_pages):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
    return text

# Function to extract text from EPUB files
def extract_text_from_epub(file_path):
    book = epub.read_epub(file_path)
    text = ""
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        content = item.content.decode('utf-8', errors='ignore')
        clean_text = re.sub('<[^<]+?>', '', content)  # Remove HTML tags
        text += clean_text + "\n\n"
    return text.strip()

# Function to extract text from TXT files
def extract_text_from_txt(file):
    text = file.read()
    return text

# Function to save extracted text as a TXT file
def save_text_as_txt(text, filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)

# Function to delete temporary files
def delete_temp_file(file_path):
    os.remove(file_path)
    
    
# Function to send name to Zapier
@st.cache_data
def send_name_to_zapier(name):
    webhook_url = "https://hooks.zapier.com/hooks/catch/19454215/22bv1r6/"
    payload = {"name": name}
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to send name to Zapier: {str(e)}")
        return False

# Main function to run the Streamlit app
def main():
    # Set up the Streamlit page
    st.set_page_config(page_title='Student Helper', page_icon="👨‍🎓")
    st.title('👩‍🎓Student Helper👨‍🎓')

    # Create a sidebar for user input
    st.sidebar.title("Student aid")
    name = st.sidebar.text_input("Hey you! Help us to be of help to you.\nPlease, input your name:")

    if name:
        if send_name_to_zapier(name):
            st.sidebar.write(f"Welcome, {name}! Thank you for choosing us as your go-to student helper.")
        else:
            st.sidebar.write(f"Welcome, {name}! We couldn't register your name, but we're still here to help.")

    # Main page content
    st.markdown('This app helps you to extract text from PDF, EPUB and TXT files')
    st.write("Upload a file📁:")
    uploaded_file = st.file_uploader("Select a file📁 from your device💻", type=["pdf", "epub"])

    if uploaded_file:
        st.write("File uploaded successfully✅!")

        # Display file content
        st.subheader("File Content:")
        if uploaded_file.type == "application/pdf":
            # Handle PDF files
            text = extract_text_from_pdf(uploaded_file)
            st.text(text[:500])  # Display first 500 characters to preview 

            if st.button("Convert and Download as TXT🖹"):
                filename = f"{uploaded_file.name.split('.')[0]}.txt"
                save_text_as_txt(text, filename)
                st.success(f"Text saved as {filename}")
                st.download_button(
                    label="Download TXT🖹 file🚀",
                    data=open(filename, 'rb').read(),
                    file_name=filename,
                    mime="text/plain"
                )

        elif uploaded_file.type == "application/epub+zip":
            # Handle EPUB files
            # Save the EPUB file temporarily
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(uploaded_file.read())  # Write contents of uploaded file
                temp_file_path = temp_file.name

            text = extract_text_from_epub(temp_file_path)
            st.text(text[:500])  # Display first 500 characters

            # Convert and download as TXT file
            if st.button("Convert and Download as TXT🖹"):
                filename = f"{uploaded_file.name.split('.')[0]}.txt"
                save_text_as_txt(text, filename)
                st.success(f"Text saved as {filename}")
                with open(filename, 'rb') as file:
                    st.download_button(
                        label="Download TXT🖹 file🚀",
                        data=file.read(),
                        file_name=filename,
                        mime="text/plain"
                    )

            # Delete the temporary EPUB file
            delete_temp_file(temp_file_path)

        else:
            st.error("Please upload a PDF or EPUB file.")

# Run the app
if __name__ == "__main__":
    main()