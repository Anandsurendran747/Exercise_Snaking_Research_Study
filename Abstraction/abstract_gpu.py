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
    Splits text into chunks, summarizes each, and combines them.
    Logs token counts and uses fallback if any error occurs.
    """
    # Get token count for the full text
    full_tokens = tokenizer.encode(text, add_special_tokens=False)
    full_token_count = len(full_tokens)
    print(f"Article '{article_title}': full text token count = {full_token_count}")
    
    # Split text into chunks and get token counts for each
    chunks, chunk_token_counts = chunk_text(text, max_tokens=512)
    for idx, count in enumerate(chunk_token_counts):
        print(f"Article '{article_title}': Chunk {idx+1} token count = {count}")

    chunk_summaries = []
    MAX_CHUNKS = 5 
    for idx, chunk in enumerate(chunks[:MAX_CHUNKS]):
        try:
            token_ids = tokenizer.encode(chunk, add_special_tokens=False)
            token_count = len(token_ids)
            
            # If the chunk is too short, use fallback
            if token_count < 50:
                fallback = simple_summary(chunk, num_sentences=1)
                print(f"Article '{article_title}', Chunk {idx+1}: Token count too low ({token_count}). Using fallback summary.")
                chunk_summaries.append(fallback)
                continue

            # Dynamically set parameters based on token count
            effective_max_length = 400 if token_count > 400 else token_count - 1
            effective_min_length = 150 if effective_max_length > 150 else max(80, effective_max_length - 1)

            print(f"Article '{article_title}', Chunk {idx+1}: token_count={token_count}, effective_max_length={effective_max_length}, effective_min_length={effective_min_length}")

            summary_out = summarizer(chunk, max_length=effective_max_length, min_length=effective_min_length, do_sample=False)
            summary = summary_out[0]['summary_text']
            chunk_summaries.append(summary.strip())
        except Exception as e:
            print(f"Error summarizing chunk {idx+1} for '{article_title}': {e}. Using fallback for this chunk.")
            chunk_summaries.append(simple_summary(chunk, num_sentences=1))

    # Combine chunk summaries if more than one exists
    if len(chunk_summaries) > 1:
        combined_text = " ".join(chunk_summaries)
        try:
            combined_tokens = tokenizer.encode(combined_text, add_special_tokens=False)
            combined_token_count = len(combined_tokens)
            print(f"Article '{article_title}': combined summary token count = {combined_token_count}")
            final_max_length = 150 if combined_token_count > 150 else combined_token_count - 1
            final_min_length = 40 if final_max_length > 40 else max(10, final_max_length - 1)
            final_summary_out = summarizer(combined_text, max_length=final_max_length, min_length=final_min_length, do_sample=False)
            final_summary = final_summary_out[0]['summary_text']
            return final_summary.strip()
        except Exception as e:
            print(f"Error summarizing combined text for '{article_title}': {e}. Using fallback for combined summary.")
            return simple_summary(combined_text, num_sentences=2)
    else:
        return chunk_summaries[0]

# File paths
input_file = "../scholar_results.json"   # Your input JSON file
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
