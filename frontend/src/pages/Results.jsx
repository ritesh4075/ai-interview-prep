import { useParams, useLocation, useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import axios from 'axios'

function ScoreBar({ label, value }) {
  const pct = Math.round(value * 100)
  const color = pct >= 70 ? 'bg-green-500' : pct >= 45 ? 'bg-yellow-500' : 'bg-red-500'
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span className="text-gray-400">{label}</span>
        <span className="text-white font-medium">{pct}%</span>
      </div>
      <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
        <div className={`h-2 rounded-full transition-all duration-700 ${color}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}

export default function Results() {
  const { id } = useParams()
  const { state } = useLocation()
  const navigate = useNavigate()
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    axios.get(`/api/feedback/summary/${id}`)
      .then(r => setSummary(r.data))
      .catch(() => {
        if (state?.answers) {
          setSummary({ answers: state.answers, avg_score: 0 })
        }
      })
      .finally(() => setLoading(false))
  }, [id])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center text-white">
        <p className="text-gray-400">Loading results...</p>
      </div>
    )
  }

  const responses = summary?.responses || state?.answers || []
  const avgScore = summary?.avg_score || 0

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <div className="max-w-3xl mx-auto px-6 py-10 space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className={`text-6xl font-black mb-2 ${avgScore >= 7 ? 'text-green-400' : avgScore >= 5 ? 'text-yellow-400' : 'text-red-400'}`}>
            {avgScore}/10
          </div>
          <p className="text-gray-400">
            {avgScore >= 7 ? '🎉 Great performance! You are interview-ready.' :
             avgScore >= 5 ? '📈 Good effort! A few areas need practice.' :
             '💪 Keep practicing! Review the feedback below.'}
          </p>
        </div>

        {/* Per-question feedback */}
        <div className="space-y-6">
          {responses.map((r, i) => {
            const fb = r.feedback || r.feedback
            return (
              <div key={i} className="bg-gray-900 rounded-2xl border border-gray-800 overflow-hidden">
                {/* Question header */}
                <div className="px-6 py-4 border-b border-gray-800 flex justify-between items-start gap-4">
                  <p className="text-sm font-medium text-gray-300 flex-1">Q{i + 1}: {r.question}</p>
                  {fb && (
                    <span className={`text-lg font-bold shrink-0 ${fb.overall_score >= 7 ? 'text-green-400' : fb.overall_score >= 5 ? 'text-yellow-400' : 'text-red-400'}`}>
                      {fb.overall_score}/10
                    </span>
                  )}
                </div>

                <div className="px-6 py-4 space-y-4">
                  {/* Your answer */}
                  <div>
                    <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Your Answer</p>
                    <p className="text-gray-300 text-sm leading-relaxed">{r.answer_text || r.answer}</p>
                  </div>

                  {fb && (
                    <>
                      {/* Score breakdown */}
                      <div className="space-y-2 pt-2 border-t border-gray-800">
                        <p className="text-xs text-gray-500 uppercase tracking-wide mb-3">Score Breakdown</p>
                        <ScoreBar label="Semantic Match" value={fb.semantic_score} />
                        <ScoreBar label="Keywords" value={fb.keyword_score} />
                        <ScoreBar label="Clarity" value={fb.clarity_score} />
                        <ScoreBar label="Confidence" value={fb.confidence_score} />
                      </div>

                      {/* Keywords */}
                      {(fb.keywords_found?.length > 0 || fb.keywords_missing?.length > 0) && (
                        <div className="flex gap-6 pt-2 border-t border-gray-800">
                          {fb.keywords_found?.length > 0 && (
                            <div>
                              <p className="text-xs text-gray-500 mb-2">✅ Keywords Found</p>
                              <div className="flex flex-wrap gap-1">
                                {fb.keywords_found.map(k => (
                                  <span key={k} className="text-xs bg-green-900/50 text-green-300 px-2 py-0.5 rounded-full">{k}</span>
                                ))}
                              </div>
                            </div>
                          )}
                          {fb.keywords_missing?.length > 0 && (
                            <div>
                              <p className="text-xs text-gray-500 mb-2">❌ Missing Keywords</p>
                              <div className="flex flex-wrap gap-1">
                                {fb.keywords_missing.map(k => (
                                  <span key={k} className="text-xs bg-red-900/50 text-red-300 px-2 py-0.5 rounded-full">{k}</span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      )}

                      {/* Suggestions */}
                      {fb.suggestions && (
                        <div className="pt-2 border-t border-gray-800">
                          <p className="text-xs text-gray-500 mb-1">💬 AI Suggestions</p>
                          <p className="text-sm text-yellow-300">{fb.suggestions}</p>
                        </div>
                      )}

                      {/* Ideal answer */}
                      {fb.ideal_answer && (
                        <details className="pt-2 border-t border-gray-800">
                          <summary className="text-xs text-indigo-400 cursor-pointer hover:text-indigo-300">View ideal answer</summary>
                          <p className="text-sm text-gray-300 mt-2 leading-relaxed">{fb.ideal_answer}</p>
                        </details>
                      )}
                    </>
                  )}
                </div>
              </div>
            )
          })}
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <button onClick={() => navigate('/')} className="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-3 rounded-xl transition text-sm">
            🔄 Start New Interview
          </button>
          <button onClick={() => navigate('/analytics')} className="flex-1 bg-gray-800 hover:bg-gray-700 text-white font-semibold py-3 rounded-xl transition text-sm">
            📊 View Analytics
          </button>
        </div>
      </div>
    </div>
  )
}
