import json
import time
import os
import requests
from scholarly import scholarly
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# List of expanded search queries
queries = [
    "Exercise snacking research studies",
    "Effects of exercise snacking on metabolism",
    "Exercise snacking and cardiovascular health",
    "Impact of short exercise sessions on strength and endurance",
    "Comparing exercise snacking vs traditional workouts",
    "High-intensity exercise snacking benefits",
    "Short-duration exercise health benefits",
    "Micro-workouts and metabolic health",
    "Exercise snacking impact on obesity",
    "Effect of intermittent exercise on fitness",
    "Physiological benefits of short workouts",
    "Exercise snacking and insulin sensitivity",
    "Brief exercise sessions and weight management",
    "Metabolic adaptations to short workouts",
    "Exercise snacking for cardiovascular improvement",
    "Aerobic fitness gains from short workouts",
    "Heart rate response to exercise snacking",
    "Impact of micro-workouts on blood pressure",
    "Small exercise bouts and heart health",
    "Effects of high-intensity micro-exercise on endurance",
    "Cardiorespiratory benefits of exercise snacking",
    "Exercise snacking for strength and hypertrophy",
    "Short workout sessions for muscle gain",
    "Resistance training in short bursts",
    "Can micro workouts increase strength?",
    "Muscle adaptations to brief resistance exercise",
    "Effect of exercise snacking on muscular endurance",
    "Exercise snacking and cognitive function",
    "Short workouts for brain health",
    "Neuroplasticity effects of short exercise bouts",
    "Does exercise snacking improve focus?",
    "Mental health benefits of intermittent exercise",
    "Exercise snacking vs continuous training",
    "Is HIIT better than exercise snacking?",
    "Exercise snacking vs steady-state cardio",
    "Comparing traditional workouts and short bursts of exercise",
    "Effectiveness of exercise snacking for fat loss",
    "Exercise snacking for older adults",
    "Short exercise sessions for sedentary individuals",
    "Exercise snacking in diabetic patients",
    "Short-duration exercise for joint health",
    "Exercise snacking for people with limited mobility",
    "Exercise snacking for office workers",
    "Micro-workouts at workplace",
    "Short exercise interventions for sedentary lifestyle",
    "How to incorporate exercise snacking into daily life?"
]

# File to store results
RESULTS_FILE = "scholar_results.json"

# Ensure the directory for HTML caching exists
os.makedirs("html_cache", exist_ok=True)

# Load existing results to avoid duplicates
def load_existing_results():
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

# Save a single result to the JSON file
def save_result_to_file(result):
    """Append a new result to the JSON file without loading the full dataset into memory."""
    with open(RESULTS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(result, indent=4, ensure_ascii=False) + ",\n")

# Setup Selenium WebDriver
def setup_driver(headless=True):
    options = Options()
    options.headless = headless
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# Fetch and store HTML before scraping
def fetch_html(url):
    """Fetches HTML from a webpage and stores it locally."""
    try:
        driver = setup_driver()
        driver.get(url)
        time.sleep(3)  # Allow JavaScript to load content
        html_content = driver.page_source
        driver.quit()

        filename = f"html_cache/{hash(url)}.html"
        with open(filename, "w", encoding="utf-8") as file:
            file.write(html_content)
        return filename
    except Exception as e:
        print(f"⚠️ Error fetching HTML for {url}: {e}")
        return None

# Extract research paper details after saving HTML
def fetch_full_content(url):
    """Extracts structured content from stored HTML."""
    html_file = fetch_html(url)
    if not html_file:
        return {"Error": "HTML not available"}

    try:
        with open(html_file, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")

        article_data = {
            "Title": "No Title Found",
            "Authors": "No Authors Found",
            "Abstract": "No Abstract Found",
            "DOI": "No DOI Found",
            "Keywords": "No Keywords Found",
            "Full Text Content": "No Full Text Available"
        }

        title_tag = soup.find("h1") or soup.find("h2")
        if title_tag:
            article_data["Title"] = title_tag.get_text(strip=True)

        author_tag = soup.find("div", class_="authors") or soup.find("span", class_="authors")
        if author_tag:
            article_data["Authors"] = author_tag.get_text(strip=True)

        abstract_tag = soup.find("div", class_="abstract-content") or soup.find("section", class_="abstract")
        if abstract_tag:
            article_data["Abstract"] = abstract_tag.get_text(separator=" ", strip=True)

        doi_tag = soup.find("a", href=lambda x: x and "doi.org" in x)
        if doi_tag:
            article_data["DOI"] = doi_tag["href"]

        keyword_section = soup.find("section", class_="keywords") or soup.find("p", class_="keywords")
        if keyword_section:
            article_data["Keywords"] = keyword_section.get_text(strip=True).replace("Keywords:", "")

        full_text_section = soup.find("div", class_="full-text") or soup.find("article")
        if full_text_section:
            article_data["Full Text Content"] = full_text_section.get_text(separator=" ", strip=True)
        else:
            for tag in soup(["script", "style", "nav", "footer", "aside", "form", "header"]):
                tag.extract()
            article_data["Full Text Content"] = soup.get_text(separator=" ", strip=True)[:10000]

        return article_data
    except Exception as e:
        print(f"⚠️ Failed to scrape {url}: {e}")
        return {"Error": "Content not available"}

# Fetch Google Scholar results
def fetch_scholar_results(query, max_results=5):
    """Fetches top Google Scholar results and extracts content."""
    results = []
    search_query = scholarly.search_pubs(query)

    for _ in range(max_results):
        try:
            article = next(search_query)
            paper_link = article.get("pub_url", "")

            result = {
                "title": article['bib'].get('title', 'N/A'),
                "author": article['bib'].get('author', 'N/A'),
                "publication_year": article['bib'].get('pub_year', 'N/A'),
                "abstract": article['bib'].get('abstract', 'N/A'),
                "citation_count": article.get('num_citations', 'N/A'),
                "link": paper_link
            }

            if paper_link:
                print(f"Scraping full abstract for: {paper_link}")
                full_abstract = fetch_full_content(paper_link)
                result["full_abstract"] = full_abstract

            results.append(result)
        except StopIteration:
            break

    return results

# Save new results while avoiding duplicates
def save_results():
    """Fetch results for all queries and save without duplicates."""
    existing_results = load_existing_results()
    seen_titles = {r.get("title", "").lower() for r in existing_results}

    for query in queries:
        print(f"Fetching Google Scholar results for: {query}")
        results = fetch_scholar_results(query)

        for result in results:
            title = result.get("title", "").lower()
            if title not in seen_titles:
                seen_titles.add(title)
                save_result_to_file(result)

        time.sleep(5)  # Prevent blocking

    print(f"✅ Data collection complete! Results saved in {RESULTS_FILE}")

# Run the process
save_results()
