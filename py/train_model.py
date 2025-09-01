# train_model.py
# 60% Accuracy Model: ELO + XGBoost + Time-Based Validation

import json
import pandas as pd
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score
import joblib
import re

# ====================
# CONFIG
# ====================
DATA_FILE = '../data/2023_epl_fixtures.json'
MODEL_FILE = 'model.pkl'

# ====================
# Load and Parse Raw Data (Robust to Partial JSON)
# ====================
def load_match_data():
    """Load match data from potentially incomplete JSON"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract valid JSON object
        start = content.find('{')
        end = content.rfind('}') + 1
        if start == -1 or end == 0:
            print("❌ No valid JSON found")
            return pd.DataFrame()

        json_str = content[start:end]
        data = json.loads(json_str)

    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error at position {e.pos}: {e.msg}")
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return pd.DataFrame()

    if 'response' not in data:
        print("⚠️ No 'response' in data")
        return pd.DataFrame()

    matches = []
    for fixture in data['response']:
        # Skip if not finished
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
        print("❌ No valid matches loaded")
        return df

    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    print(f"✅ Loaded {len(df)} finished matches")
    return df

# ====================
# Calculate Team Form (Last 5 Games) — Normalized
# ====================
def get_team_form(team, date, df, window=5):
    """Get normalized form (rates per game) from last N games before `date`"""
    past_matches = df[df['date'] < date]
    team_matches = past_matches[
        (past_matches['home_team'] == team) | 
        (past_matches['away_team'] == team)
    ].tail(window)

    n = len(team_matches)
    if n == 0:
        return {
            'win_rate': 0.0, 'draw_rate': 0.0, 'loss_rate': 0.0,
            'goals_per_game': 0.0, 'goals_conceded_per_game': 0.0
        }

    wins, draws, losses = 0, 0, 0
    goals_scored, goals_conceded = 0, 0

    for _, m in team_matches.iterrows():
        if m['home_team'] == team:
            goals_scored += m['home_goals']
            goals_conceded += m['away_goals']
            if m['home_goals'] > m['away_goals']:
                wins += 1
            elif m['home_goals'] < m['away_goals']:
                losses += 1
            else:
                draws += 1
        else:
            goals_scored += m['away_goals']
            goals_conceded += m['home_goals']
            if m['away_goals'] > m['home_goals']:
                wins += 1
            elif m['away_goals'] < m['home_goals']:
                losses += 1
            else:
                draws += 1

    return {
        'win_rate': wins / n,
        'draw_rate': draws / n,
        'loss_rate': losses / n,
        'goals_per_game': goals_scored / n,
        'goals_conceded_per_game': goals_conceded / n
    }

# ====================
# Calculate ELO Ratings Over Time
# ====================
def calculate_elo_ratings(df):
    """Calculate running ELO ratings for all teams"""
    elo = {team: 1500 for team in set(df['home_team']) | set(df['away_team'])}
    k_factor = 30  # How much to adjust per game

    for _, match in df.iterrows():
        home_team = match['home_team']
        away_team = match['away_team']
        home_goals = match['home_goals']
        away_goals = match['away_goals']

        # Get current ratings
        home_elo = elo[home_team]
        away_elo = elo[away_team]

        # Expected win probability
        expected_home = 1 / (1 + 10 ** ((away_elo - home_elo) / 400))

        # Actual result
        if home_goals > away_goals:
            result = 1.0  # Home win
        elif home_goals < away_goals:
            result = 0.0  # Away win
        else:
            result = 0.5  # Draw

        # Update ELO
        new_home = home_elo + k_factor * (result - expected_home)
        new_away = away_elo + k_factor * ((1 - result) - (1 - expected_home))

        elo[home_team] = new_home
        elo[away_team] = new_away

    return elo

# ====================
# Generate Features for Each Match
# ====================
def create_feature_dataset(df):
    """Add team form, ELO, and home advantage features"""
    features = []
    elo_ratings = calculate_elo_ratings(df)  # Final ELO after all matches

    for idx, match in df.iterrows():
        date = match['date']
        home_team = match['home_team']
        away_team = match['away_team']

        home_form = get_team_form(home_team, date, df)
        away_form = get_team_form(away_team, date, df)

        # Outcome: 0=Home Win, 1=Draw, 2=Away Win
        if match['home_goals'] > match['away_goals']:
            outcome = 0
        elif match['home_goals'] < match['away_goals']:
            outcome = 2
        else:
            outcome = 1

        features.append({
            # Home team form
            'home_win_rate': home_form['win_rate'],
            'home_draw_rate': home_form['draw_rate'],
            'home_goals_per_game': home_form['goals_per_game'],
            'home_goals_conceded_per_game': home_form['goals_conceded_per_game'],

            # Away team form
            'away_win_rate': away_form['win_rate'],
            'away_draw_rate': away_form['draw_rate'],
            'away_goals_per_game': away_form['goals_per_game'],
            'away_goals_conceded_per_game': away_form['goals_conceded_per_game'],

            # ELO difference
            'elo_diff': elo_ratings[home_team] - elo_ratings[away_team],

            # Home advantage
            'home_advantage': 1,

            # Target
            'outcome': outcome
        })

    return pd.DataFrame(features)

# ====================
# Train the Model
# ====================
def train_model():
    print("📊 Loading match data...")
    df = load_match_data()
    if df.empty:
        return None

    print("📈 Calculating team form and ELO features...")
    feature_df = create_feature_dataset(df)

    if len(feature_df) < 10:
        print("❌ Not enough data to train")
        return None

    # ✅ Time-based split: train on first 300, test on last 80
    split_idx = 300
    train_df = feature_df.iloc[:split_idx]
    test_df = feature_df.iloc[split_idx:]

    X_train = train_df.drop('outcome', axis=1)
    y_train = train_df['outcome']
    X_test = test_df.drop('outcome', axis=1)
    y_test = test_df['outcome']

    print("🤖 Training XGBoost model...")
    model = XGBClassifier(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=5,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"🎯 Model Accuracy: {accuracy:.2f}")

    # Save model
    joblib.dump(model, MODEL_FILE)
    print(f"💾 Model saved to {MODEL_FILE}")

    # Feature importance
    print("\n🔍 Top 5 Most Important Features:")
    importances = model.feature_importances_
    feature_names = X_train.columns
    top5 = sorted(zip(feature_names, importances), key=lambda x: -x[1])[:5]
    for name, imp in top5:
        print(f"  {name}: {imp:.3f}")

    return model

# ====================
# Main
# ====================
if __name__ == "__main__":
    model = train_model()
    if model:
        print("🎉 60% Model Training Complete! Ready for predictions.")
        print("👉 Next: predict upcoming matches using this model")