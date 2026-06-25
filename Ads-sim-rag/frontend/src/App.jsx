import { useState } from 'react'
import TabBar from './components/TabBar'
import CollectPanel from './components/CollectPanel'
import SimulatePanel from './components/SimulatePanel'

export default function App() {
  const [tab, setTab] = useState('collect')

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <header className="bg-gradient-to-r from-violet-950 via-indigo-950 to-gray-950 border-b border-violet-900/40 px-8 py-6">
        <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-violet-400 to-indigo-300 bg-clip-text text-transparent">
          TwinSphere
        </h1>
        <p className="text-gray-400 text-sm mt-1">Reddit Digital Twin Ad Simulation</p>
        <TabBar active={tab} onChange={setTab} />
      </header>

      <main className="px-8 py-8 max-w-5xl mx-auto">
        {tab === 'collect' ? <CollectPanel /> : <SimulatePanel />}
      </main>
    </div>
  )
}
