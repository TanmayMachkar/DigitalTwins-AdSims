import { useEffect, useRef } from 'react'

const icon = (type) =>
  type === 'error' ? '✗' : type === 'done' ? '✓' : '›'

const color = (type) =>
  type === 'error'
    ? 'text-red-400'
    : type === 'done'
    ? 'text-emerald-400'
    : 'text-gray-300'

export default function LogStream({ logs, status }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])

  if (status === 'idle') return null

  return (
    <div className="mt-6 bg-gray-900 border border-gray-800 rounded-xl p-4 font-mono text-sm max-h-72 overflow-y-auto">
      {logs.map((entry, i) => (
        <div key={i} className={`flex gap-2 py-0.5 ${color(entry.type)}`}>
          <span className="shrink-0">{icon(entry.type)}</span>
          <span>{entry.message}</span>
        </div>
      ))}
      {status === 'streaming' && (
        <div className="flex gap-2 py-0.5 text-violet-400 animate-pulse">
          <span>›</span>
          <span>Processing...</span>
        </div>
      )}
      {status === 'done' && (
        <div className="mt-3 pt-3 border-t border-gray-800 text-emerald-400 font-semibold">
          ✓ Pipeline complete
        </div>
      )}
      <div ref={bottomRef} />
    </div>
  )
}
