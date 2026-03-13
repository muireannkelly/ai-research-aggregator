import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

THEMES = [
    "AI in Education & Learning",
    "Assessment & Credentialing",
    "Future of Work & Skills",
    "Higher Education Policy",
    "Learning Science & Design"
]

def group_items(items):
    if not items:
        print("No items to group")
        return {theme: [] for theme in THEMES}

    # Build a simple list of titles + descriptions for the prompt
    item_list = ""
    for i, item in enumerate(items):
        item_list += f"{i}. {item['title']} — {item['description'][:150]}\n"

    prompt = f"""You are a research assistant for a thought leadership team focused on AI, learning and assessment.
Here is a list of articles and papers, each with an index number:
{item_list}
Assign each item to exactly one of these themes:
{chr(10).join(THEMES)}
Important rules:
- "AI in Education & Learning" should ONLY contain items directly about AI or technology as it relates to teaching, learning, students or educational institutions. Do NOT include general AI or tech news unless it has a clear education angle.
- If an item does not clearly fit any theme, assign it to the closest match.
- Every item must be assigned to exactly one theme.
Return a JSON object where each key is a theme name and the value is a list of index numbers assigned to that theme.
Only return the JSON, nothing else."""

    print("Sending to OpenAI for grouping...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    raw = response.choices[0].message.content.strip()
    
    # Clean up response in case it has markdown code fences
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    theme_indices = json.loads(raw)

  # Build grouped output
    grouped = {theme: [] for theme in THEMES}
    assigned_indices = set()
    for theme, indices in theme_indices.items():
        for idx in indices:
            if 0 <= int(idx) < len(items):
                grouped[theme].append(items[int(idx)])
                assigned_indices.add(int(idx))
    
    # Catch any items that weren't assigned and put in best-fit theme
    unassigned = [i for i in range(len(items)) if i not in assigned_indices]
    if unassigned:
        print(f"Warning: {len(unassigned)} items unassigned, adding to AI in Education & Learning")
        for idx in unassigned:
            grouped["AI in Education & Learning"].append(items[idx])

    return grouped

def main():
    # Load fetched items
    with open("output.json", "r") as f:
        items = json.load(f)

    print(f"Loaded {len(items)} items from output.json")

    # Group them
    grouped = group_items(items)

    # Print summary
    for theme, theme_items in grouped.items():
        print(f"{theme}: {len(theme_items)} items")

    # Save grouped output
    output = {
        "last_updated": __import__("datetime").datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "themes": grouped
    }

    with open("output.json", "w") as f:
        json.dump(output, f, indent=2)

    print("\nGrouped output saved to output.json")

if __name__ == "__main__":
    main()
