import json
from transformers import pipeline, AutoTokenizer

# Initialize the summarization pipeline using Facebook's BART model on GPU (device=0)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device=0)
tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")

def chunk_text(text, max_tokens=1024):
    """
    Splits the text into chunks that are within the model's max token limit.
    Returns a tuple (list_of_chunks, list_of_token_counts).
    """
    tokens = tokenizer.encode(text, add_special_tokens=False)
    if len(tokens) <= max_tokens:
        return [text], [len(tokens)]
    
    chunks = []
    token_counts = []
    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i:i+max_tokens]
        chunk_str = tokenizer.decode(chunk_tokens, skip_special_tokens=True, clean_up_tokenization_spaces=True)
        chunks.append(chunk_str)
        token_counts.append(len(chunk_tokens))
    return chunks, token_counts

def simple_summary(text, num_sentences=2):
    """
    Fallback summary: simply returns the first few sentences.
    """
    import nltk
    from nltk.tokenize import sent_tokenize
    nltk.download("punkt", quiet=True)
    sentences = sent_tokenize(text)
    return " ".join(sentences[:num_sentences])

def generate_abstract(text, article_title=""):
    """
    Generates an abstract from the input text using the summarizer.
    Attempts to create a full-page summary by increasing the length.
    """
    full_tokens = tokenizer.encode(text, add_special_tokens=False)
    full_token_count = len(full_tokens)
    print(f"Article '{article_title}': full text token count = {full_token_count}")
    
    chunks, chunk_token_counts = chunk_text(text, max_tokens=1024)  # Keep chunk size large
    chunk_summaries = []
    MAX_CHUNKS = 5  # Limit the number of chunks processed

    for idx, chunk in enumerate(chunks[:MAX_CHUNKS]):
        try:
            token_ids = tokenizer.encode(chunk, add_special_tokens=False)
            token_count = len(token_ids)
            
            if token_count < 50:
                fallback = simple_summary(chunk, num_sentences=3)
                print(f"Article '{article_title}', Chunk {idx+1}: Token count too low ({token_count}). Using fallback summary.")
                chunk_summaries.append(fallback)
                continue

            # Increase the summary length
            summary_out = summarizer(chunk, max_length=800, min_length=400, do_sample=False)
            summary = summary_out[0]['summary_text']
            chunk_summaries.append(summary.strip())
        except Exception as e:
            print(f"Error summarizing chunk {idx+1} for '{article_title}': {e}. Using fallback for this chunk.")
            chunk_summaries.append(simple_summary(chunk, num_sentences=3))

    # Combine chunk summaries and summarize again for a more detailed final summary
    combined_text = " ".join(chunk_summaries)
    try:
        combined_tokens = tokenizer.encode(combined_text, add_special_tokens=False)
        combined_token_count = len(combined_tokens)
        print(f"Article '{article_title}': combined summary token count = {combined_token_count}")

        # Increase final summary size
        final_summary_out = summarizer(combined_text, max_length=1000, min_length=500, do_sample=False)
        final_summary = final_summary_out[0]['summary_text']
        return final_summary.strip()
    except Exception as e:
        print(f"Error summarizing combined text for '{article_title}': {e}. Using fallback for combined summary.")
        return simple_summary(combined_text, num_sentences=50)


# File paths
input_file = "scholar_results_clean.json"   # Your input JSON file
output_file = "abstracts_gpu.json"          # File to store generated abstracts

# Load the scholar results JSON file
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

results = []
for entry in data:
    title = entry.get("title", "No Title")
    full_text = entry.get("full_abstract", {}).get("Full Text Content", "")
    
    if full_text:
        try:
            abstract = generate_abstract(full_text, article_title=title)
        except Exception as e:
            print(f"Error summarizing text for '{title}': {e}")
            abstract = "Error generating abstract."
    else:
        abstract = "No content available for summarization."
    
    results.append({
        "title": title,
        "abstract": abstract
    })
    print(f"Processed: {title}")

# Save the results into a single JSON file
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4, ensure_ascii=False)

print(f"\nAbstracts saved in {output_file}")
