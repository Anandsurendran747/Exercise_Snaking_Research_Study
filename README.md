
# Google Scholar Scraper

This script fetches research paper details from Google Scholar based on a list of queries related to "exercise snacking". The results are saved in a JSON file.

## Dependencies

- Python 3.x
- `requests`
- `scholarly`
- `beautifulsoup4`
- `selenium`
- `webdriver_manager`
- `json`

Install the dependencies using pip:
```sh
pip install requests scholarly beautifulsoup4 selenium webdriver_manager
```

## Usage

1. Ensure you have all the dependencies installed.
2. Run the script:
```sh
python scholer.py
```

The script will:
- Fetch Google Scholar results for each query.
- Save the results in `scholar_results.json`.
- Cache HTML pages in the `html_cache` directory.

## Output

The results are saved in `scholar_results.json` in the following format:
```json
[
    {
        "title": "Exercise snacks: a novel strategy to improve cardiometabolic health",
        "author": ["H Islam", "MJ Gibala", "JP Little"],
        "publication_year": "2022",
        "abstract": "been validated for brief isolated bouts of vigorous exercise that typify exercise snacks...",
        "citation_count": 108,
        "link": "https://journals.lww.com/acsm-essr/fulltext/2022/01000/exercise_snacks__a_novel_strategy_to_improve.5.aspx/1000",
        "full_abstract": {
            "Title": "Exercise Snacks: A Novel Strategy to Improve Cardiometabolic Health",
            "Authors": "No Authors Found",
            "Abstract": "No Abstract Found",
            "DOI": "https://doi.org/10.1161%2FCIR.0000000000000461",
            "Keywords": "No Keywords Found"
        }
    },
    // ...more results...
]
```

## Notes

- The script uses Selenium to fetch and cache HTML content for detailed scraping.
- Ensure you have Chrome installed and the appropriate WebDriver for Selenium.
- The script includes a delay to prevent blocking by Google Scholar.

## License

This project is licensed under the MIT License.
````