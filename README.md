# Web Scrapper 

A Python-based web scraping tool built with **BeautifulSoup4**. This project is specifically designed for **learning purposes**, focusing on understanding DOM parsing, HTTP requests, and data extraction techniques.

## Purpose
- Learning how to navigate the HTML tree using `bs4`.
- Managing project structure in Python.
- Handling local data storage and configuration.


## Tech Stack
* **Language:** Python 3.x
* **Core Library:** [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
* **Request Handling:** `requests`

## Project Structure
```text
webScrapper/
├── data/               # Scraped output files (CSV, JSON, etc.)
├── templates/          # HTML templates or structure guides
├── website_checker/    # Specific logic for site validation
├── main.py             # Entry point of the application
├── logics.py           # Core scraping algorithms
├── settings.py         # Configuration (URLs, Headers, Selectors)
├── utilities.py        # Helper functions
└── README.md           # Project documentation