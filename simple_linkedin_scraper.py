from playwright.sync_api import sync_playwright
import time
import csv
from datetime import datetime

def scrape_linkedin_jobs_simple():
    """Simple LinkedIn job scraper - gets 100 jobs with basic info only"""
    
    # Simple job search URL for data science roles
    SEARCH_URL = "https://www.linkedin.com/jobs/search/?keywords=data%20scientist&location=Worldwide&f_WT=2"
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            
            jobs_data = []
            job_count = 0
            target_jobs = 100
            
            print("🚀 Starting Simple LinkedIn Job Scraper")
            print(f"🎯 TARGET: {target_jobs} jobs")
            print("📝 Extracting: Title, Company, Location, Description")
            print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            # Navigate to LinkedIn jobs
            page.goto(SEARCH_URL)
            page.wait_for_timeout(5000)
            
            page_num = 0
            
            while job_count < target_jobs:
                print(f"📄 Processing page {page_num + 1}...")
                
                # Get job cards on current page
                job_cards = page.query_selector_all("ul.jobs-search__results-list li")
                
                if not job_cards:
                    print("❌ No job cards found, stopping...")
                    break
                
                for i, job_card in enumerate(job_cards):
                    if job_count >= target_jobs:
                        break
                    
                    try:
                        # Click on job card to load details
                        job_card.click()
                        page.wait_for_timeout(2000)
                        
                        # Extract basic information
                        title_element = page.query_selector("h2.topcard__title")
                        title = title_element.inner_text().strip() if title_element else "N/A"
                        
                        company_element = page.query_selector("span.topcard__flavor")
                        company = company_element.inner_text().strip() if company_element else "N/A"
                        
                        location_element = page.query_selector("span.topcard__flavor--bullet")
                        location = location_element.inner_text().strip() if location_element else "N/A"
                        
                        description_element = page.query_selector("div.description__text")
                        if description_element:
                            description = description_element.inner_text().strip()
                            # Limit description to first 300 characters
                            description = description[:300] + "..." if len(description) > 300 else description
                        else:
                            description = "N/A"
                        
                        # Get job URL
                        job_url = page.url
                        
                        # Store job data
                        jobs_data.append({
                            "job_number": job_count + 1,
                            "title": title,
                            "company": company,
                            "location": location,
                            "description": description,
                            "job_url": job_url,
                            "scraped_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                        
                        job_count += 1
                        print(f"✅ Job {job_count}: {title} at {company}")
                        
                        # Save progress every 25 jobs
                        if job_count % 25 == 0:
                            print(f"💾 Progress: {job_count}/{target_jobs} jobs collected")
                        
                    except Exception as e:
                        print(f"❌ Error processing job {i+1}: {e}")
                        continue
                
                # Try to go to next page
                if job_count < target_jobs:
                    try:
                        next_button = page.query_selector("button[aria-label='Page forward']")
                        if not next_button:
                            next_button = page.query_selector("button[aria-label='Next']")
                        
                        if next_button and not next_button.is_disabled():
                            next_button.click()
                            page.wait_for_timeout(3000)
                            page_num += 1
                        else:
                            print("📄 No more pages available")
                            break
                    except Exception as e:
                        print(f"❌ Error navigating to next page: {e}")
                        break
            
            browser.close()
            
            # Save results to CSV
            if jobs_data:
                filename = f"linkedin_jobs_simple_{len(jobs_data)}.csv"
                with open(filename, "w", newline='', encoding='utf-8') as file:
                    fieldnames = ["job_number", "title", "company", "location", "description", "job_url", "scraped_at"]
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(jobs_data)
                
                print(f"\n✅ SUCCESS! Scraped {len(jobs_data)} jobs")
                print(f"📁 Data saved to: {filename}")
                print(f"⏱️  Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Show sample of collected data
                print(f"\n📊 Sample of collected jobs:")
                for i, job in enumerate(jobs_data[:5]):
                    print(f"  {i+1}. {job['title']} at {job['company']} - {job['location']}")
                    
            else:
                print("❌ No jobs were collected")
                
    except KeyboardInterrupt:
        print(f"\n⚠️  Script stopped by user. Saving {len(jobs_data)} jobs collected so far...")
        
        if jobs_data:
            filename = f"linkedin_jobs_partial_{len(jobs_data)}.csv"
            with open(filename, "w", newline='', encoding='utf-8') as file:
                fieldnames = ["job_number", "title", "company", "location", "description", "job_url", "scraped_at"]
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(jobs_data)
            print(f"✅ Partial data saved to: {filename}")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        
        if jobs_data:
            filename = f"linkedin_jobs_error_{len(jobs_data)}.csv"
            with open(filename, "w", newline='', encoding='utf-8') as file:
                fieldnames = ["job_number", "title", "company", "location", "description", "job_url", "scraped_at"]
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(jobs_data)
            print(f"✅ Error recovery - data saved to: {filename}")

if __name__ == "__main__":
    # Install required package if not already installed
    try:
        import playwright
    except ImportError:
        print("Installing playwright...")
        import subprocess
        subprocess.run(["pip", "install", "playwright"], check=True)
        subprocess.run(["playwright", "install"], check=True)
        print("✅ Playwright installed successfully!")
    
    scrape_linkedin_jobs_simple()
