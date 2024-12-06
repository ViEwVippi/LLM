import streamlit as st
import pandas as pd
from openai import AsyncOpenAI

# Asynchronous function to analyze script
async def analyze_script_async(text, api_key):
    # Pass API Key while creating the AsyncOpenAI client
    client = AsyncOpenAI(api_key=api_key)
    
    prompt = (
        "Analyze the following script. Separate character names, dialogues, "
        "and determine the emotion conveyed in each dialogue. Provide results "
        "in the following format: Character, Dialogue, Emotion.\n\n" + text
    )
    
    completion = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return completion["choices"][0]["message"]["content"]

# Sidebar for API Key input
st.sidebar.title("OpenAI API Key")
api_key = st.sidebar.text_input("Enter your OpenAI API Key:", type="password")

# Main interface
st.title("Theater Script Coach")
st.write("Upload your script and analyze character dialogues and emotions.")

# File upload
uploaded_file = st.file_uploader("Upload a script (.txt, .csv, or .xlsx):", type=["txt", "csv", "xlsx"])

if uploaded_file and api_key:
    # Read the uploaded file
    if uploaded_file.name.endswith(".txt"):
        script_text = uploaded_file.read().decode("utf-8")
        st.text_area("Script Preview", script_text, height=200)
    elif uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
        st.dataframe(df)
        script_text = df.to_csv(index=False)
    elif uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
        st.dataframe(df)
        script_text = df.to_csv(index=False)

    # Analyze the script asynchronously
    if st.button("Analyze Script"):
        with st.spinner("Analyzing script..."):
            result = st.run_async(analyze_script_async(script_text, api_key))
        
        # Parse result into DataFrame
        lines = result.split("\n")
        data = [line.split(",") for line in lines if line]
        output_df = pd.DataFrame(data, columns=["Character", "Dialogue", "Emotion"])
        
        st.write("Analysis Results:")
        st.dataframe(output_df)

        # Download results as CSV
        csv = output_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Results as CSV",
            data=csv,
            file_name="script_analysis.csv",
            mime="text/csv",
        )
