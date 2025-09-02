# py/fetch_matches.py
import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from urllib.parse import quote

# ====================
# Load Environment Variables
# ====================
load_dotenv()

API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

# Validate config
if not all([API_KEY, SUPABASE_URL, SUPABASE_KEY]):
    raise ValueError("❌ Missing required environment variables in .env file")

# Use the base URL
SUPABASE_REST_URL = f"{SUPABASE_URL}/rest/v1"

HEADERS = {"X-Auth-Token": API_KEY}
SUPABASE_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

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
# Fetch Recent Match Results
# ====================
def fetch_recent_results():
    # Get matches from last 7 days
    today = datetime.now()
    from_date = (today - timedelta(days=7)).strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")

    url = f"https://api.football-data.org/v4/competitions/PL/matches?dateFrom={from_date}&dateTo={to_date}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        print("❌ Error fetching results:", response.text)
        return []

    data = response.json()
    results = []
    for match in data['matches']:
        if match['status'] == 'FINISHED':
            home_score = match['score']['fullTime']['home']
            away_score = match['score']['fullTime']['away']
            
            if home_score > away_score:
                result = "Home Win"
            elif home_score < away_score:
                result = "Away Win"
            else:
                result = "Draw"

            results.append({
                'home_team': normalize_team_name(match['homeTeam']['name']),
                'away_team': normalize_team_name(match['awayTeam']['name']),
                'date': match['utcDate'][:10],
                'actual_result': result,
                'score_actual': f"{home_score}-{away_score}"
            })
    
    print(f"✅ Fetched {len(results)} finished matches")
    return results

# ====================
# Update Predictions with Actual Results
# ====================
def update_predictions_with_results():
    results = fetch_recent_results()
    updated = 0

    for result in results:
        # URL-encode team names
        home_encoded = quote(result['home_team'])
        away_encoded = quote(result['away_team'])
        date_encoded = quote(result['date'])

        check_url = f"{SUPABASE_REST_URL}/predictions?home_team=eq.{home_encoded}&away_team=eq.{away_encoded}&date=eq.{date_encoded}"
        
        try:
            response = requests.get(check_url, headers=SUPABASE_HEADERS)
            if response.status_code == 200 and len(response.json()) > 0:
                record = response.json()[0]
                
                # Determine if prediction was correct
                correct = record['prediction'] == result['actual_result']
                
                # Update record
                update_url = f"{SUPABASE_REST_URL}/predictions?id=eq.{record['id']}"
                payload = {
                    "actual_result": result['actual_result'],
                    "score_actual": result['score_actual'],
                    "correct": correct,
                    "updated_at": datetime.now().isoformat()
                }
                
                patch_response = requests.patch(update_url, json=payload, headers=SUPABASE_HEADERS)
                if patch_response.status_code in [200, 204]:
                    print(f"✅ Updated: {result['home_team']} vs {result['away_team']} → {result['actual_result']} ({'✅ Correct' if correct else '❌ Wrong'})")
                    updated += 1
                else:
                    print(f"❌ Failed to update: {patch_response.text}")
            else:
                print(f"⚠️ No prediction found for {result['home_team']} vs {result['away_team']} on {result['date']}")
        except Exception as e:
            print(f"❌ Error updating {result['home_team']} vs {result['away_team']}: {e}")

    print(f"📊 Updated {updated} matches with actual results")

# ====================
# Main
# ====================
if __name__ == "__main__":
    print("📅 Fetching recent match results...")
    update_predictions_with_results()
    print("🚀 Prediction accuracy tracking complete!")