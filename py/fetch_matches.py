
import requests
from datetime import datetime, timedelta
import time

import json

from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()

# Now get the keys securely
API_KEY = os.getenv("API_FOOTBALL_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

# === CONFIG ===
API_URL = "https://v3.football.api-sports.io"
SUPABASE_TABLE = "predictions"

print("API Key:", API_KEY)  # Should show your key
print("Supabase URL:", SUPABASE_URL)

HEADERS = {
    "x-apisports-key": API_KEY
}

SUPABASE_HEADERS = {
    "apikey": SUPABASE_ANON_KEY,
    "Content-Type": "application/json",
    "Authorization": f"Bearer {SUPABASE_ANON_KEY}"
}

# Premier League ID
LEAGUES = {
    "Premier League": 39,
    "La Liga": 140,
    "Serie A": 135,
    "Bundesliga": 78,
    "Ligue 1": 61
}

# ====================
# Fetch matches from API-Football
# ====================
def fetch_upcoming_matches(league_id, days=14):
    endpoint = "/fixtures"

    # Use fixed date in 2023 (since free tier only allows 2021–2023)
    today = datetime(2023, 3, 20)  # Hardcoded to March 2023
    end_date = today + timedelta(days=14)

    params = {
        "league": league_id,
        "season": 2023,
        "from": today.strftime("%Y-%m-%d"),
        "to": end_date.strftime("%Y-%m-%d")
    }

    print(f"Fetching matches for league {league_id}, season 2023...")

    response = requests.get(f"{API_URL}{endpoint}", headers=HEADERS, params=params)

    if response.status_code != 200:
        print(f"❌ API Error {response.status_code}: {response.text}")
        return []

    data = response.json()

    if 'response' not in data:
        print("⚠️ No 'response' in data:", data)
        return []

    matches = []
    for fixture in data['response']:
        match = {
            "home_team": fixture['teams']['home']['name'],
            "away_team": fixture['teams']['away']['name'],
            "date": fixture['fixture']['date'][:10],
            "league": next(name for name, id in LEAGUES.items() if id == league_id)
        }
        matches.append(match)

    print(f"✅ Fetched {len(matches)} matches for league {league_id}")
    return matches

# ====================
# Upload to Supabase
# ====================
def upsert_predictions(matches):
    url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"
    
    for match in matches:
        # Only generate AI prediction if needed (optional)
        confidence = 60 + (hash(match['home_team']) % 20)
        prediction = "Home Win" if hash(match['home_team']) % 3 == 0 else \
                    "Away Win" if hash(match['home_team']) % 3 == 1 else "Draw"
        score_pred = "2-1" if prediction == "Home Win" else "1-2" if prediction == "Away Win" else "1-1"

        payload = {
            "league": match["league"],
            "home_team": match["home_team"],
            "away_team": match["away_team"],
            "date": match["date"],
            "prediction": prediction,
            "score_pred": score_pred,
            "confidence": confidence,
            "actual_result": match.get("actual_result"),   # ✅ Fixed
            "score_actual": match.get("score_actual"),     # ✅ Fixed
            "correct": match.get("correct")
        }

        # Check if match already exists
        existing = requests.get(
            url,
            headers=SUPABASE_HEADERS,
            params={
                "league": "eq." + match["league"],
                "home_team": "eq." + match["home_team"],
                "away_team": "eq." + match["away_team"],
                "date": "eq." + match["date"]
            }
        )

        if existing.status_code == 200 and len(existing.json()) == 0:
            # Insert new match
            response = requests.post(url, headers=SUPABASE_HEADERS, json=payload)
            if response.status_code in [200, 201]:
                print(f"✅ Added: {match['home_team']} vs {match['away_team']} ({match['date']})")
            else:
                print(f"❌ Failed to add {match['home_team']} vs {match['away_team']}: {response.text}")
        else:
            print(f"🔁 Already exists: {match['home_team']} vs {match['away_team']}")



# Add this function to fetch_matches.py
def delete_all_matches():
    url = f"{SUPABASE_URL}/rest/v1/predictions"
    response = requests.delete(url, headers=SUPABASE_HEADERS)
    print("🗑️ Deleted all matches:", response.status_code)



def fetch_historical_matches(league_id):
    # Only process Premier League (39)
    if league_id != 39:
        print(f"Skipping league {league_id}")
        return []

    try:
        with open('2023_epl_fixtures.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ File 'data/2023_epl_fixtures.json' not found")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return []

    if 'response' not in data:
        print("⚠️ No 'response' in data")
        return []

    matches = []
    for fixture in data['response']:
        # Skip if no goals data
        if 'goals' not in fixture or fixture['goals']['home'] is None:
            continue

        home_goals = fixture['goals']['home']
        away_goals = fixture['goals']['away']

        # Determine actual result
        if home_goals > away_goals:
            actual_result = "Home Win"
        elif home_goals < away_goals:
            actual_result = "Away Win"
        else:
            actual_result = "Draw"

        match = {
            "league": "Premier League",
            "home_team": fixture['teams']['home']['name'],
            "away_team": fixture['teams']['away']['name'],
            "date": fixture['fixture']['date'][:10],
            "prediction": "TBD",
            "score_pred": "1-1",
            "confidence": 50,
            "actual_result": actual_result,
            "score_actual": f"{home_goals}-{away_goals}",
            "correct": None
        }
        matches.append(match)

    print(f"✅ Loaded {len(matches)} matches from local file")
    return matches

# ====================
# Main
# ====================
def main():
# Call it before upserting
    delete_all_matches()

    all_matches = []
    for league_name, league_id in LEAGUES.items():
        time.sleep(1)
        matches = fetch_historical_matches(league_id)  # Uses local file
        all_matches.extend(matches)


    upsert_predictions(all_matches)
    print(f"\n✅ Total matches processed: {len(all_matches)}")

if __name__ == "__main__":
    main()