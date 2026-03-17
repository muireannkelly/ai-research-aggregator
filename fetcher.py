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
    "Computers & Education": "https://www.sciencedirect.com/journal/computers-and-education/rss/articles",
    "Education and Information Technologies": "https://link.springer.com/search.rss?facet-journal-id=10639&query=&search-within=Journal&facet-content-type=Article",
    "British Journal of Educational Technology": "https://bera-journals.onlinelibrary.wiley.com/feed/14678535/most-recent",
    "Int. Journal of Educational Technology in Higher Education": "https://link.springer.com/search.rss?facet-journal-id=41239&query=&search-within=Journal&facet-content-type=Article",

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
    "Dan
