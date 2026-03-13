import feedparser
import requests
import json
import ssl
import certifi
from datetime import datetime, timezone, timedelta

ssl_context = ssl.create_default_context(cafile=certifi.where())

FEEDS = {
    "EDUCAUSE Review": "https://er.educause.edu/rss",
    "EdSurge": "https://www.edsurge.com/feed",
    "Research in Learning Technology": "https://journal.alt.ac.uk/index.php/rlt/gateway/plugin/WebFeedGatewayPlugin/rss2",
    "The Guardian Education": "https://www.theguardian.com/education/rss",
    "Times Higher Education": "https://www.timeshighereducation.com/rss.xml",
    "TechCrunch": "https://techcrunch.com/feed/",
}

ARXIV_QUERIES = ["AI assessment", "machine learning education", "automated grading"]
CUTOFF = datetime.now(timezone.utc) - timedelta(days=7)

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
            print(f"{source}: error — {e}")
    return items

def fetch_arxiv():
    items = []
    for query in ARXIV_QUERIES:
        try:
            url = f"https://export.arxiv.org/api/query?search_query=all:{query.replace(' ', '+')}&sortBy=submittedDate&sortOrder=descending&max_results=10"
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
            print(f"arXiv ({query}): {count} items found")
        except Exception as e:
            print(f"arXiv ({query}): error — {e}")
    return items

def main():
    all_items = fetch_rss() + fetch_arxiv()
    print(f"\nTotal items collected: {len(all_items)}")
    with open("output.json", "w") as f:
        json.dump(all_items, f, indent=2)
    print("Saved to output.json")

if __name__ == "__main__":
    main()
