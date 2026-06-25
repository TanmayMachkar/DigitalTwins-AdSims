import { useState } from 'react'
import { useSSE } from '../hooks/useSSE'
import LogStream from './LogStream'
import ResponseCard from './ResponseCard'

export default function SimulatePanel() {
  const [inputId, setInputId] = useState('')
  const [streamUrl, setStreamUrl] = useState(null)
  const { events, status } = useSSE(streamUrl)

  const logs = events.filter((e) => e.type === 'log' || e.type === 'error')
  const cards = events.filter((e) => e.type === 'card')
  const doneEvent = events.find((e) => e.type === 'done')

  const handleStart = () => {
    if (!inputId.trim()) return
    setStreamUrl(null)
    setTimeout(() => {
      setStreamUrl(`http://localhost:8000/api/simulate?post_id=${encodeURIComponent(inputId.trim())}`)
    }, 0)
  }

  return (
    <div>
      <h2 className="text-xl font-semibold mb-1">Simulate</h2>
      <p className="text-gray-400 text-sm mb-5">
        Enter a Reddit post ID to simulate how each digital twin would respond.
      </p>

      <div className="flex gap-3">
        <input
          type="text"
          value={inputId}
          onChange={(e) => setInputId(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleStart()}
          placeholder="e.g. 1krk2jt"
          className="flex-1 bg-gray-900 border border-gray-700 rounded-lg px-4 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500"
        />
        <button
          onClick={handleStart}
          disabled={status === 'streaming' || !inputId.trim()}
          className="px-5 py-2.5 bg-violet-600 hover:bg-violet-500 disabled:opacity-40 disabled:cursor-not-allowed rounded-lg text-sm font-semibold transition-colors"
        >
          {status === 'streaming' ? 'Simulating...' : 'Simulate'}
        </button>
      </div>

      <LogStream
        logs={logs}
        status={status === 'streaming' && cards.length === 0 ? 'streaming' : cards.length > 0 ? 'idle' : status}
      />

      {cards.length > 0 && (
        <div className="mt-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-gray-200">
              Simulated Responses
              {doneEvent && (
                <span className="ml-2 text-sm text-gray-500 font-normal">({doneEvent.total} users)</span>
              )}
            </h3>
            {status === 'streaming' && (
              <span className="text-xs text-violet-400 animate-pulse">{cards.length} generated...</span>
            )}
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {cards.map((card, i) => (
              <ResponseCard key={i} username={card.username} response={card.response} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
