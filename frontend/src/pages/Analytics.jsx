import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar, CartesianGrid } from 'recharts'

export default function Analytics() {
  const navigate = useNavigate()
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    axios.get('/api/interview/history')
      .then(r => setHistory(r.data.interviews.filter(i => i.overall_score != null)))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const chartData = history.slice().reverse().map((iv, i) => ({
    name: `#${i + 1}`,
    score: iv.overall_score,
    company: iv.company,
  }))

  const companyData = Object.entries(
    history.reduce((acc, iv) => {
      if (!acc[iv.company]) acc[iv.company] = { total: 0, count: 0 }
      acc[iv.company].total += iv.overall_score
      acc[iv.company].count++
      return acc
    }, {})
  ).map(([company, { total, count }]) => ({
    company,
    avg: Math.round((total / count) * 10) / 10,
  }))

  const avgScore = history.length
    ? Math.round((history.reduce((s, i) => s + i.overall_score, 0) / history.length) * 10) / 10
    : 0

  const best = history.length ? Math.max(...history.map(i => i.overall_score)) : 0
  const trend = history.length >= 2
    ? history[0].overall_score - history[history.length - 1].overall_score
    : 0

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <div className="border-b border-gray-800 px-6 py-4 flex items-center gap-4">
        <button onClick={() => navigate('/')} className="text-gray-400 hover:text-white transition text-sm">← Dashboard</button>
        <h1 className="text-lg font-semibold">📊 Analytics</h1>
      </div>

      <div className="max-w-4xl mx-auto px-6 py-10 space-y-8">
        {loading ? (
          <p className="text-gray-400">Loading...</p>
        ) : history.length === 0 ? (
          <div className="text-center py-20">
            <p className="text-gray-400 mb-4">No completed interviews yet.</p>
            <button onClick={() => navigate('/')} className="text-indigo-400 hover:text-indigo-300 text-sm">Start your first interview →</button>
          </div>
        ) : (
          <>
            {/* Stats row */}
            <div className="grid grid-cols-3 gap-4">
              {[
                { label: 'Total Interviews', value: history.length },
                { label: 'Avg Score', value: `${avgScore}/10` },
                { label: 'Best Score', value: `${best}/10` },
              ].map(s => (
                <div key={s.label} className="bg-gray-900 rounded-xl border border-gray-800 p-5 text-center">
                  <p className="text-2xl font-bold text-indigo-400">{s.value}</p>
                  <p className="text-gray-400 text-sm mt-1">{s.label}</p>
                </div>
              ))}
            </div>

            {/* Score over time */}
            <div className="bg-gray-900 rounded-2xl border border-gray-800 p-6">
              <h3 className="font-semibold mb-4">Score Over Time</h3>
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                  <XAxis dataKey="name" stroke="#6b7280" tick={{ fontSize: 12 }} />
                  <YAxis domain={[0, 10]} stroke="#6b7280" tick={{ fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{ background: '#111827', border: '1px solid #374151', borderRadius: 8 }}
                    labelStyle={{ color: '#fff' }}
                    itemStyle={{ color: '#818cf8' }}
                  />
                  <Line type="monotone" dataKey="score" stroke="#6366f1" strokeWidth={2} dot={{ fill: '#6366f1', r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
              {trend !== 0 && (
                <p className={`text-sm mt-2 ${trend > 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {trend > 0 ? `↑ Improved by ${trend.toFixed(1)} points overall` : `↓ Declined by ${Math.abs(trend).toFixed(1)} points — keep practicing!`}
                </p>
              )}
            </div>

            {/* Per company */}
            {companyData.length > 1 && (
              <div className="bg-gray-900 rounded-2xl border border-gray-800 p-6">
                <h3 className="font-semibold mb-4">Average Score by Company</h3>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={companyData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                    <XAxis dataKey="company" stroke="#6b7280" tick={{ fontSize: 12 }} />
                    <YAxis domain={[0, 10]} stroke="#6b7280" tick={{ fontSize: 12 }} />
                    <Tooltip
                      contentStyle={{ background: '#111827', border: '1px solid #374151', borderRadius: 8 }}
                      labelStyle={{ color: '#fff' }}
                      itemStyle={{ color: '#34d399' }}
                    />
                    <Bar dataKey="avg" fill="#6366f1" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
