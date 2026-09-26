# iDNES.cz article scraper and analysis

An older local Python project that collects links to iDNES.cz articles, extracts article data, and provides analysis, visualizations, and an optional MySQL import.

> This repository is an upload of a completed older project. The project was not originally tracked with Git, so its earlier development history is unavailable. The scripts reflect the original local setup; they have not been revalidated against the current website.

## Project files

| File | Purpose |
| --- | --- |
| `articlecolletor.py` | Collects article links by category and saves them to `article_links.json`. |
| `articleprocessor.py` | Reads those links, extracts titles, text, dates, image counts, and comment counts, and saves the results to `articles_data.json`. |
| `cleaner.py` | Removes records without article text and duplicate titles from `articles_data.json`. It overwrites the file. |
| `data_analyzer.py` | Prints statistics about the collected articles. |
| `data_visualizer.py` | Generates charts from the collected articles. |
| `uploadToSQL.py` | Optionally imports articles into MySQL. |
| `QueryDB.py` | Runs example SQL queries against the imported articles. |

## Requirements

- Python 3 and the packages listed in `requirements.txt`
- Google Chrome and a matching ChromeDriver for collecting articles
- MySQL only if you want to use `uploadToSQL.py` and `QueryDB.py`

Install the Python dependencies:

```bash
python -m pip install -r requirements.txt
```

Both scraping scripts contain Chrome and ChromeDriver paths from the original computer. Before running them, adjust `chrome_options.binary_location` and `chrome_driver_path` for your machine. `articleprocessor.py` also sets the `cs_CZ.UTF-8` locale. If your system does not support that locale name, change or remove that setting; the script already parses Czech month names using its own lookup table.

## Usage

Run the commands from the repository root because the scripts use relative paths for their data files.

1. Run `python articlecolletor.py` to create `article_links.json`.
2. Run `python articleprocessor.py` to process the links and create `articles_data.json`.
3. Optionally run `python cleaner.py`. Keep a copy of the original data first if you want to preserve it, because this step overwrites the JSON file.
4. Run `python data_analyzer.py` to print statistics.
5. Before running `python data_visualizer.py`, create the `graphs/data_vizualizer/` directory where it saves PNG charts.

`article_links.json` and `articles_data.json` are generated files and are not included in the repository. The scraper uses selectors from the original website; they may need updating if the page structure has changed.

## MySQL (optional)

The import requires your own database and an `articles` table with the columns `title`, `article_text`, `image_count`, `time_date`, `comments_count`, and `category`. Neither a database creation script nor the collected data is included in this repository.

Configure the connection in both `uploadToSQL.py` and `QueryDB.py` for your local MySQL installation. You can then run `python uploadToSQL.py` followed by `python QueryDB.py`. The import expects an existing `articles_data.json`.
