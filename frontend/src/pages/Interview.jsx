import { useState } from 'react'
import { useParams, useLocation, useNavigate } from 'react-router-dom'
import axios from 'axios'
import toast from 'react-hot-toast'

export default function Interview() {
  const { id } = useParams()
  const { state } = useLocation()
  const navigate = useNavigate()
  const questions = state?.questions || []

  const [current, setCurrent] = useState(0)
  const [answer, setAnswer] = useState('')
  const [answers, setAnswers] = useState([])
  const [submitting, setSubmitting] = useState(false)
  const [ending, setEnding] = useState(false)

  const currentQ = questions[current]
  const isLast = current === questions.length - 1

  const submitAnswer = async () => {
    if (!answer.trim()) {
      toast.error('Please write an answer first')
      return
    }
    setSubmitting(true)
    try {
      const res = await axios.post(`/api/interview/${id}/answer`, {
        question: currentQ.question,
        answer_text: answer,
        question_type: currentQ.type,
      })
      const responseId = res.data.response_id

      // Get AI feedback immediately
      const fbRes = await axios.post(`/api/feedback/evaluate/${responseId}`)
      setAnswers(prev => [...prev, {
        question: currentQ.question,
        answer,
        response_id: responseId,
        feedback: fbRes.data.feedback,
      }])

      setAnswer('')
      if (isLast) {
        await endInterview()
      } else {
        setCurrent(c => c + 1)
        toast.success('Answer submitted ✓')
      }
    } catch {
      toast.error('Failed to submit answer')
    } finally {
      setSubmitting(false)
    }
  }

  const endInterview = async () => {
    setEnding(true)
    try {
      await axios.post(`/api/interview/${id}/end`)
      toast.success('Interview complete!')
      navigate(`/results/${id}`, { state: { answers } })
    } catch {
      navigate(`/results/${id}`, { state: { answers } })
    } finally {
      setEnding(false)
    }
  }

  if (!questions.length) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center text-white">
        <div className="text-center">
          <p className="text-gray-400 mb-4">No questions found.</p>
          <button onClick={() => navigate('/')} className="text-indigo-400 hover:text-indigo-300">← Back to Dashboard</button>
        </div>
      </div>
    )
  }

  const progress = ((current) / questions.length) * 100

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col">
      {/* Top bar */}
      <div className="border-b border-gray-800 px-6 py-4 flex items-center justify-between">
        <h1 className="text-lg font-semibold text-indigo-400">🎯 Mock Interview</h1>
        <span className="text-gray-400 text-sm">Question {current + 1} of {questions.length}</span>
      </div>

      {/* Progress bar */}
      <div className="h-1 bg-gray-800">
        <div className="h-1 bg-indigo-500 transition-all duration-500" style={{ width: `${progress}%` }} />
      </div>

      <div className="flex-1 max-w-3xl mx-auto w-full px-6 py-10 space-y-6">
        {/* Question card */}
        <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
          <div className="flex items-center gap-2 mb-3">
            <span className={`text-xs px-2 py-1 rounded-full font-medium capitalize ${
              currentQ.type === 'behavioral' ? 'bg-blue-900 text-blue-300' :
              currentQ.type === 'technical' ? 'bg-purple-900 text-purple-300' :
              currentQ.type === 'hr' ? 'bg-green-900 text-green-300' :
              'bg-yellow-900 text-yellow-300'
            }`}>
              {currentQ.type}
            </span>
          </div>
          <p className="text-lg font-medium leading-relaxed">{currentQ.question}</p>
          {currentQ.tip && (
            <p className="text-gray-500 text-sm mt-3 italic">💡 Tip: {currentQ.tip}</p>
          )}
        </div>

        {/* Answer textarea */}
        <div>
          <label className="text-sm text-gray-400 mb-2 block">Your Answer</label>
          <textarea
            value={answer}
            onChange={e => setAnswer(e.target.value)}
            rows={8}
            placeholder="Type your answer here. Use STAR format for behavioral questions: Situation → Task → Action → Result"
            className="w-full bg-gray-900 text-white rounded-xl px-4 py-3 border border-gray-700 focus:outline-none focus:border-indigo-500 resize-none text-sm leading-relaxed"
          />
          <div className="flex justify-between mt-1">
            <span className="text-xs text-gray-500">{answer.split(/\s+/).filter(Boolean).length} words</span>
            <span className="text-xs text-gray-500">Aim for 100–200 words</span>
          </div>
        </div>

        {/* Previously answered (mini preview) */}
        {answers.length > 0 && (
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 space-y-2">
            <p className="text-sm text-gray-400 font-medium">Completed ({answers.length})</p>
            {answers.map((a, i) => (
              <div key={i} className="flex items-center justify-between text-sm">
                <p className="text-gray-300 truncate flex-1 mr-4">Q{i + 1}: {a.question.slice(0, 60)}...</p>
                <span className={`font-bold shrink-0 ${
                  a.feedback?.overall_score >= 7 ? 'text-green-400' :
                  a.feedback?.overall_score >= 5 ? 'text-yellow-400' : 'text-red-400'
                }`}>
                  {a.feedback?.overall_score ?? '—'}/10
                </span>
              </div>
            ))}
          </div>
        )}

        {/* Submit button */}
        <button
          onClick={submitAnswer}
          disabled={submitting || ending}
          className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-semibold py-3 rounded-xl transition text-sm"
        >
          {submitting || ending
            ? 'Evaluating with AI...'
            : isLast
              ? '✅ Submit & Finish Interview'
              : `Submit Answer & Next →`
          }
        </button>
      </div>
    </div>
  )
}
