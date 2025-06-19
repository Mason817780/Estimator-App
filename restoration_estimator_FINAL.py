import streamlit as st
import openai
import os
import pandas as pd
import json
from datetime import datetime
import base64
import fitz  # PyMuPDF

# --- SETUP ---
st.set_page_config(page_title="Estimator App V2", layout="wide")
openai.api_key = st.secrets["OPENAI_API_KEY"]

# File paths
MEMORY_CSV = "learned_data.csv"
RULES_JSON = "learned_rules.json"
if not os.path.exists(MEMORY_CSV):
    pd.DataFrame(columns=["Job Summary", "Learned Insights", "Uploaded At"]).to_csv(
        MEMORY_CSV, index=False
    )
if not os.path.exists(RULES_JSON):
    with open(RULES_JSON, "w") as f:
        json.dump({}, f)

# Sidebar
st.sidebar.title("Estimator Bot")
section = st.sidebar.radio(
    "Choose a section", ["📄 Estimate Generator", "📥 Train the Bot", "📚 Bot Memory"]
)


# --- HELPERS ---
def encode_image(file):
    return base64.b64encode(file.read()).decode("utf-8")


def extract_pdf_text(uploaded_pdf):
    try:
        doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
        return "".join([page.get_text() for page in doc])
    except Exception as e:
        return f"PDF error: {e}"


def load_rules():
    try:
        with open(RULES_JSON, "r") as f:
            return json.load(f)
    except:
        return {}


def update_rules(new_rules):
    try:
        current = load_rules()
        for key, val in new_rules.items():
            current[key] = val
        with open(RULES_JSON, "w") as f:
            json.dump(current, f, indent=2)
    except Exception as e:
        print(f"Rule update error: {e}")


# --- SECTION 1: Estimate Generator ---
if section == "📄 Estimate Generator":
    st.title("Estimate Generator (GPT-4 Vision + Learned Rules)")
    job_notes = st.text_area("📋 Job Notes", height=250)
    uploaded_images = st.file_uploader(
        "📸 Upload Job Photos", type=["jpg", "jpeg", "png"], accept_multiple_files=True
    )

    if st.button("🚀 Generate Estimate"):
        with st.spinner("Thinking..."):
            images_prompt = []
            for img in uploaded_images:
                encoded = encode_image(img)
                images_prompt.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{encoded}"},
                    }
                )

            rules = load_rules()  
            rules_text = (
                json.dumps(rules, indent=2) if rules else "No rules learned yet."
            )

            messages = [
                 {
                    "role": "system",
                    "content": (
                        "You are an Xactimate estimator. Always use learned "
                        "formatting, rules, and line item style from memory."
                    ),
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                f"Job Notes:\n{job_notes}\n\n"
                                f"Apply these learned rules:\n{rules_text}"
                            ),
                        }
                    ]
                    + images_prompt,
                },
            ]

            response = openai.ChatCompletion.create(
                   model="gpt-4-vision-preview", messages=messages, max_tokens=1800
            )

            output = response.choices[0].message.content
            st.markdown("### 🧾 Estimate Output")
            st.markdown(output)

# --- SECTION 2: Train the Bot ---
elif section == "📥 Train the Bot":
    st.title("Train the Bot")
    train_notes = st.text_area("📝 Job Notes", height=200)
    train_photos = st.file_uploader(
        "📸 Upload Photos (optional)",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
    )
    final_estimate = st.file_uploader("📄 Upload Final Estimate (PDF)", type=["pdf"])

    if st.button("📤 Analyze & Learn"):
        if train_notes and final_estimate:
            with st.spinner("Learning..."):
                pdf_text = extract_pdf_text(final_estimate)
                image_data = []
                for img in train_photos:
                    encoded = encode_image(img)
                    image_data.append(
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{encoded}"},
                        }
                    )

                learn_messages = [
                     {
                        "role": "system",
                        "content": (
                            "You're training a restoration estimator AI. Compare the job notes "
                            "and the final estimate. Extract rules for formatting, line items, "
                            "and structure. Output as JSON."
                        ),
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": (
                                    f"Job Notes:\n{train_notes}\n\n"
                                    f"Final Estimate:\n{pdf_text}"
                                ),
                            }
                        ]
                        + image_data,
                    },
                ]

                response = openai.ChatCompletion.create(
                    model="gpt-4-vision-preview",
                    messages=learn_messages,
                       max_tokens=1500,
                )
                learned_json = response.choices[0].message.content

                try:
                    rules = json.loads(learned_json)
                    update_rules(rules)
                except Exception as e:
                    rules = {"raw_summary": learned_json}
                    update_rules(rules)

                df = pd.read_csv(MEMORY_CSV)
                df.loc[len(df)] = [
                    train_notes[:100] + "...",
                    learned_json,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ]
                df.to_csv(MEMORY_CSV, index=False)

                st.success("✅ Learned and updated memory.")
                st.markdown("### Learned Insights")
                st.code(learned_json)
        else:
            st.warning("Please provide both notes and a PDF.")

# --- SECTION 3: Bot Memory ---
elif section == "📚 Bot Memory":
    st.title("📚 Bot Memory (Basic View)")
    try:
        df = pd.read_csv(MEMORY_CSV)
        st.dataframe(df)
    except:
        st.warning("Memory CSV missing or empty.")
