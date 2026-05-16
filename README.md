# Player Performance Dashboard

This project builds a football player performance dashboard using Python, pandas, Plotly, seaborn, and KMeans clustering.

## To access:
http://192.168.1.133:8501/

## What it does

- Loads player stats from a CSV file
- Cleans numeric columns
- Creates per-90 metrics
- Clusters players by playing style using KMeans
- Visualizes player performance in a Streamlit dashboard
- Lets you filter by club and position
- Lets you download the clustered results

## Files

```text
player-performance-dashboard/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   └── sample_players.csv
└── src/
    ├── clean_cluster.py
    └── transfermarkt_scraper_template.py
```

## How to run it

### 1. Open the folder in VS Code

Download/unzip the project folder, then open it in VS Code.

### 2. Create a virtual environment

Windows PowerShell:

```bash
python -m venv venv
venv\Scripts\activate
```

Mac/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install libraries

```bash
pip install -r requirements.txt
```

### 4. Run the dashboard

```bash
streamlit run app.py
```

The dashboard should open in your browser.

## How to use your own Transfermarkt data

The safest workflow is:

1. Collect/export player data into a CSV.
2. Make sure it has these columns:

```text
Player, Club, Position, Age, Market_Value, Appearances, Minutes, Goals, Assists, Yellow_Cards, Red_Cards
```

3. Open the Streamlit app.
4. Upload your CSV using the sidebar.

## About the scraper template

`src/transfermarkt_scraper_template.py` is included as a starting point for pulling basic player stats from Transfermarkt squad and profile pages. The script can collect player links from a squad listing and then parse summary data such as age, position, market value, appearances, minutes, goals, and assists.

Transfermarkt HTML changes often and scraping may be restricted, so always check the site's robots.txt and terms before using it. For a school project, using an exported CSV or open structured dataset is usually easier and safer.

## How the clustering works

The app calculates:

- Goals per 90
- Assists per 90
- Goal contributions per 90
- Cards per 90
- Minutes per appearance

Then it scales the features and applies KMeans. The dashboard labels clusters as possible playing styles, such as:

- Goal-Scoring Forward
- Creative Playmaker
- High-Minute Starter
- Young Developing Player
- Balanced Contributor
