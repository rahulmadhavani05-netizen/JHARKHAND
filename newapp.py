import streamlit as st
import pandas as pd
import pytesseract
from PIL import Image
import io
import os

# --- CONFIG ---
DATA_PATH = "data/certificates.csv"

# --- FUNCTIONS ---

@st.cache_resource
def load_certificate_db(csv_path=DATA_PATH):
    if not os.path.exists(csv_path):
        st.error(f"Certificate database not found at {csv_path}")
        return pd.DataFrame()
    return pd.read_csv(csv_path)

def extract_text_from_uploaded_file(uploaded_file):
    try:
        image = Image.open(uploaded_file)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        st.error(f"OCR failed: {e}")
        return ""

def verify_certificate(extracted_text, cert_db):
    for _, row in cert_db.iterrows():
        cid = str(row['certificate_id'])
        name = str(row['name'])
        if cid in extracted_text and name.lower() in extracted_text.lower():
            return row.to_dict(), True
    return None, False

# --- STREAMLIT UI ---

st.set_page_config(page_title="Certificate Verification", page_icon="🎓")
st.title("🎓 Certificate Verification Portal (Streamlit MVP)")

st.write("Upload a scanned certificate (JPG/PNG). The app will extract text and verify against the sample database.")

uploaded_file = st.file_uploader("Upload certificate image", type=["jpg", "jpeg", "png"])
cert_db = load_certificate_db()

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Certificate", use_column_width=True)
    with st.spinner("Extracting text via OCR..."):
        extracted_text = extract_text_from_uploaded_file(uploaded_file)
    st.subheader("Extracted Text")
    st.write(extracted_text)

    if not cert_db.empty:
        result, is_valid = verify_certificate(extracted_text, cert_db)
        if is_valid:
            st.success("✅ Certificate Verified!")
            st.json(result)
        else:
            st.error("❌ Certificate not found or appears invalid.")
    else:
        st.warning("Certificate database is empty or missing.")

st.markdown("""
---
**Sample certificate data (in `data/certificates.csv`):**

| certificate_id | name      | roll_number | marks | institution    | course                |
|:--------------:|:---------:|:-----------:|:-----:|:--------------:|:---------------------:|
| CERT001        | John Doe  | 2021001     | 88    | ABC University | BSc Computer Science  |
| CERT002        | Jane Smith| 2021002     | 91    | XYZ Institute  | BCom                  |

Edit or expand this CSV for your real use-case!
""")