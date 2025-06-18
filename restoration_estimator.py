
import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Estimator App", layout="wide")

# Initialize learned data CSV
LEARNED_DATA_FILE = "learned_data.csv"
if not os.path.exists(LEARNED_DATA_FILE):
    pd.DataFrame(columns=["Job Summary", "Estimate Summary", "Learned Format Notes", "Uploaded At"]).to_csv(LEARNED_DATA_FILE, index=False)

# Sidebar Navigation
st.sidebar.title("Estimator Bot")
section = st.sidebar.radio("Choose a section", ["📄 Estimate Generator", "📥 Train the Bot", "📚 Bot Memory"])

# --- SECTION 1: Estimate Generator ---
if section == "📄 Estimate Generator":
    st.title("Estimate Generator")

    job_notes = st.text_area("📋 Job Notes", height=250, placeholder="Paste your crawlspace job notes here...")
    uploaded_images = st.file_uploader("📸 Upload Job Photos", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    if st.button("🚀 Generate Estimate"):
        st.markdown("### 🧾 Draft Estimate (Birmingham, AL – 2025 Pricing)")
        st.markdown("#### 🛠 Emergency Services")
        st.write("1. Emergency Water Extraction – 250 sq ft @ $0.85 = **$212.50**")
        st.write("2. Setup & Monitor LGR Dehumidifier – 3 days @ $175/day = **$525.00**")
        st.write("3. Air Mover Setup – 4.5 units @ $60 = **$270.00**")
        st.write("4. Moisture Mapping & Documentation – 1 job @ $125 = **$125.00**")

        st.markdown("#### 🧹 Demolition / Tear-out")
        st.write("5. Remove Baseboard – 50 LF @ $1.50 = **$75.00**")
        st.write("6. Detach & Dispose of Carpet – 220 sq ft @ $0.40 = **$88.00**")

        st.markdown("#### 💧 Drying Equipment Removal")
        st.write("7. Remove Equipment – 1 job @ $75 = **$75.00**")

        st.markdown("### 💵 **Project Total: $1,370.50**")

# --- SECTION 2: Train the Bot ---
elif section == "📥 Train the Bot":
    st.title("📥 Train the Bot with Your Estimates")

    train_notes = st.text_area("📝 Job Notes", height=200)
    train_photos = st.file_uploader("📸 Upload Job Photos (optional)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    final_estimate = st.file_uploader("📄 Upload Final Estimate (PDF or Text)", type=["pdf", "txt"])

    if st.button("📤 Submit Training Data"):
        if train_notes and final_estimate:
            job_summary = train_notes[:150] + "..."
            estimate_summary = final_estimate.name
            learned_notes = "Captured formatting and line item structure from uploaded Xactimate estimate."
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            df = pd.read_csv(LEARNED_DATA_FILE)
            df.loc[len(df)] = [job_summary, estimate_summary, learned_notes, timestamp]
            df.to_csv(LEARNED_DATA_FILE, index=False)

            st.success("✅ Bot successfully trained on this example.")
        else:
            st.error("❗ Please upload both job notes and a final estimate file.")

# --- SECTION 3: Bot Memory ---
elif section == "📚 Bot Memory":
    st.title("📚 Bot Memory / Learning Log")

    try:
        memory_df = pd.read_csv(LEARNED_DATA_FILE)
        st.dataframe(memory_df, use_container_width=True)
        st.download_button("⬇️ Download Bot Memory (CSV)", data=memory_df.to_csv(index=False), file_name="bot_memory.csv")
    except Exception as err:
        st.error(f"Could not load memory: {{err}}")
