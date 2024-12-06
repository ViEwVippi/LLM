import streamlit as st
import pandas as pd
import openai
from io import BytesIO

# **Sidebar**
st.sidebar.title("Settings")
api_key = st.sidebar.text_input("Enter OpenAI API Key", type="password")
uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel File", type=["csv", "xlsx"])

# **Function for API Call**
def get_chatgpt_response(prompt, api_key):
    try:
        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error: {e}"

# **Main Interface**
st.title("NLP Application with ChatGPT")

# Input from user
user_input = st.text_area("Enter your text prompt below:", "")

# Button to send prompt
if st.button("Submit") and user_input and api_key:
    response = get_chatgpt_response(user_input, api_key)
    st.subheader("ChatGPT Response:")
    st.write(response)

# DataFrame Processing
if uploaded_file:
    try:
        # Read file into DataFrame
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)

        st.subheader("Uploaded Data:")
        st.dataframe(df)

        # Option to process each row with ChatGPT
        if st.button("Process with ChatGPT"):
            if api_key:
                with st.spinner("Processing..."):
                    df['ChatGPT_Response'] = df.iloc[:, 0].apply(lambda x: get_chatgpt_response(str(x), api_key))
                st.subheader("Processed Data:")
                st.dataframe(df)

                # Download processed data
                towrite = BytesIO()
                df.to_csv(towrite, index=False)
                towrite.seek(0)
                st.download_button(
                    label="Download CSV",
                    data=towrite,
                    file_name="processed_data.csv",
                    mime="text/csv"
                )
            else:
                st.error("Please enter a valid OpenAI API Key.")
    except Exception as e:
        st.error(f"Error processing file: {e}")
