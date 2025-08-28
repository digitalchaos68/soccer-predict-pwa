export default function LeagueSelector({ value, onChange }) {
  return (
    <div className="p-4 bg-gray-50 border-b">
      <label className="block text-sm font-medium mb-2">Select League</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full p-2 border rounded bg-white"
      >
        {['Premier League', 'La Liga', 'Serie A', 'Bundesliga'].map((league) => (
          <option key={league} value={league}>
            {league}
          </option>
        ))}
      </select>
    </div>
  );
}