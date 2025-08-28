export default function MatchCard({ match, showActual = false }) {
  const resultColor = match.correct ? 'text-success' : 'text-danger';

  return (
    <div className="bg-white border rounded-lg p-4 mb-3 shadow-sm">
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm text-gray-600">{match.date}</span>
        <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
          {match.confidence}% Conf
        </span>
      </div>

      <div className="flex justify-between text-center mb-2">
        <div className="flex-1">
          <p className="font-semibold">{match.homeTeam}</p>
        </div>
        <div className="mx-2">vs</div>
        <div className="flex-1">
          <p className="font-semibold">{match.awayTeam}</p>
        </div>
      </div>

      <div className="text-center my-2 text-lg font-bold">
        {match.scorePred}
      </div>

      <div className="text-center text-sm text-gray-700">
        Prediction: <strong>{match.prediction}</strong>
      </div>

      {showActual && (
        <div className="mt-3 pt-3 border-t text-center">
          <p className="text-sm">
            <span className="font-semibold">Actual:</span> {match.scoreActual} ({match.actualResult})
          </p>
          <p className={`text-sm font-bold ${resultColor}`}>
            {match.correct ? '✅ Correct' : '❌ Incorrect'}
          </p>
        </div>
      )}
    </div>
  );
}