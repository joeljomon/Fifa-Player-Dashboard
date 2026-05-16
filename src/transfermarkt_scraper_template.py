"""
Transfermarkt scraper template.

Important:
- Check Transfermarkt robots.txt and terms before scraping.
- Keep requests slow and small.
- For a class/demo project, using an exported CSV or open dataset is safer than heavy scraping.

This template can collect player links from a squad page and scrape basic summary stats from each
player profile. Transfermarkt HTML changes often, so adjust selectors if needed.
"""

import time
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


def parse_market_value(value_text: str) -> float:
    if not value_text:
        return 0.0

    value_text = value_text.strip().replace("€", "").replace("m", " million").replace("k", " thousand")
    value_text = value_text.replace("€", "").replace(".0", "")

    if "million" in value_text:
        return float(value_text.replace("million", "").strip()) * 1_000_000
    if "thousand" in value_text:
        return float(value_text.replace("thousand", "").strip()) * 1_000

    try:
        return float(value_text)
    except ValueError:
        return 0.0


def parse_int(text: str) -> int:
    if not text:
        return 0
    digits = re.findall(r"\d+", text.replace(".", ""))
    return int(digits[0]) if digits else 0


def scrape_player_links(url: str, delay_seconds: float = 3.0) -> pd.DataFrame:
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    time.sleep(delay_seconds)

    soup = BeautifulSoup(response.text, "lxml")
    rows = soup.select("table.items tbody tr")

    players = []
    for row in rows:
        link = row.select_one("a[href*='/profil/spieler/']")
        if not link:
            continue
        players.append({
            "Player": link.get_text(strip=True),
            "Profile_Link": "https://www.transfermarkt.com" + link.get("href", "")
        })

    return pd.DataFrame(players).drop_duplicates()


def scrape_player_profile(profile_url: str, delay_seconds: float = 2.0) -> dict:
    response = requests.get(profile_url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    time.sleep(delay_seconds)

    soup = BeautifulSoup(response.text, "lxml")
    data = {
        "Player": None,
        "Club": None,
        "Position": None,
        "Age": None,
        "Market_Value": None,
        "Appearances": None,
        "Minutes": None,
        "Goals": None,
        "Assists": None,
        "Yellow_Cards": 0,
        "Red_Cards": 0,
    }

    name_tag = soup.select_one("h1[data-testid='player-name'], h1.spielprofil-header__name, h1[itemprop='name']")
    if name_tag:
        data["Player"] = name_tag.get_text(strip=True)

    club_tag = soup.select_one("a[data-testid='player-header-team'], a.vereinprofil_tooltip")
    if club_tag:
        data["Club"] = club_tag.get_text(strip=True)

    position_tag = soup.select_one("div.dataZusatzDaten span[data-testid='position'], div.dataZusatzDaten:nth-of-type(1) span")
    if position_tag:
        data["Position"] = position_tag.get_text(strip=True)

    age_tag = soup.find(text=re.compile(r"Age|Age:", re.I))
    if age_tag:
        sibling = age_tag.parent.find_next_sibling("span") if age_tag.parent else None
        if sibling:
            data["Age"] = parse_int(sibling.get_text())

    value_tag = soup.select_one("div[data-testid='market-value'], div.market-value, a[data-testid='market-value']")
    if value_tag:
        data["Market_Value"] = parse_market_value(value_tag.get_text())

    # Find a performance table, if available.
    for label in ["Appearances", "Apps", "Minutes", "Goals", "Assists"]:
        cell = soup.find(text=re.compile(label, re.I))
        if cell and cell.parent:
            value = cell.parent.find_next_sibling(text=True)
            if value:
                if "Appearance" in label or "Apps" in label:
                    data["Appearances"] = parse_int(value)
                elif "Minutes" in label:
                    data["Minutes"] = parse_int(value)
                elif "Goals" in label:
                    data["Goals"] = parse_int(value)
                elif "Assists" in label:
                    data["Assists"] = parse_int(value)

    return data


def scrape_squad_stats(squad_url: str, sample_count: int = 10) -> pd.DataFrame:
    players = scrape_player_links(squad_url)
    results = []
    for _, row in players.head(sample_count).iterrows():
        profile_url = row["Profile_Link"]
        player_data = scrape_player_profile(profile_url)
        if player_data["Player"]:
            results.append(player_data)

    return pd.DataFrame(results)


if __name__ == "__main__":
    # Replace with a Transfermarkt club squad/listing URL you are allowed to access.
    url = "https://www.transfermarkt.com/fc-barcelona/startseite/verein/131"
    df = scrape_squad_stats(url, sample_count=10)
    df.to_csv("data/transfermarkt_players.csv", index=False)
    print(df.head())
