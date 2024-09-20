# vic-council-candidates-scraper

A webscraper that gets all Council candidates from the VEC and writes their details to a CSV.

## Getting the data

Data is available as CSV files in the [`data` directory](https://github.com/yimbymelbourne/vic-council-candidates-scraper/tree/main/data).

- candidates.csv: Contains all candidates for all councils in Victoria.
- MCC-candidates.csv: Contains all candidates for Melbourne City Council.
- MCC-leadership.csv: Contains all leadership candidates for Melbourne City Council.

## Running project

1. Set up the virtual environment & install dependencies using [poetry](https://python-poetry.org/).

```bash
poetry init
```

```bash
poetry install
```

2. Run the project

### Scraper

```bash
poetry run python scraper.py
```

### Keyword search

```bash
poetry run python keywords.py
```
