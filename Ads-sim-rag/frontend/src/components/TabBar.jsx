const TABS = [
  { id: 'collect', label: 'Collect & Index' },
  { id: 'simulate', label: 'Simulate' },
]

export default function TabBar({ active, onChange }) {
  return (
    <div className="flex gap-2 mt-6">
      {TABS.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          className={`px-6 py-2 rounded-full text-sm font-semibold transition-all ${
            active === tab.id
              ? 'bg-violet-600 text-white shadow-lg shadow-violet-500/30'
              : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white'
          }`}
        >
          {tab.label}
        </button>
      ))}
    </div>
  )
}
