# ASU Faculty Data

## Overview
This repository contains data related to ASU faculty profiles. The full details of each faculty member are stored in the `.json` files within the repository. Additionally, a Python script (`asu_faculty.py`) is included to scrape faculty profile data automatically.

## License
There is **no license** associated with this repository. All copyright and trademark belong to [Arizona State University (ASU)](https://asu.edu).

## How to Use

### Clone the repository:
```bash
git clone https://github.com/canmi21/ASU-Faculty.git
```

### Navigate to the project directory:
```bash
cd ASU-Faculty
```

### Running the Scraper
The script `asu_faculty.py` scrapes ASU faculty profiles and saves them into a `.json` file.

#### Install dependencies:
Using pip:
```bash
pip install -r requirements.txt
```

Using uv:
```bash
uv pip install -r requirements.txt
```

#### Run the scraper:
```bash
python asu_faculty.py
```

You'll be prompted to enter:
- **Start page**: The page number to start scraping from.
- **Number of pages**: Total number of pages to scrape.
- **Number of threads**: Number of worker threads to use.

The scraped data will be saved in `asu_profiles.json`.

## Pre-Scraped Data
A dataset from **2025-03-24** has already been collected and is available in `asu_profiles.json`.

## More Information
You can access the origin for the faculty directory [here](https://search.asu.edu/view/directory-profiles).
