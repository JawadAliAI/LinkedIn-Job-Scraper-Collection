from playwright.sync_api import sync_playwright
import time
import re
import csv
from datetime import datetime

# Target countries and their Google domains
COUNTRIES = {
    "Germany": "google.de",
    "China": "google.com.hk",  # Google.cn is blocked, using HK
    "United Kingdom": "google.co.uk",
    "Australia": "google.com.au",
    "Canada": "google.ca"
}

JOB_ROLES = [
    "data scientist remote",
    "ai engineer remote", 
    "data analysis remote",
    "artificial intelligence engineer remote",
    "data analyst remote",
    "machine learning engineer remote",
    "python developer remote"
]

def extract_email(text):
    # More comprehensive email pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_pattern, text)

def extract_company_website(page):
    """Try to find company website from job posting"""
    try:
        # Look for website links in the job posting
        website_links = page.query_selector_all("a[href*='http']")
        for link in website_links:
            href = link.get_attribute('href')
            if href and not any(domain in href for domain in ['google', 'linkedin', 'indeed', 'glassdoor', 'facebook', 'twitter']):
                return href
    except:
        pass
    return None

def visit_company_website(page, website_url):
    """Visit company website to extract contact emails"""
    try:
        print(f"🌐 Checking company website: {website_url}")
        page.goto(website_url, timeout=10000)
        page.wait_for_timeout(3000)
        
        # Get page content
        content = page.content()
        emails = extract_email(content)
        
        if emails:
            return emails
            
        # Try to find contact/about pages
        contact_links = page.query_selector_all("a[href*='contact'], a[href*='about'], a[href*='team']")
        for link in contact_links[:3]:  # Check first 3 contact-related links
            try:
                href = link.get_attribute('href')
                if href:
                    if not href.startswith('http'):
                        href = website_url.rstrip('/') + '/' + href.lstrip('/')
                    
                    page.goto(href, timeout=10000)
                    page.wait_for_timeout(2000)
                    
                    content = page.content()
                    emails = extract_email(content)
                    if emails:
                        return emails
            except:
                continue
                
    except Exception as e:
        print(f"❌ Error checking website {website_url}: {e}")
    
    return []

def scrape_google_jobs():
    # User choice for no reboot option
    print("🔧 Google Jobs Scraper Setup")
    print("1. Run with fresh browser (recommended)")
    print("2. Continue without reboot (faster startup)")
    
    choice = input("Choose option (1-2): ").strip()
    
    try:
        with sync_playwright() as p:
            # More robust browser launch
            browser = p.chromium.launch(
                headless=False,
                slow_mo=500,  # Slower for stability
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor",
                    "--no-first-run",
                    "--disable-default-apps"
                ]
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 720}
            )
            page = context.new_page()

            jobs_data = []
            job_count = 0
            consecutive_no_emails = 0
            start_time = datetime.now()
            
            print("🚀 Starting Google Jobs scraper for REMOTE positions with emails...")
            print("🎯 TARGET: 100,000 jobs with emails")
            print("🌍 Searching in: Germany, China, United Kingdom, Australia, Canada")
            print("📌 Press Ctrl+C to stop and save partial results")
            print("🔍 This will check job descriptions and company websites for contact emails")
            print("⏱️  This may take several hours to complete - progress will be saved regularly")
            print(f"🕐 Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            if choice == "2":
                print("⚡ Running in no-reboot mode for faster processing")
            
            # ✅ Search through multiple job categories and countries
            for country, google_domain in COUNTRIES.items():
                if job_count >= 100000:
                    break
                    
                for job_role in JOB_ROLES:
                    if job_count >= 100000:
                        break
                        
                    print(f"\n🔍 Searching for: {job_role} in {country}")
                    
                    # Use Indeed jobs search instead of Google Jobs for better results
                    search_query = job_role.replace(" ", "%20")
                    search_url = f"https://www.indeed.com/jobs?q={search_query}&l={country}&rbl=Remote&jlid=remote"
                    
                    try:
                        page.goto(search_url, timeout=30000)
                        page.wait_for_timeout(5000)
                        
                        # Handle cookie consent
                        try:
                            accept_button = page.query_selector("button#onetrust-accept-btn-handler, button:has-text('Accept'), button:has-text('I Accept')")
                            if accept_button:
                                accept_button.click()
                                page.wait_for_timeout(2000)
                        except:
                            pass
                        
                        page_num = 0
                        
                        while job_count < 100000 and page_num < 10:  # Limit pages per search
                            # Better job card selectors for Indeed
                            job_cards = page.query_selector_all("h2.jobTitle a, [data-jk] h2 a")
                            
                            if not job_cards:
                                print(f"No more job cards found for {job_role} in {country}")
                                break

                            print(f"📋 Found {len(job_cards)} job cards on page {page_num + 1}")

                            for i, job_card in enumerate(job_cards[:15]):  # Process first 15 jobs per page
                                if job_count >= 100000:
                                    break
                                
                                try:
                                    # Get job URL and click
                                    job_url = job_card.get_attribute('href')
                                    if job_url and not job_url.startswith('http'):
                                        job_url = 'https://www.indeed.com' + job_url
                                    
                                    job_card.click()
                                    page.wait_for_timeout(4000)

                                    # Extract job details with better selectors
                                    title_element = page.query_selector("h1[data-testid='jobsearch-JobInfoHeader-title'], h1.jobsearch-JobInfoHeader-title")
                                    title = title_element.inner_text() if title_element else "N/A"
                                    
                                    company_element = page.query_selector("[data-testid='inlineHeader-companyName'] a, .jobsearch-InlineCompanyRating a")
                                    company = company_element.inner_text() if company_element else "N/A"
                                    
                                    description_element = page.query_selector("#jobDescriptionText, .jobsearch-jobDescriptionText")
                                    description = description_element.inner_text() if description_element else ""
                                    
                                    location_element = page.query_selector("[data-testid='job-location'], .jobsearch-JobInfoHeader-subtitle")
                                    location = location_element.inner_text() if location_element else ""
                                    
                                    # Verify job is remote
                                    remote_keywords = ["remote", "work from home", "telecommute", "anywhere", "distributed", "virtual", "home office", "remote work"]
                                    full_text = (title + " " + company + " " + description + " " + location).lower()
                                    is_remote = any(keyword in full_text for keyword in remote_keywords)

                                    if not is_remote:
                                        print(f"⚠️  Skipped non-remote job: {title} at {company}")
                                        continue

                                    # Extract emails from job description
                                    emails = extract_email(description)
                                    
                                    # If no emails in description, try company website
                                    if not emails and company_element:
                                        print(f"🔍 Looking for company website for: {title} at {company}")
                                        
                                        try:
                                            # Click on company name to get more info
                                            company_element.click()
                                            page.wait_for_timeout(3000)
                                            
                                            # Look for website link or contact info
                                            website_element = page.query_selector("a[href*='http']:not([href*='indeed']):not([href*='linkedin'])")
                                            if website_element:
                                                website_url = website_element.get_attribute('href')
                                                if website_url:
                                                    website_emails = visit_company_website(page, website_url)
                                                    if website_emails:
                                                        emails = website_emails
                                                        print(f"✅ Found email on company website: {emails[0]}")
                                            
                                            # Go back to job listing
                                            page.go_back()
                                            page.wait_for_timeout(3000)
                                            
                                        except Exception as e:
                                            print(f"❌ Error checking company: {e}")
                                    
                                    # Only add jobs that have emails AND are remote
                                    if emails and is_remote:
                                        consecutive_no_emails = 0
                                        jobs_data.append({
                                            "country": country,
                                            "job_category": job_role,
                                            "title": title,
                                            "company": company,
                                            "location": location,
                                            "description": description[:300],
                                            "email": ", ".join(emails),
                                            "source": "Indeed Jobs",
                                            "job_url": job_url
                                        })
                                        job_count += 1
                                        print(f"✅ Found remote job {job_count} with email: {title} at {company} ({country})")
                                        
                                        # Save progress every 500 jobs
                                        if job_count % 500 == 0:
                                            print(f"\n💾 Auto-saving progress at {job_count} jobs...")
                                            with open(f"indeed_jobs_progress_{job_count}.csv", "w", newline='', encoding='utf-8') as file:
                                                writer = csv.DictWriter(file, fieldnames=jobs_data[0].keys())
                                                writer.writeheader()
                                                writer.writerows(jobs_data)
                                            print(f"✅ Progress saved to indeed_jobs_progress_{job_count}.csv\n")
                                    else:
                                        consecutive_no_emails += 1
                                        print(f"📧 Skipped remote job without email: {title} at {company}")
                                        
                                        if consecutive_no_emails >= 20:
                                            print(f"⚠️  Found {consecutive_no_emails} consecutive jobs without emails.")
                                            consecutive_no_emails = 0
                                            
                                except Exception as e:
                                    print(f"❌ Error processing job {i+1}: {e}")
                                    continue

                            # Try to navigate to next page
                            page_num += 1
                            try:
                                next_button = page.query_selector("a[aria-label='Next Page'], a[aria-label='Next']")
                                if next_button and not next_button.is_disabled():
                                    next_button.click()
                                    page.wait_for_timeout(5000)
                                    print(f"📄 Moving to page {page_num + 1} for {job_role} in {country} (Found {job_count} jobs so far)")
                                else:
                                    print(f"No more pages available for {job_role} in {country}")
                                    break
                            except Exception as e:
                                print(f"Error navigating to next page: {e}")
                                break
                                
                    except Exception as e:
                        print(f"❌ Error loading page for {job_role} in {country}: {e}")
                        continue

            browser.close()

            # ✅ Save final CSV
            if jobs_data:
                final_time = datetime.now()
                duration = final_time - start_time
                
                with open("indeed_jobs_100k.csv", "w", newline='', encoding='utf-8') as file:
                    writer = csv.DictWriter(file, fieldnames=jobs_data[0].keys())
                    writer.writeheader()
                    writer.writerows(jobs_data)

                print(f"\n✅ Final data saved to indeed_jobs_100k.csv - Found {len(jobs_data)} REMOTE jobs with emails")
                print(f"⏱️  Total runtime: {duration}")
                
                # Show statistics by country and job category
                from collections import Counter
                country_counts = Counter([job['country'] for job in jobs_data])
                category_counts = Counter([job['job_category'] for job in jobs_data])
                
                print("\n📊 Remote jobs found by country:")
                for country, count in country_counts.items():
                    print(f"  • {country}: {count} jobs")
                
                print("\n📊 Remote jobs found by category:")
                for category, count in category_counts.items():
                    print(f"  • {category}: {count} jobs")
            else:
                print("❌ No remote jobs with emails found")
                
    except KeyboardInterrupt:
        print(f"\n⚠️  Script interrupted by user. Saving {len(jobs_data)} jobs found so far...")
        
        if jobs_data:
            final_time = datetime.now()
            duration = final_time - start_time
            
            with open("indeed_jobs_partial_100k.csv", "w", newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=jobs_data[0].keys())
                writer.writeheader()
                writer.writerows(jobs_data)
            print(f"✅ Partial data saved to indeed_jobs_partial_100k.csv - {len(jobs_data)} jobs")
            print(f"⏱️  Runtime before interruption: {duration}")
        
        try:
            browser.close()
        except:
            pass
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        
        if jobs_data:
            with open("indeed_jobs_error_100k.csv", "w", newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=jobs_data[0].keys())
                writer.writeheader()
                writer.writerows(jobs_data)
            print(f"✅ Data saved to indeed_jobs_error_100k.csv - {len(jobs_data)} jobs")
        
        try:
            browser.close()
        except:
            pass

if __name__ == "__main__":
    scrape_google_jobs()
