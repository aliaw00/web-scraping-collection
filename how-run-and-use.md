# How to Run and Use Sub-Projects

This guide provides step-by-step instructions for running and utilizing the completed projects in the Web Scraping Collection.

---

## 📋 General Pre-requisites

Ensure you have a Python 3.8+ environment initialized. If you are using a virtual environment, activate it first:
```bash
# On Linux/macOS
source env/bin/activate

# On Windows
env\Scripts\activate
```

---

## 💰 1. Price Tracker & Alert System

Monitors target product pages, logs historical prices, and triggers notifications on price drops.

### ⚙️ Setup and Configuration
1. Navigate to the project folder:
   ```bash
   cd Price-Tracker
   ```
2. Configure your watch list in `products.json`:
   ```json
   [
       {
           "name": "Sony PlayStation 5",
           "target_price": 499.99,
           "url": "https://www.ebay.com/p/27052784228?iid=314644637511"
       }
   ]
   ```
3. *(Optional)* Create a `.env` file to customize settings:
   ```env
   CHECK_INTERVAL_MIN=60
   CHECK_INTERVAL_MAX=120
   DB_NAME=prices.db
   LOG_FILE=guardian.log
   ```

### 🚀 Running the Project
* **Single Scan Pass**: Run the tracker once to collect prices:
  ```bash
  python main.py
  ```
* **Continuous Monitoring Loop**: Run the tracker in a loop. It logs sleeps according to random bounds:
  ```bash
  python main.py --loop
  ```

### 🕹️ How to Use
* **Data Log**: Inspected prices are logged to a local SQLite database (`prices.db`) in the `price_history` table.
* **Alerts**: If a product price falls below its `target_price`, a desktop pop-up notification is triggered using Linux `notify-send`.

---

## 📊 2. Reddit Trend Miner

Extracts trending topics, score metrics, and raw posts from subreddits to analyze trends.

### ⚙️ Setup and Configuration
1. Navigate to the project folder:
   ```bash
   cd Reddit-Trend-Miner
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Generate Reddit API Credentials:
   * Go to [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps) (logged in).
   * Create an app of type **"script"**.
   * Take note of the **Client ID** (under "personal use script") and the **Client Secret**.
4. Create a `.env` file in the `Reddit-Trend-Miner` directory:
   ```env
   REDDIT_CLIENT_ID="YOUR_CLIENT_ID"
   REDDIT_CLIENT_SECRET="YOUR_CLIENT_SECRET"
   REDDIT_USER_AGENT="python:subreddit.trend.miner:v1.0 (by /u/YOUR_REDDIT_USERNAME)"
   ```

### 🚀 Running the Project
1. **Fetch and Load Data (ETL)**: Run the script to extract hot posts from target subreddits:
   ```bash
   python main.py
   ```
2. **Launch Dashboard Visualizer**: Run the Streamlit interface.
   
   *Note: By default, Streamlit is accessible to other devices on your local network. To restrict access strictly to your local machine (recommended for security), pass the `--server.address` flag:*
   ```bash
   streamlit run dashboard/app.py --server.address localhost
   ```

   * **To Shut Down/Suspend the Dashboard**: In the terminal where the dashboard is running, press `Ctrl + C` to terminate the process.

### 🕹️ How to Use
* **Filter Options**: Select specific subreddits (e.g. *r/Python*, *r/learnprogramming*) in the sidebar to dynamically filter the metrics.
* **Top Metrics**: View total posts, subreddits, and top scores.
* **Keyword Chart**: Examine the Plotly bar chart indicating most mentioned words in post titles.
* **Raw Table**: Search and sort the raw data table inside the Streamlit explorer.

---

## 📰 3. News Sentiment Analyzer

An automated RSS/Atom reader classifying global headlines into positive, neutral, or negative sentiment curves.

### ⚙️ Setup and Configuration
1. Navigate to the project folder:
   ```bash
   cd News-Sentiment-Analyzer
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. *(Optional)* Modify `config.py` to add or modify RSS/Atom feeds in `NEWS_SOURCES`.

### 🚀 Running the Project
1. **Initialize and Feed Database (ETL)**:
   ```bash
   python main.py
   ```
2. **Launch Web Dashboard**: Run the visual app locally.
   
   *Note: By default, Streamlit is accessible to other devices on your local network. To restrict access strictly to your local machine (recommended for security), pass the `--server.address` flag:*
   ```bash
   streamlit run dashboard/app.py --server.address localhost
   ```

   * **To Shut Down/Suspend the Dashboard**: In the terminal where the dashboard is running, press `Ctrl + C` to terminate the process.

### 🕹️ How to Use
* **Manual Synchronization**: Click the sidebar's **"Sync & Rescrape Latest News"** button to execute a live scraper pass.
* **KPI Metrics**: View total scraped articles, global average sentiment compound index, and counts for positive/negative headline classes.
* **Aesthetic Donut & Grouped Bar Charts**: Visualize overall polarity ratios and compare sentiment volumes between different news sources (e.g., BBC vs. NYT).
* **Sentiment Area Charts**: Track the fluctuations of news tone over time.
* **Vocabulary Extraction**: Identify key vocabularies driving positive or negative headlines.
* **Feed Explorer**: Search specific keywords or filter sentiment categories inside the interactive tabular list, using direct hyperlinks to target news pages.

---

## 🎓 4. University Course Aggregator

Consolidates course catalogs, syllabi, timings, and instructor data from multiple academic providers into a searchable local SQLite database.

### ⚙️ Setup and Configuration
1. Navigate to the project folder:
   ```bash
   cd University-Course-Aggregator
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy the configuration settings:
   ```bash
   cp .env.example .env
   ```

### 🚀 Running the Project
* **Live Scrape & Cache**: Run the scraper to pull course details matching your search query:
  * Running with Mock catalog (offline-first test):
    ```bash
    python main.py --query "computer science" --provider mock
    ```
  * Scrape from real-world online platforms (Coursera/Stanford XML/MIT OCW RSS):
    ```bash
    python main.py --query "data science" --provider coursera
    python main.py --query "machine learning" --provider all
    ```
* **Offline Query Database**: Search previously cached courses inside the local database:
  ```bash
  python main.py --query "programming" --search-db
  ```
* **Consolidated Data Export**: Save matching courses into JSON or CSV files:
  ```bash
  python main.py --query "Calculus" --provider mock --export json --output calculus_courses.json
  ```

### 🕹️ How to Use
* **Console Output**: Lists search results formatted with course codes, instructors, schedules, and description previews.
* **SQLite Cache**: Scraped courses are stored in `courses.db` inside the `courses` table to avoid repeating network requests.
* **Testing**: Run `python3 -m unittest tests/test_aggregator.py` to verify the codebase functions correctly.

