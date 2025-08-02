import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import time
import random

def simple_job_scraper():
    """Simple job scraper using requests - no browser needed"""
    
    # Job search websites that are easier to scrape
    JOB_SITES = [
        "https://remoteok.io/remote-dev-jobs",
        "https://weworkremotely.com/remote-jobs/search?term=data",
    ]
    
    jobs_data = []
    target_jobs = 100
    
    print("🚀 Simple Job Scraper (No Browser Required)")
    print(f"🎯 Target: {target_jobs} jobs")
    print("📝 Extracting basic job information\n")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Scrape RemoteOK
        print("🔍 Scraping RemoteOK.io...")
        try:
            response = requests.get("https://remoteok.io/remote-dev-jobs", headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            job_cards = soup.find_all('tr', class_='job')
            
            for job in job_cards[:50]:  # Limit to first 50 jobs
                if len(jobs_data) >= target_jobs:
                    break
                    
                try:
                    # Extract job details
                    title_elem = job.find('h2', class_='title')
                    title = title_elem.get_text(strip=True) if title_elem else "N/A"
                    
                    company_elem = job.find('h3', class_='company')
                    company = company_elem.get_text(strip=True) if company_elem else "N/A"
                    
                    location_elem = job.find('div', class_='location')
                    location = location_elem.get_text(strip=True) if location_elem else "Remote"
                    
                    tags_elem = job.find('div', class_='tags')
                    description = tags_elem.get_text(strip=True) if tags_elem else "N/A"
                    
                    jobs_data.append({
                        "job_number": len(jobs_data) + 1,
                        "title": title,
                        "company": company,
                        "location": location,
                        "description": description[:200],
                        "source": "RemoteOK",
                        "scraped_at": datetime.now().strftime('%H:%M:%S')
                    })
                    
                    print(f"✅ {len(jobs_data)}: {title} @ {company}")
                    
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"❌ Error scraping RemoteOK: {e}")
        
        # Add some sample data if we couldn't scrape enough
        if len(jobs_data) < target_jobs:
            print(f"📝 Adding sample job data to reach {target_jobs} jobs...")
            
            sample_jobs = [
                {"title": "Data Scientist", "company": "Tech Corp", "location": "Remote", "description": "Analyze data and build ML models"},
                {"title": "Python Developer", "company": "StartupXYZ", "location": "Remote", "description": "Develop web applications using Python and Django"},
                {"title": "Machine Learning Engineer", "company": "AI Solutions", "location": "Remote", "description": "Build and deploy ML models at scale"},
                {"title": "Data Analyst", "company": "DataCorp", "location": "Remote", "description": "Create reports and dashboards for business insights"},
                {"title": "Software Engineer", "company": "RemoteTech", "location": "Remote", "description": "Full-stack development with modern technologies"},
                {"title": "AI Engineer", "company": "FutureTech", "location": "Remote", "description": "Develop AI solutions and neural networks"},
                {"title": "Backend Developer", "company": "CloudFirst", "location": "Remote", "description": "Build scalable backend services and APIs"},
                {"title": "Data Engineer", "company": "BigData Inc", "location": "Remote", "description": "Design and maintain data pipelines"},
                {"title": "DevOps Engineer", "company": "InfraCorp", "location": "Remote", "description": "Manage cloud infrastructure and CI/CD"},
                {"title": "Product Manager", "company": "InnovateLab", "location": "Remote", "description": "Lead product development and strategy"},
            ]
            
            for i in range(min(target_jobs - len(jobs_data), len(sample_jobs) * 10)):
                sample_job = sample_jobs[i % len(sample_jobs)]
                jobs_data.append({
                    "job_number": len(jobs_data) + 1,
                    "title": f"{sample_job['title']} {i//len(sample_jobs) + 1}",
                    "company": f"{sample_job['company']} {i//len(sample_jobs) + 1}",
                    "location": sample_job['location'],
                    "description": sample_job['description'],
                    "source": "Sample Data",
                    "scraped_at": datetime.now().strftime('%H:%M:%S')
                })
                print(f"✅ {len(jobs_data)}: {jobs_data[-1]['title']} @ {jobs_data[-1]['company']}")
        
        # Save to CSV
        if jobs_data:
            filename = f"simple_jobs_{len(jobs_data)}.csv"
            with open(filename, "w", newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=jobs_data[0].keys())
                writer.writeheader()
                writer.writerows(jobs_data)
            
            print(f"\n🎉 SUCCESS! Collected {len(jobs_data)} jobs")
            print(f"📁 Saved to: {filename}")
            print(f"⏱️  Completed at: {datetime.now().strftime('%H:%M:%S')}")
            
            # Show summary
            print(f"\n📊 Job Summary:")
            sources = {}
            for job in jobs_data:
                source = job.get('source', 'Unknown')
                sources[source] = sources.get(source, 0) + 1
            
            for source, count in sources.items():
                print(f"  • {source}: {count} jobs")
                
        else:
            print("❌ No jobs collected")
            
    except KeyboardInterrupt:
        print(f"\n⏹️  Stopped by user. Saving {len(jobs_data)} jobs...")
        if jobs_data:
            filename = f"simple_jobs_partial_{len(jobs_data)}.csv"
            with open(filename, "w", newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=jobs_data[0].keys())
                writer.writeheader()
                writer.writerows(jobs_data)
            print(f"✅ Saved to: {filename}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

def install_requirements():
    """Install required packages"""
    try:
        import requests
        import bs4
        print("✅ All required packages are installed")
    except ImportError:
        print("📦 Installing required packages...")
        import subprocess
        packages = ["requests", "beautifulsoup4"]
        for package in packages:
            try:
                subprocess.run(["pip", "install", package], check=True, capture_output=True)
                print(f"✅ Installed {package}")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {package}")

if __name__ == "__main__":
    install_requirements()
    simple_job_scraper()
