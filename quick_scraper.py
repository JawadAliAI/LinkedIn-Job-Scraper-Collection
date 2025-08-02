from playwright.sync_api import sync_playwright
import csv
from datetime import datetime
import time

def quick_linkedin_scraper():
    """Super simple LinkedIn job scraper - just basic info, no complexity"""
    
    # Multiple search URLs to get more jobs faster
    SEARCH_URLS = [
        "https://www.linkedin.com/jobs/search/?keywords=data%20scientist&f_WT=2",
        "https://www.linkedin.com/jobs/search/?keywords=data%20analyst&f_WT=2", 
        "https://www.linkedin.com/jobs/search/?keywords=machine%20learning&f_WT=2",
        "https://www.linkedin.com/jobs/search/?keywords=ai%20engineer&f_WT=2",
        "https://www.linkedin.com/jobs/search/?keywords=python%20developer&f_WT=2"
    ]
    
    jobs_data = []
    target_jobs = 100
    
    print("🚀 Quick LinkedIn Job Scraper")
    print(f"🎯 Target: {target_jobs} jobs")
    print("⚡ Fast extraction - basic info only\n")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            
            for search_url in SEARCH_URLS:
                if len(jobs_data) >= target_jobs:
                    break
                    
                print(f"🔍 Searching: {search_url.split('keywords=')[1].split('&')[0].replace('%20', ' ')}")
                
                page.goto(search_url)
                page.wait_for_timeout(3000)
                
                # Get all job cards on first page
                job_cards = page.query_selector_all("ul.jobs-search__results-list li")
                
                for job_card in job_cards:
                    if len(jobs_data) >= target_jobs:
                        break
                        
                    try:
                        job_card.click()
                        page.wait_for_timeout(1500)  # Shorter wait for speed
                        
                        # Quick extraction
                        title = "N/A"
                        company = "N/A"
                        location = "N/A"
                        description = "N/A"
                        
                        try:
                            title_el = page.query_selector("h2.topcard__title")
                            if title_el:
                                title = title_el.inner_text().strip()
                        except:
                            pass
                            
                        try:
                            company_el = page.query_selector("span.topcard__flavor")
                            if company_el:
                                company = company_el.inner_text().strip()
                        except:
                            pass
                            
                        try:
                            location_el = page.query_selector("span.topcard__flavor--bullet")
                            if location_el:
                                location = location_el.inner_text().strip()
                        except:
                            pass
                            
                        try:
                            desc_el = page.query_selector("div.description__text")
                            if desc_el:
                                description = desc_el.inner_text().strip()[:200]  # First 200 chars only
                        except:
                            pass
                        
                        jobs_data.append({
                            "job_number": len(jobs_data) + 1,
                            "title": title,
                            "company": company,
                            "location": location,
                            "description": description,
                            "scraped_at": datetime.now().strftime('%H:%M:%S')
                        })
                        
                        print(f"✅ {len(jobs_data)}: {title} @ {company}")
                        
                    except Exception as e:
                        continue
            
            browser.close()
            
            # Save to CSV
            if jobs_data:
                filename = f"quick_jobs_{len(jobs_data)}.csv"
                with open(filename, "w", newline='', encoding='utf-8') as file:
                    writer = csv.DictWriter(file, fieldnames=jobs_data[0].keys())
                    writer.writeheader()
                    writer.writerows(jobs_data)
                
                print(f"\n🎉 SUCCESS! Collected {len(jobs_data)} jobs")
                print(f"📁 Saved to: {filename}")
                print(f"⏱️  Time: {datetime.now().strftime('%H:%M:%S')}")
            
    except KeyboardInterrupt:
        print(f"\n⏹️  Stopped by user. Saving {len(jobs_data)} jobs...")
        if jobs_data:
            filename = f"quick_jobs_partial_{len(jobs_data)}.csv"
            with open(filename, "w", newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=jobs_data[0].keys())
                writer.writeheader()
                writer.writerows(jobs_data)
            print(f"✅ Saved to: {filename}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        if jobs_data:
            filename = f"quick_jobs_error_{len(jobs_data)}.csv"
            with open(filename, "w", newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=jobs_data[0].keys())
                writer.writeheader()
                writer.writerows(jobs_data)
            print(f"✅ Error recovery - saved to: {filename}")

if __name__ == "__main__":
    quick_linkedin_scraper()
