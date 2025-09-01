# predict_upcoming.py
# Predicts upcoming matches using model.pkl and secure .env credentials

import json
import requests
import pandas as pd
import joblib
from datetime import datetime
import os
from dotenv import load_dotenv
from scipy.stats import poisson
import numpy as np

from urllib.parse import quote

# ====================
# Load Environment Variables
# ====================
load_dotenv()  # Load from .env file

# ====================
# CONFIG (from .env)
# ====================
API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
MODEL_FILE = 'model.pkl'

# Validate config
if not all([API_KEY, SUPABASE_URL, SUPABASE_KEY]):
    raise ValueError("❌ Missing required environment variables in .env file")

# Use the base URL from .env
SUPABASE_REST_URL = f"{SUPABASE_URL}/rest/v1"

HEADERS = {"X-Auth-Token": API_KEY}
SUPABASE_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# Load trained model
print("🧠 Loading AI model...")
model = joblib.load(MODEL_FILE)
print("🔍 SUPABASE_URL:", SUPABASE_URL)
print("🔍 SUPABASE_REST_URL:", SUPABASE_REST_URL)
# Load team form data
try:
    with open('../data/team_form_2023.json', 'r') as f:
        team_form_data = json.load(f)
    print("✅ Loaded team form data")
except FileNotFoundError:
    print("❌ File '../data/team_form_2023.json' not found. Run 'python calculate_form.py' first.")
    team_form_data = {}

def normalize_team_name(name):
    """Convert full API team name to short name used in team_form_2023.json"""
    mapping = {
        "Arsenal FC": "Arsenal",
        "Aston Villa FC": "Aston Villa",
        "AFC Bournemouth": "Bournemouth",
        "Brentford FC": "Brentford",
        "Brighton & Hove Albion FC": "Brighton",
        "Burnley FC": "Burnley",
        "Chelsea FC": "Chelsea",
        "Crystal Palace FC": "Crystal Palace",
        "Everton FC": "Everton",
        "Fulham FC": "Fulham",
        "Leeds United FC": "Leeds United",
        "Leicester City FC": "Leicester",
        "Liverpool FC": "Liverpool",
        "Luton Town FC": "Luton",
        "Manchester City FC": "Manchester City",
        "Manchester United FC": "Manchester United",
        "Newcastle United FC": "Newcastle",
        "Nottingham Forest FC": "Nottingham Forest",
        "Sheffield United FC": "Sheffield Utd",
        "Southampton FC": "Southampton",
        "Tottenham Hotspur FC": "Tottenham",
        "West Ham United FC": "West Ham",
        "Wolverhampton Wanderers FC": "Wolves",
        "Sunderland AFC": "Sunderland"
    }
    return mapping.get(name, name)


# ====================
# Fetch Upcoming Fixtures
# ====================
def fetch_upcoming_fixtures():
    url = "https://api.football-data.org/v4/competitions/PL/matches?status=SCHEDULED"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        print("❌ Error fetching fixtures:", response.text)
        return []

    data = response.json()
    matches = []
    for match in data['matches']:
        # Extract league name from API
        league_name = match['competition']['name']  # ← This is "Premier League"

        matches.append({
            'date': match['utcDate'],
            'home_team': match['homeTeam']['name'],
            'away_team': match['awayTeam']['name'],
            'league': league_name  # ✅ Use dynamic value
        })
    
    print(f"✅ Fetched {len(matches)} upcoming matches")
    return matches

# ====================
# Simulate Team Form & ELO for Prediction
# ====================
def get_team_strength(team_name):
    # Placeholder ELO ratings (in real app, update weekly)
    elo_ratings = {
        "Arsenal": 1620, "Manchester City": 1700, "Liverpool": 1650,
        "Aston Villa": 1580, "Newcastle": 1560, "Tottenham": 1590,
        "Chelsea": 1550, "Manchester United": 1520, "Fulham": 1510,
        "Brighton": 1540, "Crystal Palace": 1500, "Everton": 1490,
        "Nottingham Forest": 1505, "Brentford": 1530, "West Ham": 1515,
        "Wolves": 1500, "Bournemouth": 1480, "Sheffield Utd": 1450,
        "Luton": 1430, "Burnley": 1440
    }
    return elo_ratings.get(team_name, 1500)

def predict_match(home_team, away_team):
    print(f"\n🔍 Predicting: {home_team} vs {away_team}")

    # Normalize names
    home_key = normalize_team_name(home_team)
    away_key = normalize_team_name(away_team)

    # Get real form from saved data
    home_form = team_form.get(home_key, {
        'win_rate': 0.5, 'draw_rate': 0.2, 'loss_rate': 0.3,
        'goals_per_game': 1.4, 'goals_conceded_per_game': 1.3
    })
    away_form = team_form.get(away_key, {
        'win_rate': 0.5, 'draw_rate': 0.2, 'loss_rate': 0.3,
        'goals_per_game': 1.4, 'goals_conceded_per_game': 1.3
    })

    # Log form data
    print(f"  📊 {home_team} ({home_key}) form: {home_form['goals_per_game']:.2f} ⚽️, {home_form['goals_conceded_per_game']:.2f} 🛡️")
    print(f"  📊 {away_team} ({away_key}) form: {away_form['goals_per_game']:.2f} ⚽️, {away_form['goals_conceded_per_game']:.2f} 🛡️")

    # Estimate expected goals using form
    baseline_home = 1.3
    baseline_away = 1.1

    lambda_home = baseline_home * (home_form['goals_per_game'] / 1.4) * (away_form['goals_conceded_per_game'] / 1.3)
    lambda_away = baseline_away * (away_form['goals_per_game'] / 1.4) * (home_form['goals_conceded_per_game'] / 1.3)

    lambda_home = np.clip(lambda_home, 0.3, 4.0)
    lambda_away = np.clip(lambda_away, 0.3, 4.0)

    print(f"  🎯 λ_home: {lambda_home:.2f}, λ_away: {lambda_away:.2f}")

    # Build Poisson score matrix
    max_goals = 5
    home_probs = poisson.pmf(np.arange(0, max_goals + 1), lambda_home)
    away_probs = poisson.pmf(np.arange(0, max_goals + 1), lambda_away)
    score_matrix = np.outer(home_probs, away_probs)

    # Find most likely score
    best_home, best_away = np.unravel_index(score_matrix.argmax(), score_matrix.shape)
    score_pred = f"{int(best_home)}-{int(best_away)}"
    score_prob = score_matrix.max()

    # Total outcome probabilities
    p_home_win = np.sum(score_matrix * (np.arange(max_goals+1)[:, None] > np.arange(max_goals+1)))
    p_away_win = np.sum(score_matrix * (np.arange(max_goals+1)[:, None] < np.arange(max_goals+1)))
    p_draw = np.sum(score_matrix * (np.arange(max_goals+1)[:, None] == np.arange(max_goals+1)))

    outcome_confidence = max(p_home_win, p_away_win, p_draw)
    confidence = int(outcome_confidence * 100)

    # Predict outcome
    if best_home > best_away:
        prediction = "Home Win"
    elif best_home < best_away:
        prediction = "Away Win"
    else:
        prediction = "Draw"

    if home_key not in team_form:
        print(f"⚠️ Team not found: '{home_team}' → '{home_key}'")
    if away_key not in team_form:
        print(f"⚠️ Team not found: '{away_team}' → '{away_key}'")

    print(f"  📈 Outcome Prob: Home Win={p_home_win:.2f}, Draw={p_draw:.2f}, Away Win={p_away_win:.2f}")
    print(f"  🎯 Most Likely Score: {score_pred} (prob={score_prob:.2f})")
    print(f"  ✅ Final: {prediction} → {score_pred} ({confidence}%)")

    return prediction, confidence, score_pred

# ====================
# Upload Prediction to Supabase
# ====================
def upload_prediction(match, prediction, confidence, score_pred):
    url = f"{SUPABASE_REST_URL}/predictions"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }

    # Normalize team names BEFORE sending to Supabase
    home_team_norm = normalize_team_name(match['home_team'])
    away_team_norm = normalize_team_name(match['away_team'])

    payload = {
        "league": match['league'],
        "home_team": home_team_norm,  # ✅ Use normalized name
        "away_team": away_team_norm,  # ✅ Use normalized name
        "date": match['date'][:10],
        "prediction": prediction,
        "score_pred": score_pred,
        "confidence": confidence,
        "actual_result": None,
        "score_actual": None,
        "correct": None,
        "updated_at": datetime.now().isoformat()
    }

    # URL-encode for query
    home_team_encoded = quote(home_team_norm)
    away_team_encoded = quote(away_team_norm)
    date_encoded = quote(match['date'][:10])

    check_url = f"{SUPABASE_REST_URL}/predictions?home_team=eq.{home_team_encoded}&away_team=eq.{away_team_encoded}&date=eq.{date_encoded}"

    print(f"\n🔍 Predicting: {match['home_team']} vs {match['away_team']}")
    print(f"🌐 Check URL: {check_url}")
    print(f"📡 Headers: {dict(headers)}")
    print(f"🔑 API Key Length: {len(SUPABASE_KEY)}")
    print(f"📄 Payload: {payload}")

    try:
        response = requests.get(check_url, headers=headers, timeout=10)
        print(f"🔍 GET Response: {response.status_code}")
        print(f"📄 GET Body: {response.text}")

        if response.status_code == 200 and len(response.json()) > 0:
            record_id = response.json()[0]['id']
            update_url = f"{SUPABASE_REST_URL}/predictions?id=eq.{record_id}"
            print(f"✅ Record found: ID={record_id}")
            print(f"🌐 Update URL: {update_url}")

            response = requests.patch(update_url, json=payload, headers=headers, timeout=10)
            print(f"🔧 PATCH Response: {response.status_code}")
            print(f"📄 PATCH Body: {response.text}")
            action = "🔄 Updated"
        else:
            print("➡️  No record found. Creating new.")
            print(f"🌐 POST URL: {url}")
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            print(f"➕ POST Response: {response.status_code}")
            print(f"📄 POST Body: {response.text}")
            action = "➕ Created"

        if response.status_code in [200, 201, 204]:
            print(f"✅ {action}: {match['home_team']} vs {match['away_team']} → {prediction} ({confidence}%)")
        else:
            print(f"❌ Upload failed: {response.status_code} {response.text}")

    except Exception as e:
        print(f"❌ Request failed: {type(e).__name__}: {e}")

# ====================
# Main
# ====================
if __name__ == "__main__":

    # Load real team form
    with open('../data/team_form_2023.json', 'r') as f:
        team_form = json.load(f)

    print("📅 Fetching upcoming fixtures...")
    matches = fetch_upcoming_fixtures()
    
    for match in matches:
        pred, conf, score = predict_match(match['home_team'], match['away_team'])
        upload_prediction(match, pred, conf, score)
    
    print("🚀 Predictions uploaded! Check your PWA.")