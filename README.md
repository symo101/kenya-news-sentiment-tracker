# 📰 Kenya News Sentiment Tracker

> NLP project — real Kenyan news headlines scraped from StandardMedia.co.ke, analysed for sentiment using TextBlob and deployed as a live interactive dashboard.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://kenya-news-sentiment-tracker.streamlit.app/)

🔗 **Live App:** [kenya-news-sentiment-tracker.streamlit.app](https://kenya-news-sentiment-tracker.streamlit.app/)

---

## 📸 Screenshots

![Overview](app_pic1.png)

![By Category](app_pic2.png)

![Headlines Table](app_pic3.png)

---

## 🎯 Project Overview

This project scrapes real headlines from **StandardMedia.co.ke** across 6 news categories, scores each headline's sentiment using **TextBlob NLP**, and visualises the results in an interactive Streamlit dashboard.

**Key Question:** *Is Kenyan news coverage mostly positive, negative or neutral — and which categories drive the most negative sentiment?*

---

## 🔄 Project Pipeline

```
SCRAPE  ──►  CLEAN  ──►  SENTIMENT  ──►  VISUALISE  ──►  DEPLOY
```

---

## 📁 Project Structure

```
kenya-news-sentiment-tracker/
│
├── app.py                      # Streamlit dashboard
├── standard_scraper.py         # Web scraper
├── sentiment_analysis.ipynb    # Cleaning + sentiment notebook
│
├── news_raw.csv                # Raw scraped headlines (214 rows)
├── news_clean.csv              # Cleaned + scored dataset (213 rows)
│
├── requirements.txt            # Python dependencies
└── README.md
```

---

## 🔍 Stage Breakdown

### 1️⃣ Web Scraping — `standard_scraper.py`
- Built with `requests` and `BeautifulSoup`
- Used Chrome DevTools to identify stable article link selectors
- Scraped 6 categories: Politics, Business, Health, Sports, World, Counties
- Fields collected: headline text, category, URL, scraped timestamp
- Output: `news_raw.csv` — **214 headlines**

### 2️⃣ Cleaning — `sentiment_analysis.ipynb`
- Removed extra whitespace and special characters
- Dropped duplicate and very short headlines
- Parsed timestamps into proper datetime format
- Output: `news_clean.csv` — **213 headlines, 0 missing values**

### 3️⃣ Sentiment Analysis — `sentiment_analysis.ipynb`
- Scored every headline using **TextBlob** polarity
- Polarity range: –1.0 (very negative) → 0.0 (neutral) → +1.0 (very positive)
- Labelled each headline as Positive / Neutral / Negative

| Threshold | Label |
|---|---|
| polarity > 0.1 | Positive |
| –0.1 to 0.1 | Neutral |
| polarity < –0.1 | Negative |

### 4️⃣ Streamlit Dashboard — `app.py`

| Feature | Description |
|---|---|
| 🎯 Live Scorer | Type any headline → instant polarity score + label |
| 📊 Overview tab | Sentiment distribution bar chart + polarity histogram |
| 📂 By Category tab | Mean polarity per category + stacked breakdown |
| ☁️ Word Clouds tab | Most common words — Positive / Neutral / Negative |
| 📋 Headlines Table | Colour-coded filterable table of all headlines |
| 🔍 Sidebar filters | Filter by category and sentiment |

---

## 📊 Key Findings

| Metric | Value |
|---|---|
| Total headlines analysed | 213 |
| Positive | 36 (17%) |
| Neutral | 150 (70%) |
| Negative | 27 (13%) |
| Mean polarity | 0.021 |
| Most negative category | **Politics** |
| Most positive category | **Sports** |
| Largest category | Business (61 headlines) |

1. **70% of Kenyan news headlines are neutral** — factual reporting dominates
2. **Politics is the most negative category** — consistent with political tension coverage
3. **Sports is the most positive** — wins and achievements drive positive tone
4. **Overall mean polarity is 0.021** — Kenyan news leans very slightly positive

---

## 🚀 Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/symo101/kenya-news-sentiment-tracker.git
cd kenya-news-sentiment-tracker

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download TextBlob language data
python -m textblob.download_corpora

# 4. Run the dashboard
streamlit run app.py
```

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| `requests` + `BeautifulSoup` | Web scraping |
| `pandas` + `numpy` | Data cleaning |
| `TextBlob` | NLP sentiment scoring |
| `matplotlib` + `seaborn` | Charts |
| `WordCloud` | Word cloud visualisation |
| `Streamlit` | Web app and deployment |

---

## 📦 Requirements

```
requests
beautifulsoup4
pandas
numpy
matplotlib
seaborn
textblob
wordcloud
streamlit==1.32.0
altair==5.2.0
```

---

## 👤 Author

**Simon**
- 🐙 GitHub: [github.com/symo101](https://github.com/symo101)
- 🔗 Live App: [kenya-news-sentiment-tracker.streamlit.app](https://kenya-news-sentiment-tracker.streamlit.app/)

---

*Data scraped from StandardMedia.co.ke in March 2026 for educational and portfolio purposes only.*
