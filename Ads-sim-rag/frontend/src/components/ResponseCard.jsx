export default function ResponseCard({ username, response }) {
  const initial = username.charAt(0).toUpperCase()
  const hues = ['violet', 'indigo', 'sky', 'emerald', 'amber', 'rose']
  const hue = hues[username.charCodeAt(0) % hues.length]

  const avatarColors = {
    violet: 'bg-violet-700',
    indigo: 'bg-indigo-700',
    sky: 'bg-sky-700',
    emerald: 'bg-emerald-700',
    amber: 'bg-amber-700',
    rose: 'bg-rose-700',
  }

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 hover:border-violet-800 transition-colors">
      <div className="flex items-center gap-3 mb-3">
        <div className={`w-9 h-9 rounded-full ${avatarColors[hue]} flex items-center justify-center text-sm font-bold text-white shrink-0`}>
          {initial}
        </div>
        <div>
          <p className="font-semibold text-sm text-white">u/{username}</p>
          <p className="text-xs text-gray-500">Digital Twin</p>
        </div>
      </div>
      <p className="text-gray-300 text-sm leading-relaxed whitespace-pre-wrap">{response}</p>
    </div>
  )
}
