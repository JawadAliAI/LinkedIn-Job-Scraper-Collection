import openai
import smtplib
from email.message import EmailMessage
from pathlib import Path
from dotenv import load_dotenv
import os

# Load API keys and credentials
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
EMAIL_ADDRESS = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASS")

# Path to your CV (PDF or DOCX)
CV_PATH = Path("Jawad Ali Resume.pdf")  # Your actual CV file

# Simulated job list (replace with real scraping later)
def search_jobs():
    return [
        {"title": "AI Research Engineer", "company": "DeepLearn Inc", "email": "hr@deeplearn.ai"},
        {"title": "NLP Scientist", "company": "LanguageAI", "email": "jobs@languageai.org"},
        {"title": "Computer Vision Engineer", "company": "VisionX", "email": "careers@visionx.com"}
    ]

# Generate email using OpenAI
def generate_email(job):
    prompt = f"""
    Write a short, professional job application email for the position of {job['title']} at {job['company']}.
    Mention relevant AI skills (NLP, Deep Learning, Python, TensorFlow).
    Note that the resume is attached. Keep it under 200 words.
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=250
    )
    return response.choices[0].message.content

# Send email with CV attachment
def send_email(subject, body, to_email):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg.set_content(body)

    # Attach CV
    if CV_PATH.exists():
        with open(CV_PATH, "rb") as f:
            msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename=CV_PATH.name)
        print("📎 CV attached.")
    else:
        print("⚠️ CV file not found!")

    # Send email
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"✅ Email sent to {to_email}\n")
    except smtplib.SMTPAuthenticationError:
        print("❌ Gmail authentication failed!")
        print("🔧 You need to set up a Gmail App Password:")
        print("   1. Go to https://myaccount.google.com/security")
        print("   2. Enable 2-Factor Authentication")
        print("   3. Generate an App Password for 'Mail'")
        print("   4. Replace EMAIL_PASS in your .env file with the 16-character app password")
        print(f"   5. Current email saved as draft for: {to_email}\n")

# Main process
def main():
    jobs = search_jobs()
    for job in jobs:
        print(f"📨 Preparing application for: {job['title']} at {job['company']}")
        email_body = generate_email(job)
        print("✉️ Email Preview:")
        print(email_body)
        send_email(
            subject=f"Application for {job['title']} Role",
            body=email_body,
            to_email=job['email']
        )

if __name__ == "__main__":
    main()
