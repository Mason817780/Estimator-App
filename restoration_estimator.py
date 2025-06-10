import streamlit as st
import openai

# Paste your real OpenAI API key between the quotes
openai.api_key = "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&rlz=1C1RXQR_enUS1114US1114&oq=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&gs_lcrp=EgZjaHJvbWUyBggAEEUYOdIBCDU4MDFqMGo3qAIHsAIB8QXoqeGEOdyEp_EF6KnhhDnchKc&sourceid=chrome&ie=UTF-8"

st.title("🛠️ Crawlspace Estimate Generator")
st.write("Upload a job photo and type out the job notes. This tool will generate a draft estimate.")

image = st.file_uploader("Upload job photo", type=["jpg", "png", "jpeg"])
notes = st.text_area("Job Notes", placeholder="Crawlspace flood. 16 air movers. 4 dehumidifiers. Standing water.")

if st.button("Generate Estimate") and (image or notes):
    with st.spinner("Generating..."):
        response = openai.ChatCompletion.create(
            model="gpt-4-0613",
            messages=[
                {"role": "system", "content": "You are a professional restoration estimator. Write full Xactimate line items including codes, names, qty, unit price, and total."},
                {"role": "user", "content": f"Job notes: {notes}"}
            ],
            max_tokens=1500
        )
        st.success("Estimate Generated:")
        st.markdown(response.choices[0].message["content"])

