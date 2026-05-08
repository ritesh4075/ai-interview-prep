import { useState, useEffect } from 'react'
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

  // =========================
  // 🎤 SPEECH SYNTHESIS (AI speaks question)
  // =========================
  const speakQuestion = (text) => {
    window.speechSynthesis.cancel() // prevent overlap
    const speech = new SpeechSynthesisUtterance(text)
    speech.lang = "en-US"
    speech.rate = 1
    window.speechSynthesis.speak(speech)
  }

  // Auto speak question on change
  useEffect(() => {
    if (currentQ?.question) {
      speakQuestion(currentQ.question)
    }
  }, [current])

  // =========================
  // 🎤 SPEECH RECOGNITION (user speaks answer)
  // =========================
  const startVoiceInput = () => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition

    if (!SpeechRecognition) {
      alert("Speech Recognition not supported in this browser")
      return
    }

    const recognition = new SpeechRecognition()
    recognition.lang = "en-US"
    recognition.interimResults = false

    recognition.start()

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript
      setAnswer(transcript)
    }

    recognition.onerror = (event) => {
      console.error("Speech error:", event.error)
    }
  }

  // =========================
  // SUBMIT ANSWER
  // =========================
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

      const fbRes = await axios.post(`/api/feedback/evaluate/${responseId}`)

      setAnswers(prev => [
        ...prev,
        {
          question: currentQ.question,
          answer,
          response_id: responseId,
          feedback: fbRes.data.feedback,
        }
      ])

      setAnswer('')

      if (isLast) {
        await endInterview()
      } else {
        setCurrent(c => c + 1)
        toast.success('Answer submitted ✓')
      }

    } catch (err) {
      toast.error('Failed to submit answer')
    } finally {
      setSubmitting(false)
    }
  }

  // =========================
  // END INTERVIEW
  // =========================
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
          <button
            onClick={() => navigate('/')}
            className="text-indigo-400 hover:text-indigo-300"
          >
            ← Back to Dashboard
          </button>
        </div>
      </div>
    )
  }

  const progress = (current / questions.length) * 100

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col">

      {/* Top bar */}
      <div className="border-b border-gray-800 px-6 py-4 flex justify-between">
        <h1 className="text-lg font-semibold text-indigo-400">
          🎯 Mock Interview
        </h1>
        <span className="text-gray-400 text-sm">
          Question {current + 1} of {questions.length}
        </span>
      </div>

      {/* Progress */}
      <div className="h-1 bg-gray-800">
        <div
          className="h-1 bg-indigo-500 transition-all"
          style={{ width: `${progress}%` }}
        />
      </div>

      <div className="flex-1 max-w-3xl mx-auto w-full px-6 py-10 space-y-6">

        {/* Question */}
        <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
          <p className="text-lg font-medium">{currentQ?.question}</p>
        </div>

        {/* Answer */}
        <textarea
          value={answer}
          onChange={e => setAnswer(e.target.value)}
          rows={7}
          className="w-full bg-gray-900 p-3 rounded-xl border border-gray-700"
          placeholder="Type your answer..."
        />

        {/* Voice + Submit buttons */}
        <div className="flex gap-3">

          <button
            onClick={startVoiceInput}
            className="bg-green-600 px-4 py-2 rounded-lg"
          >
            🎤 Speak Answer
          </button>

          <button
            onClick={submitAnswer}
            disabled={submitting || ending}
            className="bg-indigo-600 px-4 py-2 rounded-lg"
          >
            {isLast ? "Finish" : "Submit"}
          </button>

        </div>

      </div>
    </div>
  )
}