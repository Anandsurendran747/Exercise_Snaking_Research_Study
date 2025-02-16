import re
import json
import spacy

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

def clean_text(text):
    """
    Cleans the input text by:
    - Removing URLs, DOIs, and unwanted metadata.
    - Removing citations and figure references.
    - Filtering out irrelevant or short sentences.
    """
    if not text:
        return ""
    
    # Remove URLs, DOIs, and unwanted links
    text = re.sub(r"https?://\S+|www\.\S+|doi:\s*\S+", "", text, flags=re.I)
    text = re.sub(r"https?://\S+|www\.\S+|doi:\s*\S+|\b(?:ncbi|pubmed|sciencedirect|springer|nature|elsevier|arxiv|jstor)\.\S+", "", text, flags=re.I)


    # Process text with spaCy
    doc = nlp(text)
    cleaned_sentences = []
    
    # Keywords and patterns to remove metadata and irrelevant content
    metadata_keywords = [
        "Journal", "Volume", "Issue", "Citations", "Open Access",
        "Corresponding Author", "Search for more papers", "Department for Health",
        "orcid", "bath.ac.uk", "©", "Special Issue"
    ]
    citation_pattern = re.compile(r"\[\d+(,\s*\d+)*\]|\(\d+(,\s*\d+)*\)|Fig\.? \d+|Figure \d+", re.I)
    
    for sent in doc.sents:
        sentence = sent.text.strip()
        
        # Remove in-text citations, figure references
        sentence = citation_pattern.sub("", sentence)
        
        # Skip very short sentences or metadata-containing sentences
        if len(sentence) < 20 or any(keyword.lower() in sentence.lower() for keyword in metadata_keywords):
            continue
        
        cleaned_sentences.append(sentence)
    
    # Join cleaned sentences into a single cleaned text
    cleaned_text = " ".join(cleaned_sentences)
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()
    
    return cleaned_text

def process_json(input_file, output_file):
    """
    Reads a JSON file, cleans the scholar text data, and writes the cleaned version to a new file.
    """
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    cleaned_data = []
    for entry in data:
        # Ensure "full_abstract" exists
        if "full_abstract" in entry and "Full Text Content" in entry["full_abstract"]:
            cleaned_entry = entry.copy()
            raw_text = entry["full_abstract"]["Full Text Content"]
            cleaned_text_content = clean_text(raw_text)
            cleaned_entry["full_abstract"]["Cleaned Text Content"] = cleaned_text_content
            cleaned_data.append(cleaned_entry)
    
    # Save cleaned data
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Cleaned data saved to '{output_file}'")

if __name__ == "__main__":
    input_file = "../scholar_results.json"  # Update this to the correct path
    output_file = "scholar_results_clean.json"
    process_json(input_file, output_file)
