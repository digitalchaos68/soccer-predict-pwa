export const mockPredictions = {
  'Premier League': {
    upcoming: [
      {
        id: 1,
        homeTeam: 'Manchester City',
        awayTeam: 'Arsenal',
        date: '2025-04-05',
        prediction: 'Draw',
        confidence: 62,
        scorePred: '2-2'
      },
      {
        id: 2,
        homeTeam: 'Liverpool',
        awayTeam: 'Chelsea',
        date: '2025-04-06',
        prediction: 'Home Win',
        confidence: 70,
        scorePred: '2-1'
      },
      {
        id: 3,
        homeTeam: 'Tottenham',
        awayTeam: 'Manchester United',
        date: '2025-04-07',
        prediction: 'Away Win',
        confidence: 58,
        scorePred: '1-2'
      },
    ],
    history: [
      {
        id: 101,
        homeTeam: 'Aston Villa',
        awayTeam: 'Fulham',
        date: '2025-03-22',
        prediction: 'Home Win',
        actualResult: 'Home Win',
        scorePred: '2-1',
        scoreActual: '2-1',
        correct: true
      },
      {
        id: 102,
        homeTeam: 'Newcastle',
        awayTeam: 'Brighton',
        date: '2025-03-23',
        prediction: 'Draw',
        actualResult: 'Away Win',
        scorePred: '1-1',
        scoreActual: '1-2',
        correct: false
      },
    ]
  }
};

// For future leagues
export const availableLeagues = ['Premier League', 'La Liga', 'Serie A', 'Bundesliga'];