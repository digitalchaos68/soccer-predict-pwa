import { supabase } from '../lib/supabaseClient'

export async function fetchPredictions(league = 'Premier League') {
  try {
    const { data, error } = await supabase
      .from('predictions')
      .select('*')
      .eq('league', league)
      .order('date', { ascending: true })

    if (error) {
      console.error('Supabase error:', error)
      return { upcoming: [], history: [] }
    }

    // Split into upcoming and history
    const today = new Date().toISOString().split('T')[0]
    const upcoming = data.filter(match => match.date >= today)
    const history = data.filter(match => match.date < today)

    return { upcoming, history }
  } catch (err) {
    console.error('Fetch error:', err)
    return { upcoming: [], history: [] }
  }
}