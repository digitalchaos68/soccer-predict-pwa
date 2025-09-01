# calculate_form.py
import json
import pandas as pd

DATA_FILE = '../data/2023_epl_fixtures.json'
FORM_FILE = '../data/team_form_2023.json'

def load_match_data():
    """Load and parse match data"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        start = content.find('{')
        end = content.rfind('}') + 1
        if start == -1 or end == 0:
            print("❌ No valid JSON found")
            return pd.DataFrame()
        data = json.loads(content[start:end])
    except Exception as e:
        print(f"❌ Error loading JSON: {e}")
        return pd.DataFrame()

    if 'response' not in data:
        return pd.DataFrame()

    matches = []
    for fixture in data['response']:
        status = fixture.get('fixture', {}).get('status', {}).get('long')
        if status != "Match Finished":
            continue
        goals = fixture.get('goals', {})
        home_goals = goals.get('home')
        away_goals = goals.get('away')
        if home_goals is None or away_goals is None:
            continue

        matches.append({
            'date': fixture['fixture']['date'],
            'home_team': fixture['teams']['home']['name'],
            'away_team': fixture['teams']['away']['name'],
            'home_goals': home_goals,
            'away_goals': away_goals
        })

    df = pd.DataFrame(matches)
    if df.empty:
        return df
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    print(f"✅ Loaded {len(df)} finished matches")
    return df

def calculate_team_form(df):
    """Calculate form with goals per game"""
    form = {}

    for _, match in df.iterrows():
        home_team = match['home_team']
        away_team = match['away_team']

        # Initialize
        if home_team not in form:
            form[home_team] = {
                'wins': 0, 'draws': 0, 'losses': 0,
                'goals_scored': 0, 'goals_conceded': 0
            }
        if away_team not in form:
            form[away_team] = {
                'wins': 0, 'draws': 0, 'losses': 0,
                'goals_scored': 0, 'goals_conceded': 0
            }

        # Update results
        if match['home_goals'] > match['away_goals']:
            form[home_team]['wins'] += 1
            form[away_team]['losses'] += 1
        elif match['home_goals'] < match['away_goals']:
            form[home_team]['losses'] += 1
            form[away_team]['wins'] += 1
        else:
            form[home_team]['draws'] += 1
            form[away_team]['draws'] += 1

        # Update goals
        form[home_team]['goals_scored'] += match['home_goals']
        form[home_team]['goals_conceded'] += match['away_goals']
        form[away_team]['goals_scored'] += match['away_goals']
        form[away_team]['goals_conceded'] += match['home_goals']

    # Add rates and averages
    for team in form:
        n = form[team]['wins'] + form[team]['draws'] + form[team]['losses']
        if n > 0:
            form[team]['win_rate'] = form[team]['wins'] / n
            form[team]['draw_rate'] = form[team]['draws'] / n
            form[team]['loss_rate'] = form[team]['losses'] / n
            form[team]['goals_per_game'] = form[team]['goals_scored'] / n
            form[team]['goals_conceded_per_game'] = form[team]['goals_conceded'] / n
        else:
            form[team]['win_rate'] = 0.0
            form[team]['draw_rate'] = 0.0
            form[team]['loss_rate'] = 0.0
            form[team]['goals_per_game'] = 0.0
            form[team]['goals_conceded_per_game'] = 0.0

    return form

if __name__ == "__main__":
    df = load_match_data()
    if df.empty:
        print("❌ No matches loaded")
        exit(1)

    form = calculate_team_form(df)
    with open(FORM_FILE, 'w') as f:
        json.dump(form, f, indent=2)
    print(f"✅ Saved team form to {FORM_FILE}")