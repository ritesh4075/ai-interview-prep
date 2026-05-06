import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import toast from 'react-hot-toast'
import { useAuth } from '../hooks/useAuth'

const COMPANIES = ['General', 'Amazon', 'Google', 'TCS', 'Infosys', 'Microsoft']
const ROLES = ['Software Engineer', 'Data Scientist', 'Data Analyst', 'ML Engineer', 'Backend Developer', 'Frontend Developer', 'Full Stack Developer']
const DIFFICULTIES = ['easy', 'medium', 'hard']

export default function Dashboard() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [resumes, setResumes] = useState([])
  const [history, setHistory] = useState([])
  const [form, setForm] = useState({ company: 'General', role: 'Data Scientist', difficulty: 'medium', resume_id: '' })
  const [uploading, setUploading] = useState(false)
  const [starting, setStarting] = useState(false)

  useEffect(() => {
    axios.get('/api/resume/list').then(r => setResumes(r.data.resumes)).catch(() => {})
    axios.get('/api/interview/history').then(r => setHistory(r.data.interviews)).catch(() => {})
  }, [])

  const handleUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    const fd = new FormData()
    fd.append('file', file)
    setUploading(true)
    try {
      const res = await axios.post('/api/resume/upload', fd)
      setResumes(prev => [res.data.resume, ...prev])
      setForm(f => ({ ...f, resume_id: res.data.resume.id }))
      toast.success(`Resume parsed! Found ${res.data.resume.skills?.length || 0} skills.`)
    } catch {
      toast.error('Resume upload failed')
    } finally {
      setUploading(false)
    }
  }

  const handleStart = async () => {
    setStarting(true)
    try {
      const res = await axios.post('/api/interview/start', form)
      navigate(`/interview/${res.data.interview.id}`, { state: { questions: res.data.questions } })
    } catch {
      toast.error('Could not start interview')
    } finally {
      setStarting(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Navbar */}
      <nav className="border-b border-gray-800 px-6 py-4 flex justify-between items-center">
        <h1 className="text-xl font-bold text-indigo-400">🎯 InterviewAI</h1>
        <div className="flex items-center gap-4">
          <button onClick={() => navigate('/analytics')} className="text-gray-400 hover:text-white text-sm transition">Analytics</button>
          <span className="text-gray-400 text-sm">{user?.name}</span>
          <button onClick={logout} className="text-sm text-red-400 hover:text-red-300 transition">Logout</button>
        </div>
      </nav>

      <div className="max-w-5xl mx-auto px-6 py-10 space-y-8">
        {/* Header */}
        <div>
          <h2 className="text-2xl font-bold">Welcome back, {user?.name?.split(' ')[0]} 👋</h2>
          <p className="text-gray-400 mt-1">Configure your mock interview below and start practicing.</p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Start Interview Card */}
          <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800 space-y-4">
            <h3 className="font-semibold text-lg">Start Mock Interview</h3>

            <div>
              <label className="text-sm text-gray-400 mb-1 block">Target Company</label>
              <select
                value={form.company}
                onChange={e => setForm({ ...form, company: e.target.value })}
                className="w-full bg-gray-800 text-white rounded-lg px-3 py-2 border border-gray-700 focus:outline-none focus:border-indigo-500"
              >
                {COMPANIES.map(c => <option key={c}>{c}</option>)}
              </select>
            </div>

            <div>
              <label className="text-sm text-gray-400 mb-1 block">Role</label>
              <select
                value={form.role}
                onChange={e => setForm({ ...form, role: e.target.value })}
                className="w-full bg-gray-800 text-white rounded-lg px-3 py-2 border border-gray-700 focus:outline-none focus:border-indigo-500"
              >
                {ROLES.map(r => <option key={r}>{r}</option>)}
              </select>
            </div>

            <div>
              <label className="text-sm text-gray-400 mb-1 block">Difficulty</label>
              <div className="flex gap-2">
                {DIFFICULTIES.map(d => (
                  <button
                    key={d}
                    onClick={() => setForm({ ...form, difficulty: d })}
                    className={`flex-1 py-2 rounded-lg text-sm font-medium capitalize transition ${
                      form.difficulty === d
                        ? 'bg-indigo-600 text-white'
                        : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                    }`}
                  >
                    {d}
                  </button>
                ))}
              </div>
            </div>

            {resumes.length > 0 && (
              <div>
                <label className="text-sm text-gray-400 mb-1 block">Resume (optional)</label>
                <select
                  value={form.resume_id}
                  onChange={e => setForm({ ...form, resume_id: e.target.value })}
                  className="w-full bg-gray-800 text-white rounded-lg px-3 py-2 border border-gray-700 focus:outline-none focus:border-indigo-500"
                >
                  <option value="">No resume</option>
                  {resumes.map(r => <option key={r.id} value={r.id}>{r.filename}</option>)}
                </select>
              </div>
            )}

            <button
              onClick={handleStart}
              disabled={starting}
              className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-semibold py-3 rounded-lg transition"
            >
              {starting ? 'Preparing questions...' : '🚀 Start Interview'}
            </button>
          </div>

          {/* Upload Resume Card */}
          <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800 space-y-4">
            <h3 className="font-semibold text-lg">Upload Resume</h3>
            <p className="text-gray-400 text-sm">Upload your PDF resume to get personalized questions based on your skills and experience.</p>

            <label className="block border-2 border-dashed border-gray-700 hover:border-indigo-500 rounded-xl p-8 text-center cursor-pointer transition">
              <input type="file" accept=".pdf" onChange={handleUpload} className="hidden" />
              {uploading
                ? <p className="text-indigo-400">Parsing resume...</p>
                : <p className="text-gray-400">📄 Click to upload PDF resume</p>
              }
            </label>

            {resumes.length > 0 && (
              <div className="space-y-2">
                <p className="text-sm text-gray-400">Your resumes:</p>
                {resumes.slice(0, 3).map(r => (
                  <div key={r.id} className="bg-gray-800 rounded-lg px-3 py-2 text-sm">
                    <p className="text-white">{r.filename}</p>
                    <p className="text-gray-400 text-xs mt-0.5">{r.skills?.slice(0, 4).join(', ')} {r.skills?.length > 4 ? `+${r.skills.length - 4} more` : ''}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Interview History */}
        {history.length > 0 && (
          <div>
            <h3 className="font-semibold text-lg mb-4">Recent Interviews</h3>
            <div className="space-y-2">
              {history.slice(0, 5).map(iv => (
                <div
                  key={iv.id}
                  onClick={() => iv.status === 'completed' && navigate(`/results/${iv.id}`)}
                  className="bg-gray-900 border border-gray-800 rounded-xl px-5 py-4 flex items-center justify-between cursor-pointer hover:border-gray-600 transition"
                >
                  <div>
                    <p className="font-medium">{iv.company} — {iv.role}</p>
                    <p className="text-gray-400 text-sm capitalize">{iv.difficulty} · {iv.status}</p>
                  </div>
                  <div className="text-right">
                    {iv.overall_score != null
                      ? <p className={`text-lg font-bold ${iv.overall_score >= 7 ? 'text-green-400' : iv.overall_score >= 5 ? 'text-yellow-400' : 'text-red-400'}`}>{iv.overall_score}/10</p>
                      : <p className="text-gray-500 text-sm">In progress</p>
                    }
                    <p className="text-gray-500 text-xs">{new Date(iv.started_at).toLocaleDateString()}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
