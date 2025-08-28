import { useState } from 'react';
import Header from './components/Header';
import LeagueSelector from './components/LeagueSelector';
import Upcoming from './pages/Upcoming';
import History from './pages/History';
import Stats from './pages/Stats';
import { mockPredictions } from './data/mockData';

export default function App() {
  const [league, setLeague] = useState('Premier League');
  const [activeTab, setActiveTab] = useState('upcoming');

  const data = mockPredictions[league] || mockPredictions['Premier League'];

  // Calculate stats
  const correct = data.history.filter(m => m.correct).length;
  const incorrect = data.history.filter(m => !m.correct).length;
  const total = correct + incorrect;
  const accuracy = total > 0 ? Math.round((correct / total) * 100) : 0;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <Header league={league} setLeague={setLeague} />

      {/* League Selector */}
      <LeagueSelector value={league} onChange={setLeague} />

      {/* Tabs */}
      <div className="flex bg-white border-b">
        {[
          { id: 'upcoming', label: 'Upcoming' },
          { id: 'history', label: 'History' },
          { id: 'stats', label: 'Stats' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex-1 py-3 text-center font-medium ${
              activeTab === tab.id
                ? 'text-primary border-b-2 border-primary'
                : 'text-gray-600'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="pb-16 px-4 pt-2">
        {activeTab === 'upcoming' && <Upcoming matches={data.upcoming} />}
        {activeTab === 'history' && <History matches={data.history} />}
        {activeTab === 'stats' && <Stats correct={correct} incorrect={incorrect} accuracy={accuracy} />}
      </div>

      {/* Footer Hint */}
      <div className="fixed bottom-0 left-0 right-0 p-3 text-center text-xs text-gray-500 bg-white border-t">
        Add to Home Screen for best experience
      </div>
    </div>
  );
}