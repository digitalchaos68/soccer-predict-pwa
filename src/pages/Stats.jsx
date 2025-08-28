import StatsCard from '../components/StatsCard';

export default function Stats({ correct, incorrect, accuracy }) {
  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold">Prediction Performance</h2>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <StatsCard title="Correct" value={correct} color="success" />
        <StatsCard title="Incorrect" value={incorrect} color="danger" />
      </div>

      <StatsCard title="Accuracy Rate" value={`${accuracy}%`} color="primary" />

      <div className="mt-6 p-4 bg-gray-50 rounded">
        <h3 className="font-semibold mb-2">Recent Trends</h3>
        <ul className="text-sm text-gray-700 space-y-1">
          <li>✅ 3 correct home wins in a row</li>
          <li>❌ 2 missed draws last week</li>
        </ul>
      </div>
    </div>
  );
}