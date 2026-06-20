# app.py
import streamlit as st
import requests
import fitz
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

PDF_URL = "https://hyrox.com/wp-content/uploads/2025/12/SSAC-Report.pdf"

@st.cache_data
def get_pdf_text(url):
    response = requests.get(url)
    pdf = fitz.open(stream=response.content, filetype="pdf")
    text = ""
    for page in pdf:
        text += page.get_text()
    return text

def chunk_text(text, chunk_size=3000, overlap=200):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks

def ask_question(question, pdf_text, model):
    chunks = chunk_text(pdf_text)
    relevant_chunks = [c for c in chunks if any(
        word.lower() in c.lower() for word in question.split()
    )]
    context = "\n\n".join(relevant_chunks[:3])
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Answer based on the provided context from a PDF. Be concise."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ]
    )
    return response.choices[0].message.content

# UI
st.title("🏋️ Hyrox Research Paper Q&A")
st.caption("Ask anything about the Hyrox Sports Science Report 2025")

with st.spinner("Loading PDF..."):
    pdf_text = get_pdf_text(PDF_URL)

question = st.text_input("Ask a question:")
model = st.selectbox("Choose a model:", ["gpt-3.5-turbo", "gpt-4o-mini", "gpt-5.5"])

if question:
    with st.spinner("Thinking..."):
        answer = ask_question(question, pdf_text, model)
    st.markdown("### Answer")
    st.write(answer)