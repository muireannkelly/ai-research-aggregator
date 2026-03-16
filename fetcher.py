import feedparser
import requests
import json
import ssl
import certifi
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup

ssl_context = ssl.create_default_context(cafile=certifi.where())

FEEDS = {
    # Education blogs & journals
    "EDUCAUSE Review": "https://er.educause.edu/rss",
    "EdSurge": "https://www.edsurge.com/feed",
    "Research in Learning Technology": "https://journal.alt.ac.uk/index.php/rlt/gateway/plugin/WebFeedGatewayPlugin/rss2",
    "Khan Academy Blog": "https://blog.khanacademy.org/feed/",
    "Education Next": "https://educationnext.org/feed",
    "Computers & Education: AI": "https://www.sciencedirect.com/journal/computers-and-education-artificial-intelligence/rss/articles",

    # Thought leaders
    "Ethan Mollick (One Useful Thing)": "https://www.oneusefulthing.org/feed",
    "Lilach Mollick": "https://lilachmollick.substack.com/feed",
    "Azeem Azhar (Exponential View)": "https://www.exponentialview.co/feed",
    "Andrew Ng (The Batch)": "https://www.deeplearning.ai/the-batch/tag/science/",
    "Erik Brynjolfsson": "https://brynjolfsson.substack.com/feed",
    "Steve Fitzpatrick": "https://fitzyhistory.substack.com/feed",
    "Amanda Askell": "https://www.askell.blog/feed",
    "Zvi Mowshowitz": "https://thezvi.substack.com/feed",
    "Jack Clark (Import AI)": "https://jack-clark.net/feed",
    "Alberto Romero (Algorithmic Bridge)": "https://thealgorithmicbridge.substack.com/feed",
    "John Warner (Biblioracle)": "https://biblioracle.substack.com/feed",
    "Michael Spencer (AI Supremacy)": "https://www.ai-supremacy.com/feed",
    "Nik Bear Brown (Education & AI)": "https://www.skepticism.ai/s/education-and-ai/feed",
    "Economic Innovation Group": "https://agglomerations.eig.org/feed",
    "Dan Fitzpatrick (Forbes)": "https://www.forbes.com/sites/danfitzpatrick/feed/",

    # Competitor & org news
    "OpenAI News": "https://openai.com/news/rss.xml",
    "Google Education Blog": "https://blog.google/outreach-initiatives/education/rss/",

    # News
    "The Guardian Education": "https://www.theguardian.com/education/rss",
    "Inside Higher Ed": "https://www.insidehighered.com/rss.xml",
    "TechCrunch": "https://techcrunch.com/feed/",
    "MIT Technology Review": "https://www.technologyreview.com/feed/",
}

ARXIV_QUERIES = {
    "AI in education":              'ti:"education" AND (ti:"AI" OR ti:"artificial intelligence" OR ti:"large language model" OR ti:"LLM")',
    "AI tutoring & assessment":     '(ti:"tutoring" OR ti:"assessment") AND (ti:"AI" OR ti:"large language model" OR ti:"LLM")',
    "learning outcomes & efficacy": 'abs:"learning outcomes" AND (abs:"AI" OR abs:"LLM" OR abs:"large language model")',
    "pedagogy & instruction":       '(abs:"pedagogy" OR abs:"instructional design") AND (abs:"AI" OR abs:"artificial intelligence" OR abs:"LLM")',
    "intelligent tutoring systems": 'ti:"intelligent tutoring system" OR ti:"intelligent tutoring systems"',
    "automated assessment":         'ti:"automated assessment" OR ti:"automated grading" OR ti:"automated feedback"',
    "cognitive science & AI":       'abs:"cognitive science" AND (abs:"AI" OR abs:"large language model" OR abs:"LLM")',
    "learning science":             'abs:"learning science" AND (abs:"AI" OR abs:"artificial intelligence" OR abs:"LLM")',
}

CUTOFF = datetime.now(timezone.utc) - timedelta(days=7)

# Note: avoid generic words like "learn" or "learning" which match "machine learning"
EDUCATION_KEYWORDS = [
    "education", "edtech", "teaching", "teacher", "learner", "learners",
    "student", "students", "classroom", "curriculum", "pedagogy", "tutoring",
    "assessment", "literacy", "school", "university", "college", "course",
    "academic", "upskill", "reskill", "training", "instruction", "e-learning",
    "higher ed", "k-12", "learning outcome", "learning design", "learning science",
    "educational", "instructional"
]

FILTERED_SOURCES = {"Hacker News", "TechCrunch", "MIT Technology Review", "OpenAI News"}

def is_education_relevant(item):
    """Return True if the item is education/learning focused."""
    if item["source"] not in FILTERED_SOURCES:
        return True
    text = (item["title"] + " " + item["description"]).lower()
    return any(kw in text for kw in EDUCATION_KEYWORDS)

def parse_date(entry):
    for attr in ["published_parsed", "updated_parsed"]:
        if hasattr(entry, attr) and getattr(entry, attr):
            return datetime(*getattr(entry, attr)[:6], tzinfo=timezone.utc)
    return datetime.now(timezone.utc)

def fetch_rss():
    items = []
    for source, url in FEEDS.items():
        try:
            feed = feedparser.parse(url)
            count = 0
            for entry in feed.entries:
                pub_date = parse_date(entry)
                if pub_date >= CUTOFF:
                    items.append({
                        "title": entry.get("title", "No title"),
                        "url": entry.get("link", ""),
                        "source": source,
                        "date": pub_date.strftime("%Y-%m-%d"),
                        "description": entry.get("summary", "")[:300]
                    })
                    count += 1
            print(f"{source}: {count} items found")
        except Exception as e:
            print(f"{source}: error - {e}")
    return items

def fetch_arxiv():
    items = []
    for label, query in ARXIV_QUERIES.items():
        try:
            url = f"https://export.arxiv.org/api/query?search_query={requests.utils.quote(query)}&sortBy=submittedDate&sortOrder=descending&max_results=10"
            response = requests.get(url, timeout=10)
            feed = feedparser.parse(response.text)
            count = 0
            for entry in feed.entries:
                pub_date = parse_date(entry)
                if pub_date >= CUTOFF:
                    items.append({
                        "title": entry.get("title", "No title"),
                        "url": entry.get("link", ""),
                        "source": "arXiv",
                        "date": pub_date.strftime("%Y-%m-%d"),
                        "description": entry.get("summary", "")[:300]
                    })
                    count += 1
            print(f"arXiv ({label}): {count} items found")
        except Exception as e:
            print(f"arXiv ({label}): error - {e}")
    return items

def fetch_hacker_news():
    """Fetch Hacker News stories mentioning education or AI learning"""
    items = []
    queries = [
        "AI education", "edtech", "AI tutoring", "learning science",
        "pedagogy", "educational technology", "AI classroom",
        "teaching with AI", "AI assessment", "higher education AI"
    ]
    try:
        for query in queries:
            cutoff_ts = int((datetime.now(timezone.utc) - timedelta(days=7)).timestamp())
            url = f"https://hn.algolia.com/api/v1/search?query={requests.utils.quote(query)}&tags=story&numericFilters=created_at_i>{cutoff_ts}&hitsPerPage=5"
            response = requests.get(url, timeout=10)
            data = response.json()
            count = 0
            for hit in data.get("hits", []):
                title = hit.get("title", "No title")
                story_url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
                points = hit.get("points", 0)
                comments = hit.get("num_comments", 0)
                if points and points > 10:
                    items.append({
                        "title": title,
                        "url": story_url,
                        "source": "Hacker News",
                        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                        "description": f"{points} points, {comments} comments on Hacker News"
                    })
                    count += 1
            print(f"Hacker News ({query}): {count} items found")
    except Exception as e:
        print(f"Hacker News: error - {e}")
    return items

def fetch_anthropic_news():
    """Scrape Anthropic news page for recent posts"""
    items = []
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; research-aggregator/1.0)"}
        response = requests.get("https://www.anthropic.com/news", headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        count = 0
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "/news/" in href and href != "/news":
                full_url = f"https://www.anthropic.com{href}" if href.startswith("/") else href
                title = link.get_text(strip=True)
                if title and len(title) > 10:
                    items.append({
                        "title": title,
                        "url": full_url,
                        "source": "Anthropic News",
                        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                        "description": "Latest news and announcements from Anthropic"
                    })
                    count += 1
                    if count >= 5:
                        break
        print(f"Anthropic News: {count} items found")
    except Exception as e:
        print(f"Anthropic News: error - {e}")
    return items

def main():
    all_items = fetch_rss() + fetch_arxiv() + fetch_hacker_news() + fetch_anthropic_news()

    # Deduplicate by URL
    seen_urls = set()
    unique_items = []
    for item in all_items:
        if item["url"] not in seen_urls and item["url"]:
            seen_urls.add(item["url"])
            unique_items.append(item)

    # Filter OpenAI, TechCrunch, MIT Tech Review, and Hacker News to education-relevant articles only
    unique_items = [item for item in unique_items if is_education_relevant(item)]

    print(f"\nTotal unique items collected: {len(unique_items)}")
    with open("output.json", "w") as f:
        json.dump(unique_items, f, indent=2)
    print("Saved to output.json")

if __name__ == "__main__":
    main()
