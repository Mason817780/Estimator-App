import streamlit as st
from PIL import Image
from PyPDF2 import PdfReader
import openai
import base64
import os

# Initialize your OpenAI API key securely (make sure this is set in your environment)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Streamlit App Layout
st.set_page_config(page_title="Estimator App")
st.title("📋 Crawlspace Estimate Generator")
st.write("Upload a job photo or PDF and type out the job notes to generate a draft estimate.")

# File Upload
uploaded_file = st.file_uploader("Upload job photo or PDF", type=["jpg", "jpeg", "png", "pdf"])

# Job Notes Input
notes = st.text_area("Job Notes", placeholder="Example: Living room flooded. 16 air movers, 4 dehumidifiers, standing water...")

# Extract text from PDF (optional)
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Encode image to base64 (optional for future GPT-4 Vision use)
def encode_image(file):
    return base64.b64encode(file.read()).decode("utf-8")

# Generate Estimate
if st.button("Generate Estimate"):
    with st.spinner("Generating estimate..."):

        extracted_text = ""
        encoded_image = ""

        if uploaded_file is not None:
            if uploaded_file.type == "application/pdf":
                extracted_text = extract_text_from_pdf(uploaded_file)
            else:
                encoded_image = encode_image(uploaded_file)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert Xactimate restoration estimator generating job estimates based on job notes and photos. "
                    "Use 2025 pricing from Birmingham, Alabama. Output MUST follow this strict structure and include dollar pricing:\n\n"
                    "PROJECT SCOPE:\n"
                    "1. Living Room Water Damage Restoration\n\n"
                    "ESTIMATED WORK DETAILS:\n"
                    "Living Room:\n\n"
                    "1. Emergency Service Call:\n"
                    "- WTR EMERSRV – Emergency service call during business hours – Qty: 1 @ $125 = $125\n\n"
                    "2. Water Extraction:\n"
                    "- WTR EXT – Extract water from affected area – Qty: 500 sq.ft @ $0.45 = $225\n\n"
                    "3. Demolition:\n"
                    "- DMO FLOOR – Remove and dispose carpet & pad – Qty: 300 sq.ft @ $1.25 = $375\n"
                    "- DMO WALL – Remove wet drywall (4ft cut) – Qty: 200 sq.ft @ $2.00 = $400\n\n"
                    "4. Drying Equipment:\n"
                    "- WTR DRYEQP – Drying setup fee – Qty: 1 @ $125 = $125\n"
                    "- WTR AIR MVR – 4 units x 3 days = 12 units @ $30 = $360\n"
                    "- WTR DEHU – 1 unit x 3 days = 3 units @ $45 = $135\n\n"
                    "5. Restoration Prep:\n"
                    "- RST FLRCOV – Install new carpet (sq.ft TBD)\n"
                    "- RST DRYWALL – Install and finish drywall (sq.ft TBD)\n\n"
                    "TOTAL ESTIMATED COST: [Auto-calculate based on items above]\n\n"
                    "⚠️ Output RULES:\n"
                    "- DO NOT explain anything.\n"
                    "- DO NOT write paragraphs.\n"
                    "- Only clean, line-by-line scope with quantities, pricing, and math.\n"
                    "- End with a bold total cost."
                )
            },
            {
                "role": "user",
                "content": f"Job Notes: {notes}\nExtracted Text: {extracted_text}"
            }
        ]

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=messages,
                max_tokens=2000
            )

            estimate = response.choices[0].message.content
            st.subheader("🧾 Draft Estimate:")
            st.markdown(estimate)

        except Exception as e:
            st.error(f"Error: {e}")
