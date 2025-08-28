import MatchCard from '../components/MatchCard';

export default function Upcoming({ matches }) {
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold mb-4">Upcoming Predictions (Next 2 Weeks)</h2>
      {matches.length === 0 ? (
        <p className="text-gray-500 text-center py-4">No upcoming matches.</p>
      ) : (
        matches.map((match) => (
          <MatchCard key={match.id} match={match} />
        ))
      )}
    </div>
  );
}