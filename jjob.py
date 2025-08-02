import requests
import openai
import smtplib
import feedparser
from email.message import EmailMessage
from pathlib import Path
from dotenv import load_dotenv
import os
import time
import random

# Load secrets
load_dotenv()

# OpenAI and Email setup
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
EMAIL_ADDRESS = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASS")
CV_PATH = Path("Jawad Ali Resume.pdf")

# RemoteOK job search
def search_jobs_from_remoteok(max_jobs=100):
    print("\n🔍 Fetching jobs from RemoteOK...")
    url = "https://remoteok.com/api"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers)
        jobs_data = response.json()
        filtered = []
        for job in jobs_data:
            if isinstance(job, dict):
                title = job.get("position") or job.get("title", "")
                company = job.get("company", "")
                email = job.get("email")
                if not email or "@" not in email:
                    continue
                combined = f"{title.lower()} {' '.join(str(tag).lower() for tag in job.get('tags', []))}"
                if any(k in combined for k in ["ai", "ml", "nlp", "deep learning", "data science"]):
                    filtered.append({
                        "title": title,
                        "company": company,
                        "email": email,
                        "url": job.get("url", "#")
                    })
                if len(filtered) >= max_jobs:
                    break
        print(f"✅ RemoteOK jobs found: {len(filtered)}")
        return filtered
    except Exception as e:
        print("❌ RemoteOK error:", e)
        return []

# Indeed job RSS feed

def get_indeed_jobs(keyword="AI Engineer", location="remote", max_jobs=50):
    print("\n🔍 Fetching jobs from Indeed RSS...")
    query = keyword.replace(" ", "+")
    url = f"https://www.indeed.com/rss?q={query}&l={location}"
    feed = feedparser.parse(url)
    jobs = []
    for entry in feed.entries[:max_jobs]:
        jobs.append({
            "title": entry.title,
            "company": entry.title.split(" - ")[-1],
            "email": None,
            "url": entry.link
        })
    print(f"✅ Indeed jobs found: {len(jobs)}")
    return jobs

# Dummy job filler
def generate_additional_jobs(count):
    print(f"\n➕ Generating {count} dummy jobs...")
    companies = ["Google", "Microsoft", "Amazon", "Meta"]
    titles = ["AI Engineer", "ML Scientist"]
    jobs = []
    for i in range(count):
        company = random.choice(companies)
        title = random.choice(titles)
        jobs.append({
            "title": title,
            "company": company,
            "email": None,
            "url": f"https://careers.{company.lower()}.com/job-{i}"
        })
    return jobs

# Combine sources
def search_multiple_job_sources(max_jobs=100):
    jobs = []
    jobs.extend(search_jobs_from_remoteok(min(50, max_jobs)))
    jobs.extend(get_indeed_jobs(max_jobs=min(30, max_jobs)))
    if len(jobs) < max_jobs:
        jobs.extend(generate_additional_jobs(max_jobs - len(jobs)))
    return jobs[:max_jobs]

# Email content generation
def generate_email(job):
    prompt = f"""
    Write a short job application email for the position of {job['title']} at {job['company']}.
    Name: Jawad Ali Yousafzai
    Email: jawadaliyousafzai.ai@gmail.com
    Phone: +923413503377
    Resume attached
    Skills: AI, NLP, CV, DL, Python, TensorFlow
    Education: BS in AI
    Experience: 3+ years
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=250
    )
    return response.choices[0].message.content

# Send email
def send_email(subject, body, to_email):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg.set_content(body)

    if CV_PATH.exists():
        with open(CV_PATH, "rb") as f:
            msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename=CV_PATH.name)
    else:
        print("⚠️ CV not found!")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"✅ Email sent to {to_email}")
        time.sleep(random.uniform(2, 5))
    except Exception as e:
        print(f"❌ Email error to {to_email}: {e}")
        time.sleep(5)

# Main loop
def main():
    target = 100
    jobs = search_multiple_job_sources(target)
    print(f"\n📨 Starting applications to {len(jobs)} jobs")
    sent = 0
    for i, job in enumerate(jobs, 1):
        print(f"\n[{i}] {job['title']} at {job['company']}")
        print(f"🔗 {job['url']}")
        if job['email']:
            try:
                body = generate_email(job)
                send_email(f"Application: {job['title']} at {job['company']}", body, job['email'])
                sent += 1
            except Exception as e:
                print("❌ Error:", e)
        else:
            print("📌 No email found – skipped.")
    print(f"\n🎯 Completed: {sent} emails sent")

if __name__ == "__main__":
    main()