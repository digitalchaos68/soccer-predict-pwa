import { useEffect, useState } from 'react'
import MatchCard from '../components/MatchCard'
import { fetchPredictions } from '../data/fetchPredictions'

export default function Upcoming({ league }) {
  const [matches, setMatches] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      const { upcoming } = await fetchPredictions(league)
      setMatches(upcoming)
      setLoading(false)
    }
    load()
  }, [league])

  if (loading) return <p className="text-center py-4">Loading predictions...</p>

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold mb-4">Upcoming Predictions (Next 2 Weeks)</h2>
      {matches.length === 0 ? (
        <p className="text-gray-500 text-center py-4">No matches found.</p>
      ) : (
        matches.map((match) => (
          <MatchCard key={match.id} match={match} />
        ))
      )}
    </div>
  )
}