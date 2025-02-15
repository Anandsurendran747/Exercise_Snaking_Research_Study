import json

# Load data from JSON file
def load_json(filename):
    with open(filename, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

# Save cleaned data back to JSON
def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# Remove duplicates based on title field
def remove_duplicates(filename):
    data = load_json(filename)
    unique_titles = set()
    cleaned_data = []

    for entry in data:
        title = entry.get("title", "").strip().lower()
        if title and title not in unique_titles:
            unique_titles.add(title)
            cleaned_data.append(entry)

    save_json(filename, cleaned_data)
    print(f"✅ Removed duplicates! Updated data saved in {filename}")

# Run the function on your JSON file
remove_duplicates("test.json")
