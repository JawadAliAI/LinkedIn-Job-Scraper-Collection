from playwright.sync_api import sync_playwright
import time
import re
import csv
from datetime import datetime

# Multiple job search URLs for different roles - REMOTE ONLY in specific countries
# f_WT=2 parameter filters for remote jobs on LinkedIn
# Location codes: Germany, China, United Kingdom, Australia, Canada
COUNTRIES = {
    "Germany": "101282230",
    "China": "102890883", 
    "United Kingdom": "101165590",
    "Australia": "101452733",
    "Canada": "101174742"
}

JOB_ROLES = [
    "data%20scientist",
    "ai%20engineer", 
    "data%20analysis",
    "artificial%20intelligence%20engineer",
    "data%20analyst"
]

# Generate URLs for each job role in each country
JOB_SEARCH_URLS = []
for country, geo_id in COUNTRIES.items():
    for role in JOB_ROLES:
        url = f"https://www.linkedin.com/jobs/search/?keywords={role}&location={country}&geoId={geo_id}&f_WT=2"
        JOB_SEARCH_URLS.append((url, country, role.replace("%20", " ")))

def extract_email(text):
    # More comprehensive email pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_pattern, text)

def extract_email_from_profile(page, profile_url):
    """Extract email from LinkedIn profile page"""
    try:
        page.goto(profile_url)
        page.wait_for_timeout(3000)
        
        # Look for contact info button
        contact_button = page.query_selector("a[data-control-name='contact_see_more']")
        if not contact_button:
            contact_button = page.query_selector("button:has-text('Contact info')")
        if not contact_button:
            contact_button = page.query_selector("a:has-text('Contact info')")
        
        if contact_button:
            contact_button.click()
            page.wait_for_timeout(2000)
            
            # Extract email from contact info modal
            email_elements = page.query_selector_all("a[href^='mailto:']")
            if email_elements:
                for element in email_elements:
                    href = element.get_attribute('href')
                    if href and 'mailto:' in href:
                        email = href.replace('mailto:', '').strip()
                        return [email]
            
            # Also check for email in text content of modal
            contact_section = page.query_selector("section.artdeco-modal")
            if contact_section:
                contact_text = contact_section.inner_text()
                emails = extract_email(contact_text)
                if emails:
                    return emails
                    
            # Close the modal
            close_button = page.query_selector("button[aria-label='Dismiss']")
            if close_button:
                close_button.click()
                page.wait_for_timeout(1000)
        
        # Check the about section for emails
        about_section = page.query_selector("section.artdeco-card:has-text('About')")
        if about_section:
            about_text = about_section.inner_text()
            emails = extract_email(about_text)
            if emails:
                return emails
        
        # For company pages, check additional sections
        if '/company/' in profile_url:
            # Check company overview section
            overview_section = page.query_selector("section[data-module='OverviewModule']")
            if overview_section:
                overview_text = overview_section.inner_text()
                emails = extract_email(overview_text)
                if emails:
                    return emails
            
            # Check company details/contact section
            contact_section = page.query_selector("section:has-text('Website')")
            if contact_section:
                contact_text = contact_section.inner_text()
                emails = extract_email(contact_text)
                if emails:
                    return emails
                    
    except Exception as e:
        print(f"❌ Error extracting email from profile: {e}")
    
    return []

def scrape_linkedin_jobs():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)  # set headless=True to hide browser
            context = browser.new_context()
            page = context.new_page()

            jobs_data = []
            job_count = 0
            consecutive_no_emails = 0
            start_time = datetime.now()
            
            print("🚀 Starting LinkedIn job scraper for REMOTE positions with emails...")
            print("🎯 TARGET: 100,000 jobs with emails")
            print("🌍 Searching in: Germany, China, United Kingdom, Australia, Canada")
            print("📌 Press Ctrl+C to stop and save partial results")
            print("🔍 This will now check recruiter and company profiles for contact emails")
            print("⏱️  This may take several hours to complete - progress will be saved regularly")
            print(f"🕐 Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            # Ask user if they want to login
            print("🔐 LinkedIn Login Options:")
            print("1. Login for better profile access (RECOMMENDED)")
            print("2. Skip login and continue with limited access")
            
            while True:
                try:
                    choice = input("\nEnter your choice (1 or 2): ").strip()
                    if choice in ['1', '2']:
                        break
                    else:
                        print("Please enter 1 or 2")
                except KeyboardInterrupt:
                    print("\n❌ Script cancelled by user")
                    return
            
            login_successful = False
            
            if choice == '1':
                # ✅ Step 1: Login to LinkedIn
                print("\n🔐 LinkedIn Login Required")
            page.goto("https://www.linkedin.com/login")
            print("Please log in to LinkedIn manually in the browser window...")
            print("⏳ Waiting for you to complete login (60 seconds)...")
            print("📝 Make sure you're logged in before the timer expires!")
            print("💡 TIP: If you need more time, the script will check again after 60 seconds\n")
            
            login_successful = False
            max_login_attempts = 3
            login_attempt = 1
            
            while not login_successful and login_attempt <= max_login_attempts:
                if login_attempt > 1:
                    print(f"🔄 Login attempt {login_attempt}/{max_login_attempts}")
                    print("⏳ Additional 30 seconds to complete login...\n")
                    time.sleep(30)
                else:
                    time.sleep(60)
                
                # Check if login was successful
                try:
                    # Try to navigate to LinkedIn feed to verify login
                    page.goto("https://www.linkedin.com/feed/")
                    page.wait_for_timeout(3000)
                    
                    # Check if we're redirected back to login page or if we can see feed elements
                    if "login" in page.url:
                        print(f"❌ Login attempt {login_attempt} failed - still on login page")
                        if login_attempt < max_login_attempts:
                            print("🔄 Please complete login in the browser window...")
                    else:
                        # Check for feed elements to confirm we're logged in
                        feed_element = page.query_selector("main.feed-scaffold-layout__content")
                        if feed_element:
                            login_successful = True
                            print("✅ Login successful! Enhanced profile access enabled")
                            print("🎉 You can now access more contact information from profiles\n")
                        else:
                            print(f"⚠️  Login verification inconclusive on attempt {login_attempt}")
                            if login_attempt < max_login_attempts:
                                print("🔄 Please ensure you're fully logged in...")
                                
                except Exception as e:
                    print(f"⚠️  Could not verify login status on attempt {login_attempt}: {e}")
                
                login_attempt += 1
            
            if not login_successful:
                print("⚠️  Proceeding without confirmed login - profile access may be limited")
                print("📧 Email extraction will focus on job descriptions and public info\n")
            else:
                print("\n⚠️  Skipping login - profile access will be limited")
                print("📧 Email extraction will focus on job descriptions and public info\n")
            
            # ✅ Step 2: Search through multiple job categories and countries (Remote jobs only)
            for search_url, country, job_role in JOB_SEARCH_URLS:
                if job_count >= 100000:
                    break
                    
                print(f"\n🔍 Searching for: {job_role} in {country}")
                
                try:
                    page.goto(search_url)
                    page.wait_for_timeout(3000)
                except Exception as e:
                    print(f"❌ Error loading page for {job_role} in {country}: {e}")
                    continue
            
                page_num = 0

                while job_count < 100000:
                    # Get current page job cards
                    job_cards = page.query_selector_all("ul.jobs-search__results-list li")
                    
                    if not job_cards:
                        print(f"No more job cards found for {job_role} in {country}")
                        break

                    for job in job_cards:
                        if job_count >= 100000:
                            break
                        
                        try:
                            job.click()
                            page.wait_for_timeout(2000)

                            title = page.query_selector("h2.topcard__title").inner_text() if page.query_selector("h2.topcard__title") else ""
                            company = page.query_selector("span.topcard__flavor").inner_text() if page.query_selector("span.topcard__flavor") else ""
                            description = page.query_selector("div.description__text").inner_text() if page.query_selector("div.description__text") else ""
                            
                            # Check for remote work indicators
                            location_element = page.query_selector("span.topcard__flavor--bullet")
                            location = location_element.inner_text() if location_element else ""
                            
                            # Verify job is remote
                            remote_keywords = ["remote", "work from home", "telecommute", "anywhere", "distributed", "virtual"]
                            full_text = (title + " " + company + " " + description + " " + location).lower()
                            is_remote = any(keyword in full_text for keyword in remote_keywords)

                            # First check description for emails (rare but possible)
                            emails = extract_email(description)
                            recruiter_name = ""
                            
                            # If no emails in description, try to get from recruiter profile
                            if not emails and is_remote:
                                print(f"🔍 Looking for recruiter profile for: {title} at {company}")
                                
                                # Look for recruiter information
                                recruiter_element = page.query_selector("a.app-aware-link:has-text('Recruiter')")
                                if not recruiter_element:
                                    recruiter_element = page.query_selector("a[href*='/in/']:has(img)")
                                if not recruiter_element:
                                    recruiter_element = page.query_selector("a.jobs-poster__name")
                                    
                                if recruiter_element:
                                    recruiter_name = recruiter_element.inner_text().strip()
                                    recruiter_url = recruiter_element.get_attribute('href')
                                    
                                    if recruiter_url and '/in/' in recruiter_url:
                                        if not recruiter_url.startswith('https://'):
                                            recruiter_url = 'https://www.linkedin.com' + recruiter_url
                                        
                                        print(f"📧 Checking recruiter profile: {recruiter_name}")
                                        profile_emails = extract_email_from_profile(page, recruiter_url)
                                        if profile_emails:
                                            emails = profile_emails
                                            print(f"✅ Found email in recruiter profile: {emails[0]}")
                                        else:
                                            print(f"❌ No email found in recruiter profile")
                                        
                                        # Go back to job page
                                        page.go_back()
                                        page.wait_for_timeout(2000)
                                
                                # If still no emails, try company page
                                if not emails:
                                    company_element = page.query_selector("a.jobs-details-top-card__company-url")
                                    if not company_element:
                                        company_element = page.query_selector("a[href*='/company/']")
                                    
                                    if company_element:
                                        company_url = company_element.get_attribute('href')
                                        if company_url and '/company/' in company_url:
                                            if not company_url.startswith('https://'):
                                                company_url = 'https://www.linkedin.com' + company_url
                                            
                                            print(f"🏢 Checking company profile: {company}")
                                            company_emails = extract_email_from_profile(page, company_url)
                                            if company_emails:
                                                emails = company_emails
                                                print(f"✅ Found email in company profile: {emails[0]}")
                                            else:
                                                print(f"❌ No email found in company profile")
                                            
                                            # Go back to job page
                                            page.go_back()
                                            page.wait_for_timeout(2000)
                            
                            # Only add jobs that have emails AND are remote
                            if emails and is_remote:
                                consecutive_no_emails = 0
                                jobs_data.append({
                                    "country": country,
                                    "job_category": job_role,
                                    "title": title,
                                    "company": company,
                                    "location": location,
                                    "recruiter_name": recruiter_name,
                                    "description": description[:200],
                                    "email": ", ".join(emails)
                                })
                                job_count += 1
                                print(f"✅ Found remote job {job_count} with email: {title} at {company} ({country})")
                                
                                # Save progress every 1000 jobs
                                if job_count % 1000 == 0:
                                    print(f"\n💾 Auto-saving progress at {job_count} jobs...")
                                    with open(f"linkedin_jobs_progress_{job_count}.csv", "w", newline='', encoding='utf-8') as file:
                                        writer = csv.DictWriter(file, fieldnames=jobs_data[0].keys())
                                        writer.writeheader()
                                        writer.writerows(jobs_data)
                                    print(f"✅ Progress saved to linkedin_jobs_progress_{job_count}.csv\n")
                                    
                            elif not is_remote:
                                print(f"⚠️  Skipped non-remote job: {title} at {company}")
                            elif is_remote and not emails:
                                consecutive_no_emails += 1
                                print(f"📧 Skipped remote job without email: {title} at {company}")
                                
                                # If too many consecutive jobs without emails, suggest manual intervention
                                if consecutive_no_emails >= 20:
                                    print(f"⚠️  Found {consecutive_no_emails} consecutive jobs without emails. Consider manual login for better profile access.")
                                    consecutive_no_emails = 0
                                
                        except Exception as e:
                            print(f"❌ Error processing job: {e}")
                            continue

                    # Navigate to next page for current job category
                    page_num += 1
                    try:
                        # Look for next button and click it
                        next_button = page.query_selector("button[aria-label='Page forward']")
                        if not next_button:
                            next_button = page.query_selector("button[aria-label='Next']")
                        
                        if next_button and not next_button.is_disabled():
                            next_button.click()
                            page.wait_for_timeout(3000)
                            print(f"📄 Moving to page {page_num + 1} for {job_role} in {country} (Found {job_count} jobs so far)")
                        else:
                            print(f"No more pages available for {job_role} in {country}")
                            break
                    except Exception as e:
                        print(f"Error navigating to next page for {job_role} in {country}: {e}")
                        break

            browser.close()

            # ✅ Save final CSV
            if jobs_data:
                final_time = datetime.now()
                duration = final_time - start_time
                
                with open("linkedin_jobs_100k.csv", "w", newline='', encoding='utf-8') as file:
                    writer = csv.DictWriter(file, fieldnames=jobs_data[0].keys())
                    writer.writeheader()
                    writer.writerows(jobs_data)

                print(f"\n✅ Final data saved to linkedin_jobs_100k.csv - Found {len(jobs_data)} REMOTE jobs with emails")
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
            
            with open("linkedin_jobs_partial_100k.csv", "w", newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=jobs_data[0].keys())
                writer.writeheader()
                writer.writerows(jobs_data)
            print(f"✅ Partial data saved to linkedin_jobs_partial_100k.csv - {len(jobs_data)} jobs")
            print(f"⏱️  Runtime before interruption: {duration}")
        
        try:
            browser.close()
        except:
            pass
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        
        if jobs_data:
            with open("linkedin_jobs_error_100k.csv", "w", newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=jobs_data[0].keys())
                writer.writeheader()
                writer.writerows(jobs_data)
            print(f"✅ Data saved to linkedin_jobs_error_100k.csv - {len(jobs_data)} jobs")
        
        try:
            browser.close()
        except:
            pass

if __name__ == "__main__":
    scrape_linkedin_jobs()
