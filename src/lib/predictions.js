import { supabase } from './supabaseClient';

// Normalize full name → short name
function normalizeTeamName(name) {
  const mapping = {
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
  };
  return mapping[name] || name;
}

export async function fetchPredictions() {
  const { data, error } = await supabase
    .from('predictions')
    .select('*')
    .order('date', { ascending: true });

  if (error) {
    console.error('Error fetching predictions:', error);
    return [];
  }

  return data.map(p => ({
    ...p,
    home_team: normalizeTeamName(p.home_team),
    away_team: normalizeTeamName(p.away_team),
    date: new Date(p.date).toLocaleDateString(),
    confidence: p.confidence || 0
  }));
}