import streamlit as st
from openai import OpenAI
import pandas as pd
from io import StringIO
from PyPDF2 import PdfReader
import json

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
    if file is None:
        return ""
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

prompt = """
You are a helpful assistant for analyzing plays. Your task is to analyze the content of the provided play script and output the results in JSON format.

1. Analyze the play and create the following outputs:
   - Dialogue Analysis Table: Each entry should include:
       - "speaker": The name of the character speaking in the play. Leave blank for narration or descriptions.
       - "line": The specific dialogue or text.
       - "sentiment": The sentiment of the line (e.g., positive, negative, neutral).
       - "emotion": Possible emotions associated with the speaker.
       - "reason": The reason why the speaker might be saying this line based on the play's context.

   - Emotion Statistics Table: Each entry should include:
       - "emotion": The name of each identified emotion.
       - "count": The number of times this emotion appears.
       - "proportion": The percentage of total lines associated with this emotion.
       - "description": When and where this emotion commonly appears in the play.

2. Output the result in the following JSON format:
```json
{
    "dialogue_table": [
        {
            "speaker": "Speaker Name",
            "line": "The line spoken by the character.",
            "sentiment": "Sentiment analysis of the line.",
            "emotion": ["Emotion 1", "Emotion 2"],
            "reason": "The reason behind the dialogue."
        },
        ...
    ],
    "emotion_statistics": [
        {
            "emotion": "Emotion Name",
            "count": Number of occurrences,
            "proportion": Percentage of total lines,
            "description": "Description of when and where the emotion occurs."
        },
        ...
    ]
}
"""

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
                {"role": "system", "content": prompt },
                {"role": "user", "content": f'Analyze the following play section:\n{text}. (If the section given is none or not section, Analyze the whole file.) '},
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
                result_dict = json.loads(analysis_result)
                dialogue_table = result_dict["dialogue_table"]
                emotion_statistics = result_dict["emotion_statistics"]
                dialogue_df = pd.DataFrame(dialogue_table)
                emotion_stats_df = pd.DataFrame(emotion_statistics)
                st.subheader("Dialogue Analysis")
                st.dataframe(dialogue_df)
                st.subheader("Emotion Statistics")
                st.dataframe(emotion_stats_df)
            except Exception as e:
                st.error(f"An error occurred: {e}")
else:
    st.info("Please provide both the API Key and upload a file to enable the Analyze button.")