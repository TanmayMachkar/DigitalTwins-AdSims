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
