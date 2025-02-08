import streamlit as st
import pandas as pd
import re
import spacy
from io import BytesIO
from pdfminer.high_level import extract_text

# Load Spacy NLP model
nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(uploaded_file):
    """Extract text from uploaded PDF file."""
    return extract_text(uploaded_file)

def extract_contact_info(text):
    """Extract name, email, and phone number from text."""
    doc = nlp(text)
    
    # Extract name 
    name = None
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name = ent.text
            break
    
    # Extract emails
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    
    # Extract phone numbers 
    phones = re.findall(r'\b(?:\+?\d{1,3}[\s-]?)?(?:\(\d{2,4}\)|\d{2,4})[\s-]?\d{3,4}[\s-]?\d{4}\b', text)
    
    return name, emails, phones

def convert_df_to_csv(df):
    """Convert DataFrame to CSV format."""
    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return output

# Streamlit UI
st.title("Resume Extractor")

uploaded_files = st.file_uploader("Upload Resumes (PDF only)", type=["pdf"], accept_multiple_files=True)

data_list = []

if uploaded_files:
    for uploaded_file in uploaded_files:
        # Extract text from resume
        text = extract_text_from_pdf(uploaded_file)
        
        # Extract name, emails, and phone numbers
        name, emails, phones = extract_contact_info(text)
        
        # Append data to list
        data_list.append({"Name": name, "Email": ', '.join(emails), "Phone Numbers": ', '.join(phones)})
    
    # Create DataFrame
    df = pd.DataFrame(data_list)
    
    # Display table
    st.write("### Information")
    st.dataframe(df)
    
    # Convert to CSV
    csv_file = convert_df_to_csv(df)
    
    # Download button
    st.download_button(label="Download as CSV", data=csv_file, file_name="extracted_data.csv", mime="text/csv")
