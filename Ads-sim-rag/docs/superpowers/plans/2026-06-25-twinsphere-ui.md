# TwinSphere UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a TwinSphere web app with a FastAPI SSE backend and React Vite frontend supporting two modes — Collect & Index (stream live logs) and Simulate (stream user response cards).

**Architecture:** FastAPI backend exposes two SSE GET endpoints that call existing `src/` Python modules directly and yield JSON events for progress/results. React Vite frontend consumes these streams via `EventSource`, rendering a live log panel for collect/index and response cards for simulate.

**Tech Stack:** Python 3.11, FastAPI, uvicorn, sse-starlette, React 18, Vite, Tailwind CSS

## Global Constraints

- Backend root: `d:\Work Docs\BE Project\DigitalTwins-AdSims\Ads-sim-rag\backend\`
- Frontend root: `d:\Work Docs\BE Project\DigitalTwins-AdSims\Ads-sim-rag\frontend\`
- Backend runs on port 8000; frontend dev server on port 5173
- No subprocess calls — import `src/` modules directly in backend
- SSE only flows server→client; use GET with query params
- App title: "TwinSphere" everywhere

---

## File Map

**Backend (new)**
- `backend/main.py` — FastAPI app, CORS, router mounts
- `backend/routers/collect_router.py` — SSE endpoint: collect + index
- `backend/routers/simulate_router.py` — SSE endpoint: simulate per user
- `backend/requirements.txt` — fastapi, uvicorn, sse-starlette

**Frontend (new)**
- `frontend/` — Vite React scaffold
- `frontend/src/App.jsx` — root layout: header + tab switcher
- `frontend/src/components/TabBar.jsx` — two-tab nav (Collect & Index / Simulate)
- `frontend/src/components/CollectPanel.jsx` — URL input, start button, live log stream
- `frontend/src/components/LogStream.jsx` — scrolling log display with status icons
- `frontend/src/components/SimulatePanel.jsx` — post ID input, start button, card grid
- `frontend/src/components/ResponseCard.jsx` — single user response card
- `frontend/src/hooks/useSSE.js` — reusable hook: opens EventSource, collects events, handles done/error

---

### Task 1: FastAPI backend scaffold

**Files:**
- Create: `backend/main.py`
- Create: `backend/requirements.txt`
- Create: `backend/routers/__init__.py`

**Interfaces:**
- Produces: FastAPI `app` instance at `http://localhost:8000`; CORS open to `http://localhost:5173`; health check at `GET /api/health` returns `{"status": "ok"}`

- [ ] **Step 1: Install backend dependencies**

```bash
pip install fastapi uvicorn sse-starlette
```

- [ ] **Step 2: Create `backend/requirements.txt`**

```
fastapi
uvicorn
sse-starlette
```

- [ ] **Step 3: Create `backend/routers/__init__.py`** (empty file)

- [ ] **Step 4: Create `backend/main.py`**

```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers.collect_router import router as collect_router
from backend.routers.simulate_router import router as simulate_router

app = FastAPI(title="TwinSphere API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(collect_router, prefix="/api")
app.include_router(simulate_router, prefix="/api")

@app.get("/api/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 5: Verify backend starts**

```bash
cd "d:\Work Docs\BE Project\DigitalTwins-AdSims\Ads-sim-rag"
uvicorn backend.main:app --reload --port 8000
```

Expected: `Uvicorn running on http://127.0.0.1:8000`
Visit `http://localhost:8000/api/health` → `{"status":"ok"}`

- [ ] **Step 6: Commit**

```bash
git add backend/
git commit -m "feat: scaffold FastAPI backend with CORS and health check"
```

---

### Task 2: Collect & Index SSE endpoint

**Files:**
- Create: `backend/routers/collect_router.py`

**Interfaces:**
- Consumes: `src.reddit_client.fetch_commenters_histories`, `src.twin_builder.build_twin_profiles`, `src.rag_engine.create_vector_db` (imported directly)
- Produces: `GET /api/collect?url=<reddit_url>` — SSE stream of `text/event-stream`. Each event is `data: <json>\n\n`. JSON shapes:
  - `{"type": "log", "message": "string"}` — progress log line
  - `{"type": "done", "post_id": "string"}` — pipeline complete
  - `{"type": "error", "message": "string"}` — failure

- [ ] **Step 1: Create `backend/routers/collect_router.py`**

```python
import json
import os
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from src.reddit_client import fetch_commenters_histories
from src.twin_builder import build_twin_profiles
from src.rag_engine import create_vector_db
from src.config import RAW_DIR, PROCESSED_DIR

router = APIRouter()

def event(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"

async def run_collect_pipeline(url: str):
    try:
        yield event({"type": "log", "message": f"Starting data collection for: {url}"})

        yield event({"type": "log", "message": "Fetching Reddit post and user histories..."})
        user_histories, post_info = fetch_commenters_histories(url)
        yield event({"type": "log", "message": f"Fetched {len(user_histories)} user histories for post '{post_info['title']}'"})

        histories_file = os.path.join(RAW_DIR, f"{post_info['id']}_user_histories.json")

        yield event({"type": "log", "message": "Building digital twin profiles..."})
        build_twin_profiles(histories_file)
        yield event({"type": "log", "message": f"Twin profiles built in {PROCESSED_DIR}"})

        yield event({"type": "log", "message": "Indexing profiles into vector database..."})
        create_vector_db(PROCESSED_DIR)
        yield event({"type": "log", "message": "Vector database indexed and ready."})

        yield event({"type": "done", "post_id": post_info["id"]})

    except Exception as e:
        yield event({"type": "error", "message": str(e)})

@router.get("/collect")
async def collect(url: str):
    return StreamingResponse(
        run_collect_pipeline(url),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
```

- [ ] **Step 2: Test endpoint manually**

```bash
curl "http://localhost:8000/api/collect?url=https://www.reddit.com/r/animequestions/comments/1krk2jt/which_one_do_yall_prefer_naruto_or_one_piece/"
```

Expected: stream of `data: {"type":"log",...}` lines ending with `data: {"type":"done",...}`

- [ ] **Step 3: Commit**

```bash
git add backend/routers/collect_router.py
git commit -m "feat: add collect+index SSE endpoint"
```

---

### Task 3: Simulate SSE endpoint

**Files:**
- Create: `backend/routers/simulate_router.py`

**Interfaces:**
- Consumes: `src.simulator.simulate_reaction`, `src.rag_engine` (ChromaDB collection), `src.config`
- Produces: `GET /api/simulate?post_id=<id>` — SSE stream. JSON shapes:
  - `{"type": "log", "message": "string"}` — status update
  - `{"type": "card", "username": "string", "response": "string"}` — one simulated user
  - `{"type": "done", "total": number}` — all users simulated
  - `{"type": "error", "message": "string"}` — failure

- [ ] **Step 1: Create `backend/routers/simulate_router.py`**

```python
import json
import os
import chromadb
from chromadb.utils import embedding_functions
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from src.simulator import simulate_reaction
from src.config import RAW_DIR, EMBEDDING_DIR
import json as _json

router = APIRouter()

def event(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"

async def run_simulate_pipeline(post_id: str):
    try:
        meta_file = os.path.join(RAW_DIR, f"{post_id}_post_meta.json")
        histories_file = os.path.join(RAW_DIR, f"{post_id}_user_histories.json")

        if not os.path.isfile(meta_file) or not os.path.isfile(histories_file):
            yield event({"type": "error", "message": f"No data found for post ID '{post_id}'. Run Collect & Index first."})
            return

        with open(meta_file, "r", encoding="utf-8") as f:
            post_info = _json.load(f)
        with open(histories_file, "r", encoding="utf-8") as f:
            user_histories = _json.load(f)

        yield event({"type": "log", "message": f"Post: {post_info['title']}"})
        yield event({"type": "log", "message": f"Simulating {len(user_histories)} users..."})

        embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        chroma_client = chromadb.PersistentClient(path=EMBEDDING_DIR)
        collection = chroma_client.get_collection(name="user_memory", embedding_function=embed_fn)

        total = 0
        for username, _ in user_histories.items():
            twin_id = f"twin_{username}"
            yield event({"type": "log", "message": f"Simulating {username}..."})
            response = simulate_reaction(post_info["title"], twin_id, collection)
            yield event({"type": "card", "username": username, "response": response})
            total += 1

        yield event({"type": "done", "total": total})

    except Exception as e:
        yield event({"type": "error", "message": str(e)})

@router.get("/simulate")
async def simulate(post_id: str):
    return StreamingResponse(
        run_simulate_pipeline(post_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
```

- [ ] **Step 2: Test endpoint manually**

```bash
curl "http://localhost:8000/api/simulate?post_id=1krk2jt"
```

Expected: stream of log events then card events then done event.

- [ ] **Step 3: Commit**

```bash
git add backend/routers/simulate_router.py
git commit -m "feat: add simulate SSE endpoint"
```

---

### Task 4: React Vite frontend scaffold

**Files:**
- Create: `frontend/` (Vite scaffold)
- Modify: `frontend/index.html` — set title to TwinSphere
- Create: `frontend/src/index.css` — Tailwind directives

**Interfaces:**
- Produces: dev server at `http://localhost:5173` rendering blank TwinSphere shell

- [ ] **Step 1: Scaffold Vite React project**

```bash
cd "d:\Work Docs\BE Project\DigitalTwins-AdSims\Ads-sim-rag"
npm create vite@latest frontend -- --template react
cd frontend
npm install
```

- [ ] **Step 2: Install Tailwind CSS**

```bash
npm install -D tailwindcss @tailwindcss/vite
```

- [ ] **Step 3: Configure Tailwind in `frontend/vite.config.js`**

```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
})
```

- [ ] **Step 4: Replace `frontend/src/index.css`**

```css
@import "tailwindcss";
```

- [ ] **Step 5: Set page title in `frontend/index.html`**

Replace `<title>Vite + React</title>` with `<title>TwinSphere</title>`

- [ ] **Step 6: Clear `frontend/src/App.jsx` to minimal shell**

```jsx
export default function App() {
  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <p className="p-8 text-xl">TwinSphere loading...</p>
    </div>
  )
}
```

- [ ] **Step 7: Verify dev server**

```bash
cd frontend && npm run dev
```

Expected: browser shows dark page with "TwinSphere loading..."

- [ ] **Step 8: Commit**

```bash
cd ..
git add frontend/
git commit -m "feat: scaffold React Vite frontend with Tailwind"
```

---

### Task 5: useSSE hook

**Files:**
- Create: `frontend/src/hooks/useSSE.js`

**Interfaces:**
- Produces: `useSSE(url)` — React hook. Returns `{ events, status }` where:
  - `events`: array of parsed JSON objects from SSE stream
  - `status`: `"idle" | "streaming" | "done" | "error"`
  - `url`: when set (non-null string), hook opens EventSource and streams. When null, hook resets.

- [ ] **Step 1: Create `frontend/src/hooks/useSSE.js`**

```js
import { useState, useEffect } from 'react'

export function useSSE(url) {
  const [events, setEvents] = useState([])
  const [status, setStatus] = useState('idle')

  useEffect(() => {
    if (!url) {
      setEvents([])
      setStatus('idle')
      return
    }

    setEvents([])
    setStatus('streaming')
    const es = new EventSource(url)

    es.onmessage = (e) => {
      const data = JSON.parse(e.data)
      setEvents((prev) => [...prev, data])
      if (data.type === 'done' || data.type === 'error') {
        setStatus(data.type === 'done' ? 'done' : 'error')
        es.close()
      }
    }

    es.onerror = () => {
      setStatus('error')
      setEvents((prev) => [...prev, { type: 'error', message: 'Connection lost.' }])
      es.close()
    }

    return () => es.close()
  }, [url])

  return { events, status }
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/hooks/useSSE.js
git commit -m "feat: add useSSE hook for EventSource streaming"
```

---

### Task 6: App layout — header and tab bar

**Files:**
- Modify: `frontend/src/App.jsx`
- Create: `frontend/src/components/TabBar.jsx`

**Interfaces:**
- Produces: Full-page layout with gradient header showing "TwinSphere" title + subtitle, and two tabs: "Collect & Index" and "Simulate". Active tab renders the correct panel (panels are placeholders for now).

- [ ] **Step 1: Create `frontend/src/components/TabBar.jsx`**

```jsx
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
```

- [ ] **Step 2: Replace `frontend/src/App.jsx`**

```jsx
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
```

- [ ] **Step 3: Create placeholder `frontend/src/components/CollectPanel.jsx`**

```jsx
export default function CollectPanel() {
  return <div className="text-gray-400">Collect & Index panel coming soon</div>
}
```

- [ ] **Step 4: Create placeholder `frontend/src/components/SimulatePanel.jsx`**

```jsx
export default function SimulatePanel() {
  return <div className="text-gray-400">Simulate panel coming soon</div>
}
```

- [ ] **Step 5: Verify layout in browser**

```bash
cd frontend && npm run dev
```

Expected: Dark page with gradient header "TwinSphere", subtitle, two tab buttons, tab switching works.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/
git commit -m "feat: add TwinSphere header and tab navigation"
```

---

### Task 7: LogStream component

**Files:**
- Create: `frontend/src/components/LogStream.jsx`

**Interfaces:**
- Consumes: `logs` — array of `{type, message}` objects; `status` — `"idle"|"streaming"|"done"|"error"`
- Produces: Auto-scrolling dark terminal-style log panel. Log lines prefixed with `✓` (done), `✗` (error), or `›` (log). Shows spinner when streaming. Shows completion banner when done.

- [ ] **Step 1: Create `frontend/src/components/LogStream.jsx`**

```jsx
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
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/LogStream.jsx
git commit -m "feat: add auto-scrolling LogStream component"
```

---

### Task 8: CollectPanel — full implementation

**Files:**
- Modify: `frontend/src/components/CollectPanel.jsx`

**Interfaces:**
- Consumes: `useSSE(url)` hook; `LogStream` component
- Produces: URL text input + "Start Collection" button. On submit, calls `GET http://localhost:8000/api/collect?url=<input>` via EventSource, renders live logs in `LogStream`. Button disabled while streaming. On done, shows post ID. On error, shows error in log.

- [ ] **Step 1: Replace `frontend/src/components/CollectPanel.jsx`**

```jsx
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
```

- [ ] **Step 2: Test in browser**

Start backend: `uvicorn backend.main:app --reload --port 8000`
Start frontend: `cd frontend && npm run dev`
Paste a Reddit URL and click Start Collection.
Expected: log lines appear in real-time as collection runs.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/CollectPanel.jsx
git commit -m "feat: implement CollectPanel with SSE log streaming"
```

---

### Task 9: ResponseCard component

**Files:**
- Create: `frontend/src/components/ResponseCard.jsx`

**Interfaces:**
- Consumes: `username` (string), `response` (string)
- Produces: Dark card with Reddit-style avatar placeholder, bold username, and response text body.

- [ ] **Step 1: Create `frontend/src/components/ResponseCard.jsx`**

```jsx
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
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/ResponseCard.jsx
git commit -m "feat: add ResponseCard component"
```

---

### Task 10: SimulatePanel — full implementation

**Files:**
- Modify: `frontend/src/components/SimulatePanel.jsx`

**Interfaces:**
- Consumes: `useSSE(url)` hook; `LogStream`, `ResponseCard` components
- Produces: Post ID text input + "Simulate" button. On submit, calls `GET http://localhost:8000/api/simulate?post_id=<input>`. Streams log events into `LogStream`. As `card` events arrive, appends `ResponseCard` components to a grid in real-time. Shows total count when done.

- [ ] **Step 1: Replace `frontend/src/components/SimulatePanel.jsx`**

```jsx
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

      <LogStream logs={logs} status={status === 'streaming' && cards.length === 0 ? 'streaming' : cards.length > 0 ? 'idle' : status} />

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
```

- [ ] **Step 2: Test end-to-end in browser**

1. Start backend: `uvicorn backend.main:app --reload --port 8000`
2. Start frontend: `cd frontend && npm run dev`
3. Go to Simulate tab
4. Enter post ID `1krk2jt` and click Simulate
5. Expected: log lines show, then cards appear one-by-one as each simulation completes

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/SimulatePanel.jsx
git commit -m "feat: implement SimulatePanel with real-time response cards"
```

---

### Task 11: Startup script

**Files:**
- Create: `start.bat` (Windows) or notes below

**Interfaces:**
- Produces: Single command to start both backend and frontend for demo

- [ ] **Step 1: Create `start.bat`**

```bat
@echo off
start "TwinSphere Backend" cmd /k "uvicorn backend.main:app --port 8000"
timeout /t 2
start "TwinSphere Frontend" cmd /k "cd frontend && npm run dev"
echo TwinSphere starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
```

- [ ] **Step 2: Commit**

```bash
git add start.bat
git commit -m "feat: add startup script for demo"
```
