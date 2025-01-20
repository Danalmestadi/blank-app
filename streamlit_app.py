import streamlit as st
import pdfplumber
import spacy
import pandas as pd
from io import BytesIO

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Function to extract text from PDF
def extract_text_from_pdf(file):
    with pdfplumber.open(file) as pdf:
        text = "".join([page.extract_text() for page in pdf.pages])
    return text

# Function to analyze the text
def analyze_text(text):
    doc = nlp(text)
    data = {"Name": None, "Skills": [], "Education": [], "Experience": []}
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            data["Name"] = ent.text
        elif ent.label_ in {"ORG", "WORK_OF_ART"}:
            data["Experience"].append(ent.text)
        elif ent.label_ == "SKILL":
            data["Skills"].append(ent.text)
        elif ent.label_ == "EDUCATION":
            data["Education"].append(ent.text)
    return data

# Streamlit UI
st.title("Resume Analyzer")
uploaded_files = st.file_uploader("Upload Resumes (PDF only)", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    all_data = []
    for uploaded_file in uploaded_files:
        text = extract_text_from_pdf(uploaded_file)
        analysis = analyze_text(text)
        all_data.append(analysis)
    
    # Convert all_data to DataFrame
    df = pd.DataFrame(all_data)
    
    st.subheader("Extracted Data")
    st.dataframe(df)

    # Provide a download button for the DataFrame
    st.subheader("Download Results")

    # Function to convert DataFrame to Excel
    @st.cache
    def convert_df_to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        processed_data = output.getvalue()
        return processed_data

    excel_data = convert_df_to_excel(df)

    # Add download button
    st.download_button(
        label="Download Excel Sheet",
        data=excel_data,
        file_name="resume_analysis.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
