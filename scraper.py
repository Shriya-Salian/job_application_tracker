from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse
import time


def get_domain(url):
    return urlparse(url).netloc.replace("www.", "")


# WORKDAY: Unisys, Calix, SAP, Oracle HCM
def extract_from_workday(url, driver):
    try:
        title_element = driver.find_element(By.TAG_NAME, 'h2')
        title = title_element.text.strip()
    except:
        title = "Unknown Title"

    try:
        company_element = driver.find_element(By.XPATH, '//div[@data-automation-id="postingCompanyName"]')
        company = company_element.text.strip()
    except:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        company = domain.split('.')[0].title()

    job_id = "N/A"
    for part in url.split('/'):
        if part.startswith('_R-'):
            job_id = part[1:]
            break

    if job_id == "N/A":
        try:
            job_id_element = driver.find_element(By.XPATH, '//span[contains(text(), "Job ID")]')
            job_id = job_id_element.find_element(By.XPATH, '..').text.replace('Job ID', '').strip()
        except:
            pass

    return {
        "title": title,
        "company": company,
        "job_id": job_id
    }


# INDEED
def extract_from_indeed(url, driver):
    try:
        title_element = driver.find_element(By.TAG_NAME, 'h1')
        title = title_element.text.strip()
    except:
        title = "Unknown Title"

    try:
        company_element = driver.find_element(By.CLASS_NAME, 'icl-u-lg-mr--sm')
        company = company_element.text.strip()
    except:
        company = "Unknown Company"

    job_id = "N/A"
    try:
        job_id = url.split('jk=')[1].split('&')[0]
    except:
        pass

    return {
        "title": title,
        "company": company,
        "job_id": job_id
    }


# GLASSDOOR
def extract_from_glassdoor(url, driver):
    try:
        title_element = driver.find_element(By.TAG_NAME, 'h1')
        title = title_element.text.strip()
    except:
        title = "Unknown Title"

    try:
        company_element = driver.find_element(By.XPATH, '//div[@data-test="employer-link"]')
        company = company_element.text.strip()
    except:
        company = "Unknown Company"

    job_id = url.split('/')[-2] if '/job-' in url else "N/A"

    return {
        "title": title,
        "company": company,
        "job_id": job_id
    }


# LINKEDIN
def extract_from_linkedin(url, driver):
    try:
        title_element = driver.find_element(By.TAG_NAME, 'h1')
        title = title_element.text.strip()
    except:
        title = "Unknown Title"

    try:
        company_element = driver.find_element(By.XPATH, '//a[contains(@href, "/company")]')
        company = company_element.text.strip()
    except:
        company = "Unknown Company"

    job_id = url.split("currentJobId=")[-1].split("&")[0] if "currentJobId=" in url else "N/A"

    return {
        "title": title,
        "company": company,
        "job_id": job_id
    }


# GENERIC FALLBACK
def extract_generic(url, driver):
    try:
        title_element = driver.find_element(By.TAG_NAME, 'h1')
        title = title_element.text.strip()
    except:
        title = "Unknown Title"

    company = get_domain(url).split('.')[0].title()
    job_id = "N/A"

    return {
        "title": title,
        "company": company,
        "job_id": job_id
    }


# MAIN SCRAPER FUNCTION
def extract_job_details(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        driver.get(url)
        time.sleep(3)  # Wait for JS to load

        domain = get_domain(url)

        if any(keyword in domain for keyword in ['myworkdayjobs', 'wd1', 'wd2', 'wd3', 'wd5']):
            result = extract_from_workday(url, driver)
            result['source'] = f"{result['company']} Workday"  # e.g., "Calix Workday"
        elif 'indeed.com' in domain:
            result = extract_from_indeed(url, driver)
            result['source'] = "Indeed"
        elif 'glassdoor.com' in domain:
            result = extract_from_glassdoor(url, driver)
            result['source'] = "Glassdoor"
        elif 'linkedin.com' in domain:
            result = extract_from_linkedin(url, driver)
            result['source'] = "LinkedIn"
        else:
            result = extract_generic(url, driver)
            result['source'] = result['company'] or "Unknown Site"
        
        return result

    except Exception as e:
        return {
            "title": "Error",
            "company": str(e),
            "job_id": None
        }

    finally:
        driver.quit()