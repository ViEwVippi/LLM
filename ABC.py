import streamlit as st
from openai import OpenAI
import pandas as pd
from io import StringIO
from PyPDF2 import PdfReader

# Sidebar for API Key
st.sidebar.title("Settings")
st.sidebar.text("Provide your OpenAI API Key")
api_key = st.sidebar.text_input("OpenAI API Key", type="password")



# App Title and Description
st.title("Play's Sentiment Analysis")
st.markdown(
    """<p>
    <strong>NLP Application for Sentiment Analysis on Plays</strong><br>
    This application helps analyze the sentiments in plays using the ChatGPT 3.5 Turbo model.
    </p>""",
    unsafe_allow_html=True,
)

# Input for Play File
st.subheader("Upload Play")
st.text("Please upload your play in PDF, or TXT format.")
file = st.file_uploader("Choose a file", type=["txt", "pdf"])

# Input for Specific Section
st.subheader("Specify Section to Analyze")
st.text(
    "You may specify a range (e.g., page numbers, 'beginning', 'middle', 'end') or provide context (e.g., a specific event)."
)
section = st.text_input("Section", "")

if not file:
    st.warning("Please upload a file to proceed.")
    st.stop()

# Read and Process File
def read_file(file):
    if file.type == "text/plain":
        return file.read().decode("utf-8")
    elif file.type == "application/pdf":
        reader = PdfReader(file)
        return "\n".join([page.extract_text() for page in reader.pages])
    else:
        return ""

data = read_file(file)

if not data:
    st.error("Unable to read the uploaded file. Please try another file.")
    st.stop()

# Call OpenAI API for Sentiment Analysis
def analyze_sentiments(text, apikey):
    # Set the API key dynamically
    try:
        client = OpenAI(
            api_key= apikey,
            )
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for sentiment analysis."},
                {"role": "user", "content": f"Analyze the following play section:\n{text}.\n"},
            ],
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        raise Exception(f"OpenAI API error: {e}")

# Perform Sentiment Analysis
if api_key and file:
    if st.button("Analyze"):
        with st.spinner("Analyzing sentiments..."):
            try:
                analysis_result = analyze_sentiments(data, api_key)  # Pass the API key dynamically
                st.write(analysis_result)  # Display result
            except Exception as e:
                st.error(f"An error occurred: {e}")
else:
    st.info("Please provide both the API Key and upload a file to enable the Analyze button.")