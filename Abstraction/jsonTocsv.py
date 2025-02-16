import json
import pandas as pd

def json_to_csv(json_file, csv_file):
    with open(json_file, 'r', encoding='utf-8') as f:  # Specify encoding
        data = json.load(f)
    
    df = pd.DataFrame(data)
    df.to_csv(csv_file, index=False, encoding='utf-8')  # Ensure CSV uses UTF-8
    print(f"CSV file saved as {csv_file}")

# Example usage
json_to_csv('scholar_results.json', 'output.csv')
