import json
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

SENDGRID_API_KEY = os.environ["SENDGRID_API_KEY"]
TO_EMAIL = os.environ["TO_EMAIL"]
FROM_EMAIL = os.environ["FROM_EMAIL"]

def build_email_html(data):
    last_updated = data.get("last_updated", "")
    themes = data.get("themes", {})

    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Georgia, serif; max-width: 700px; margin: 0 auto; padding: 20px; color: #222; }}
            h1 {{ font-size: 24px; border-bottom: 2px solid #222; padding-bottom: 10px; }}
            h2 {{ font-size: 18px; margin-top: 30px; background: #f5f5f5; padding: 8px 12px; }}
            .item {{ margin: 15px 0; padding-bottom: 15px; border-bottom: 1px solid #eee; }}
            .item a {{ font-size: 16px; font-weight: bold; color: #1a0dab; text-decoration: none; }}
            .meta {{ font-size: 12px; color: #666; margin: 4px 0; }}
            .description {{ font-size: 14px; margin-top: 5px; }}
            .empty {{ color: #999; font-style: italic; font-size: 14px; }}
        </style>
    </head>
    <body>
        <h1>🔬 Research Digest</h1>
        <p style="color:#666;">Updated: {last_updated}</p>
    """

    for theme, items in themes.items():
        html += f"<h2>{theme}</h2>"
        if not items:
            html += "<p class='empty'>No items this period.</p>"
        else:
            for item in items:
                title = item.get("title", "No title")
                url = item.get("url", "#")
                source = item.get("source", "")
                date = item.get("date", "")
                description = item.get("description", "")
                # Strip any HTML tags from description
                import re
                description = re.sub(r'<[^>]+>', '', description)[:250]
                html += f"""
                <div class="item">
                    <a href="{url}" target="_blank">{title}</a>
                    <div class="meta">{source} &bull; {date}</div>
                    <div class="description">{description}</div>
                </div>
                """

    html += "</body></html>"
    return html

def main():
    with open("output.json", "r") as f:
        data = json.load(f)

    total_items = sum(len(v) for v in data.get("themes", {}).values())
    print(f"Building email with {total_items} items...")

    html_content = build_email_html(data)

    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=TO_EMAIL,
        subject=f"Research Digest — {data.get('last_updated', '')}",
        html_content=html_content
    )

    sg = SendGridAPIClient(SENDGRID_API_KEY)
    response = sg.send(message)
    print(f"Email sent! Status code: {response.status_code}")

if __name__ == "__main__":
    main()
