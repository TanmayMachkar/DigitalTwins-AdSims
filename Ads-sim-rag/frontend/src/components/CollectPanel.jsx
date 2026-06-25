import { useState } from 'react'
import { useSSE } from '../hooks/useSSE'
import LogStream from './LogStream'

export default function CollectPanel() {
  const [inputUrl, setInputUrl] = useState('')
  const [streamUrl, setStreamUrl] = useState(null)
  const { events, status } = useSSE(streamUrl)

  const logs = events.filter((e) => e.type === 'log' || e.type === 'error')
  const doneEvent = events.find((e) => e.type === 'done')

  const handleStart = () => {
    if (!inputUrl.trim()) return
    setStreamUrl(null)
    setTimeout(() => {
      setStreamUrl(`http://localhost:8000/api/collect?url=${encodeURIComponent(inputUrl.trim())}`)
    }, 0)
  }

  return (
    <div>
      <h2 className="text-xl font-semibold mb-1">Collect & Index</h2>
      <p className="text-gray-400 text-sm mb-5">
        Paste a Reddit post URL to collect user histories and build twin profiles.
      </p>

      <div className="flex gap-3">
        <input
          type="text"
          value={inputUrl}
          onChange={(e) => setInputUrl(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleStart()}
          placeholder="https://www.reddit.com/r/..."
          className="flex-1 bg-gray-900 border border-gray-700 rounded-lg px-4 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500"
        />
        <button
          onClick={handleStart}
          disabled={status === 'streaming' || !inputUrl.trim()}
          className="px-5 py-2.5 bg-violet-600 hover:bg-violet-500 disabled:opacity-40 disabled:cursor-not-allowed rounded-lg text-sm font-semibold transition-colors"
        >
          {status === 'streaming' ? 'Running...' : 'Start Collection'}
        </button>
      </div>

      <LogStream logs={logs} status={status} />

      {doneEvent && (
        <div className="mt-4 p-4 bg-emerald-950/50 border border-emerald-800 rounded-xl text-sm">
          <span className="text-emerald-400 font-semibold">Collection complete. </span>
          <span className="text-gray-300">
            Post ID: <code className="text-violet-300 bg-gray-800 px-1.5 py-0.5 rounded">{doneEvent.post_id}</code>
            {' '}— use this in the Simulate tab.
          </span>
        </div>
      )}
    </div>
  )
}
