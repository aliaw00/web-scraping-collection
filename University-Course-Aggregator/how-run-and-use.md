# University Course Aggregator

The **University Course Aggregator** is a performant, modular, and resilient Python command-line utility that fetches, parses, and consolidates course metadata, schedules, and syllabi from multiple academic institutions and online providers.

It saves consolidated data to a local SQLite database, allowing users to query, search, and export courses without hitting external endpoints repeatedly.

---

## 🚀 Key Features

*   **Modular Architecture**: Uses a provider pattern (`BaseCourseProvider`) allowing easy creation of scrapers for new universities.
*   **Multiple Source Integrations**:
    *   **Coursera API**: Connects to the public Coursera catalog API for online course listings.
    *   **Stanford ExploreCourses**: Scrapes active classroom courses using Stanford's public XML feed.
    *   **MIT OpenCourseWare (OCW)**: Parses the MIT OCW New Courses RSS XML feed with a fallback static HTML crawler.
    *   **Mock Provider**: Simulates a high-quality university catalog offline for local testing and CI/CD validation.
*   **Offline First / Database Caching**: Stores courses in a local SQLite database (`courses.db`) to enable fast local search and analysis.
*   **Consolidated Search & Queries**: Search across all scraped course descriptions, titles, syllabi, or course IDs.
*   **Multiple Export Formats**: Export collected course data into structured `JSON` or `CSV` files.
*   **Resilience & Performance**: Implements timeout configurations and retry logic to gracefully handle network issues and prevent hanging.

---

## 🛠️ Setup and Installation

### 1. Install Dependencies
Make sure you have active virtual environment and install dependencies:
```bash
cd University-Course-Aggregator
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` to customize settings:
```bash
cp .env.example .env
```
Inside `.env`, you can customize:
*   `DB_NAME`: The database filename (default: `courses.db`).
*   `LOG_LEVEL`: Logging verbosity (default: `INFO`).
*   `REQUEST_TIMEOUT`: Timeout for network connections (default: `10` seconds).
*   `MAX_RETRIES`: Number of retries for failed network queries (default: `3`).
*   `DEFAULT_QUERY`: Default search term (default: `computer science`).

**API Credentials Note**: The default providers (Coursera, Stanford XML, MIT OCW RSS) utilize public feeds and endpoints and **do not require any API keys or authentication**. All configurations are managed locally in the `.env` file.

---

## 🚀 Running and Usage

Execute the aggregator using `python main.py`.

### 1. Run Scrapers (Collect Course Data)
Run the aggregator to fetch courses from one or more providers and save them to the local database.

*   **Run with Mock Provider** (Default, recommended for quick tests/offline):
    ```bash
    python main.py --query "computer science" --provider mock
    ```
*   **Scrape a Specific Real Provider** (e.g. Coursera):
    ```bash
    python main.py --query "data science" --provider coursera
    ```
*   **Scrape Multiple Providers**:
    ```bash
    python main.py --query "physics" --provider coursera --provider stanford --provider mit_ocw
    ```
*   **Scrape All Real Providers** (excludes mock):
    ```bash
    python main.py --query "machine learning" --provider all
    ```

### 2. Query and Search Local Database (Offline Search)
Search the accumulated courses stored in your local database without making any external API requests.
```bash
python main.py --query "programming" --search-db
```

### 3. Export Data
Export consolidated courses to a `JSON` or `CSV` file using the `--export` and `--output` flags.

*   **Export from Live Scraping**:
    ```bash
    python main.py --query "calculus" --provider mock --export json --output courses_output.json
    ```
*   **Export from Local Database Search**:
    ```bash
    python main.py --query "CS" --search-db --export csv --output cs_courses.csv
    ```

### 4. Utility Options
*   **List Available Providers**:
    ```bash
    python main.py --list-providers
    ```
*   **Help Details**:
    ```bash
    python main.py --help
    ```

---

## 🧪 Running Tests

A comprehensive unit test suite is provided to verify database integration, configuration, mock data generation, and offline robustness.

To execute tests:
```bash
python3 -m unittest tests/test_aggregator.py
```
