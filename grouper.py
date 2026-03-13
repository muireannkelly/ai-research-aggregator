import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

THEMES = [
    "AI in Education & Learning",
    "Assessment & Credentialing",
    "Future of Work & Skills",
    "Higher Education Policy",
    "Learning Science & Design",
    "Skills & Workforce Development",
    "Research & Academic Papers",
    "Industry & Competitor News"
]

def group_items(items):
    if not items:
        print("No items to group")
        return {theme: [] for theme in THEMES}

    grouped = {theme: [] for theme in THEMES}

    # Process in batches of 30 to avoid OpenAI context limits
    batch_size = 30
    batches = [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
    print(f"Processing {len(items)} items in {len(batches)} batches...")

    for batch_num, batch in enumerate(batches):
        item_list = ""
        for i, item in enumerate(batch):
            item_list += f"{i}. {item['title']} — {item['description'][:150]}\n"

        prompt = f"""You are a research assistant for a thought leadership team focused on AI, learning and assessment.

Here is a list of articles and papers, each with an index number:

{item_list}

Assign EVERY item to exactly one of these themes:
{chr(10).join(THEMES)}

Important rules:
- "AI in Education & Learning" should ONLY contain items directly about AI or technology as it relates to teaching, learning, students or educational institutions. Do NOT include general AI or tech news unless it has a clear education angle.
- You MUST assign every single item. Do not skip any index numbers.
- If an item does not clearly fit any theme, assign it to the closest match.
- "AI in Education & Learning": ONLY articles about AI/technology directly related to teaching, learning, students or education. NOT general AI news.
- "Assessment & Credentialing": exams, grading, qualifications, credentials, badges, certification
- "Future of Work & Skills": careers, employment, workplace skills, economic trends, labour market
- "Higher Education Policy": universities, colleges, policy, funding, regulation, government
- "Learning Science & Design": pedagogy, curriculum, learning theory, instructional design, cognitive science
- "Skills & Workforce Development": upskilling, reskilling, training, professional development, bootcamps, learning & development, L&D
- "Research & Academic Papers": academic studies, papers, research findings, arXiv preprints
- "Industry & Competitor News": EdTech companies, product launches, OpenAI, Google, Khan Academy, Anthropic, McGraw Hill, Pearson competitors
- Every number from 0 to {len(batch)-1} MUST appear exactly once in your response.

Return a JSON object where each key is a theme name and the value is a list of index numbers assigned to that theme.
Only return the JSON, nothing else."""

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )

            raw = response.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            raw = raw.strip()

            theme_indices = json.loads(raw)

            assigned_in_batch = set()
            for theme, indices in theme_indices.items():
                if theme in grouped:
                    for idx in indices:
                        if 0 <= int(idx) < len(batch):
                            grouped[theme].append(batch[int(idx)])
                            assigned_in_batch.add(int(idx))

            # Catch any unassigned items in this batch
            unassigned = [i for i in range(len(batch)) if i not in assigned_in_batch]
            if unassigned:
                print(f"Batch {batch_num + 1}: {len(unassigned)} unassigned items added to closest theme")
                for idx in unassigned:
                    grouped["AI in Education & Learning"].append(batch[idx])

            print(f"Batch {batch_num + 1}/{len(batches)}: {len(batch)} items processed")

        except Exception as e:
            print(f"Batch {batch_num + 1} error: {e}")
            for item in batch:
                grouped["AI in Education & Learning"].append(item)

    return grouped

def main():
    with open("output.json", "r") as f:
        items = json.load(f)

    print(f"Loaded {len(items)} items from output.json")

    grouped = group_items(items)

    # Remove duplicates across themes — keep first occurrence only
    seen_urls = set()
    deduplicated = {theme: [] for theme in THEMES}
    total_kept = 0
    total_removed = 0

    for theme in THEMES:
        for item in grouped[theme]:
            url = item.get("url", "")
            if url not in seen_urls:
                seen_urls.add(url)
                deduplicated[theme].append(item)
                total_kept += 1
            else:
                total_removed += 1

    if total_removed > 0:
        print(f"Removed {total_removed} duplicate articles across themes")

    for theme, theme_items in deduplicated.items():
        print(f"{theme}: {len(theme_items)} items")

    output = {
        "last_updated": __import__("datetime").datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "themes": deduplicated
    }

    with open("output.json", "w") as f:
        json.dump(output, f, indent=2)

    print("\nGrouped output saved to output.json")

if __name__ == "__main__":
    main()
