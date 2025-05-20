import streamlit as st
import PyPDF2
import io
import os
from openai import OpenAI
from dotenv import load_dotenv
import base64

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Validate API Key
# if not OPENAI_API_KEY:
#     st.error("OpenAI API key is missing. Please check your .env file.")
#     st.stop()

# Streamlit UI Configuration
st.set_page_config(page_title="AI Resume Critiquer", page_icon="📃", layout="centered")

# encode local image to base64
def get_base64_of_image(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Set background from local image
bg_image = get_base64_of_image("background.jpg")

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{bg_image}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📃 AI Resume Critiquer")
st.markdown("Upload your resume and get AI-powered feedback tailored to your needs!")

# File upload and input
uploaded_file = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])
job_role = st.text_input("Enter the job role you're targeting (optional)", placeholder="e.g. Software Engineer, Data Analyst")
tone = st.selectbox("Choose feedback tone", ["Professional", "Encouraging", "Concise"])

# Helper functions
def extract_text_from_pdf(file_bytes):
    try:
        pdf_reader = PyPDF2.PdfReader(file_bytes)
        return "\n".join(page.extract_text() or "" for page in pdf_reader.pages)
    except Exception:
        return ""

def extract_text_from_file(file):
    if file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(file.read()))
    return file.read().decode("utf-8")

# Button to trigger analysis
if st.button("🔍 Analyze Resume") and uploaded_file:
    with st.spinner("Analyzing resume with AI..."):
        try:
            file_content = extract_text_from_file(uploaded_file)

            if not file_content.strip():
                st.error("The uploaded file does not contain any text.")
                st.stop()

            prompt = f"""You are a professional HR recruiter and resume reviewer. Please analyze the following resume and give specific, constructive feedback in a **{tone.lower()}** tone.

Focus on the following:
1. Content clarity and professional tone
2. Skillset presentation (hard & soft skills)
3. Experience descriptions and quantification
4. Specific improvements to align with {'the role of ' + job_role if job_role else 'general job applications'}

Resume:
{file_content}

Structure your response in bullet points or markdown headers. Be clear, helpful, and actionable.
"""

            client = OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert resume reviewer with years of experience in HR and recruitment."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=1000
            )

            ai_feedback = response.choices[0].message.content

            st.markdown("### ✅ Analysis Results")
            st.markdown(ai_feedback)

            st.download_button("💾 Download Feedback", ai_feedback, file_name="resume_feedback.txt")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
else:
    st.info("Please upload your resume and optionally enter a target role.")

