import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import axios from "axios";

const reactionColors = {
  like: "#09a45c",
  dislike: "#d82d4e",
  comment: "#2879ff",
  repost: "#7a3cff",
  ignore: "#8e9baa",
  alert_authority: "#ff7a00",
  volunteer: "#00a9b8"
};

/* ── Dummy responses for when backend is offline ── */
const DUMMY_RESPONSES = [
  {
    agent_name: "Ava — Tech Enthusiast",
    persona_icon: "⚡",
    reaction: "comment",
    confidence: 92,
    reasoning:
      "This post sparks a classic debate that resonates deeply with the tech and sports communities alike. The comparison draws parallels to platform wars in tech — polarizing but engaging.",
    final_message:
      "Great debate! Both are legends in their own right, but Messi's playmaking and vision are unmatched. Would love to see more data-driven comparisons!",
    tags: ["football", "debate", "comparison", "opinion"]
  },
  {
    agent_name: "Marco — Casual Scroller",
    persona_icon: "📱",
    reaction: "like",
    confidence: 78,
    reasoning:
      "A hot take that grabs attention. As someone who scrolls feeds quickly, this is the kind of post that makes you stop and engage. Simple, bold, effective.",
    final_message:
      "Messi all the way! 🐐 But Ronaldo fans, don't come for me 😂",
    tags: ["football", "messi", "viral"]
  },
  {
    agent_name: "Priya — Analytical Mind",
    persona_icon: "📊",
    reaction: "comment",
    confidence: 88,
    reasoning:
      "The post makes a subjective claim without supporting evidence. It would benefit from statistics — goals, assists, trophies — to make a stronger argument. Engagement-worthy nonetheless.",
    final_message:
      "Interesting take! If we look at the numbers: Messi has more assists after all, more Ballon d'Ors, and a World Cup. Numbers don't lie.",
    tags: ["statistics", "football", "analysis"]
  },
  {
    agent_name: "Jake — The Contrarian",
    persona_icon: "🎭",
    reaction: "dislike",
    confidence: 65,
    reasoning:
      "This kind of post oversimplifies a complex comparison. I enjoy playing devil's advocate — Ronaldo's discipline and longevity deserve equal recognition.",
    final_message:
      "Hard disagree. Ronaldo's Champions League record and adaptability across leagues put him on top for me. This debate is tired without nuance.",
    tags: ["football", "ronaldo", "counterpoint"]
  },
  {
    agent_name: "Sofia — Community Builder",
    persona_icon: "🤝",
    reaction: "repost",
    confidence: 84,
    reasoning:
      "Posts like this unite and divide communities in fun ways. Reposting with a poll could drive massive engagement and build conversation threads.",
    final_message:
      "Reposting this with a poll — who's the real GOAT? Let the people decide! This is the content that brings communities together.",
    tags: ["engagement", "poll", "community", "football"]
  },
  {
    agent_name: "Liam — Safety Sentinel",
    persona_icon: "🛡️",
    reaction: "ignore",
    confidence: 55,
    reasoning:
      "While this is a harmless opinion post, it doesn't contribute constructive information. I tend to prioritize content with actionable insights over debate bait.",
    final_message:
      "Eh, just another GOAT debate. Seen a thousand of these. Wake me up when there's actual news.",
    tags: ["low-priority", "opinion", "sports"]
  }
];

function toTitle(value) {
  if (!value) return "Unknown";
  return value
    .replace(/_/g, " ")
    .split(" ")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

/* ── Emotion Emoji Map ── */
const reactionEmojis = {
  like: "👍",
  dislike: "👎",
  comment: "💬",
  repost: "🔁",
  ignore: "😴",
  alert_authority: "🚨",
  volunteer: "🤝"
};

/* ─────────────────────────────────────────────
   2D Avatar Component — SVG character with
   mouth animation that "reads" final_message
   ───────────────────────────────────────────── */
function Avatar({ message, reaction }) {
  const [mouthOpen, setMouthOpen] = useState(false);
  const [displayText, setDisplayText] = useState("");
  const intervalRef = useRef(null);
  const charIndexRef = useRef(0);
  const emoji = reactionEmojis[reaction] || null;

  /* animate mouth & typewriter text whenever the message changes */
  useEffect(() => {
    clearInterval(intervalRef.current);
    charIndexRef.current = 0;
    setDisplayText("");

    if (!message) {
      setMouthOpen(false);
      return;
    }

    let toggle = false;
    intervalRef.current = setInterval(() => {
      toggle = !toggle;
      setMouthOpen(toggle);

      charIndexRef.current += 2;
      setDisplayText(message.slice(0, charIndexRef.current));

      if (charIndexRef.current >= message.length) {
        clearInterval(intervalRef.current);
        setMouthOpen(false);
      }
    }, 60);

    return () => clearInterval(intervalRef.current);
  }, [message]);

  return (
    <div className="avatar-wrapper">
      {/* Speech bubble — only visible when reading */}
      {message && (
        <div className="speech-bubble">
          <p>{displayText}<span className="cursor-blink">|</span></p>
        </div>
      )}

      {/* Emotion emoji floating above head */}
      {emoji && (
        <div className="emotion-emoji" key={reaction}>
          {emoji}
        </div>
      )}

      {/* SVG character */}
      <svg
        viewBox="0 0 200 260"
        className="avatar-svg"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Body */}
        <ellipse cx="100" cy="220" rx="52" ry="38" fill="#1a3a4a" stroke="#0ec9b5" strokeWidth="2" />
        {/* Neck */}
        <rect x="88" y="170" width="24" height="25" rx="8" fill="#f5c6a0" />
        {/* Head */}
        <ellipse cx="100" cy="120" rx="55" ry="60" fill="#f5c6a0" />
        {/* Hair */}
        <ellipse cx="100" cy="78" rx="57" ry="38" fill="#2c1810" />
        <ellipse cx="48" cy="105" rx="12" ry="24" fill="#2c1810" />
        <ellipse cx="152" cy="105" rx="12" ry="24" fill="#2c1810" />
        {/* Eyes */}
        <ellipse cx="78" cy="122" rx="8" ry="9" fill="white" />
        <ellipse cx="122" cy="122" rx="8" ry="9" fill="white" />
        <circle cx="80" cy="123" r="4" fill="#1a1a2e" />
        <circle cx="124" cy="123" r="4" fill="#1a1a2e" />
        {/* Sparkle in eyes */}
        <circle cx="82" cy="121" r="1.5" fill="white" />
        <circle cx="126" cy="121" r="1.5" fill="white" />
        {/* Eyebrows */}
        <path d="M65 108 Q78 100 90 108" stroke="#2c1810" strokeWidth="2.5" fill="none" strokeLinecap="round" />
        <path d="M110 108 Q122 100 135 108" stroke="#2c1810" strokeWidth="2.5" fill="none" strokeLinecap="round" />
        {/* Nose */}
        <path d="M97 135 Q100 142 103 135" stroke="#d4a574" strokeWidth="1.8" fill="none" strokeLinecap="round" />
        {/* Mouth — animated open/close */}
        {mouthOpen ? (
          <ellipse cx="100" cy="152" rx="12" ry="8" fill="#c0392b">
            <animate attributeName="ry" values="8;5;8" dur="0.25s" repeatCount="indefinite" />
          </ellipse>
        ) : (
          <path d="M88 150 Q100 160 112 150" stroke="#c0392b" strokeWidth="2.5" fill="none" strokeLinecap="round" />
        )}
        {/* Shirt collar */}
        <path d="M72 195 Q100 210 128 195" stroke="#0ec9b5" strokeWidth="2" fill="none" />
        {/* Shoulders */}
        <ellipse cx="60" cy="225" rx="18" ry="14" fill="#1a3a4a" stroke="#0ec9b5" strokeWidth="1.5" />
        <ellipse cx="140" cy="225" rx="18" ry="14" fill="#1a3a4a" stroke="#0ec9b5" strokeWidth="1.5" />
      </svg>

      {/* Label */}
      {!message && (
        <p className="avatar-hint">Hover a card to hear me read!</p>
      )}
    </div>
  );
}

/* ─────────────────────────────────────────────
   Main App
   ───────────────────────────────────────────── */
function App() {
  const [postText, setPostText] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [results, setResults] = useState(DUMMY_RESPONSES);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [hoveredMessage, setHoveredMessage] = useState("");
  const [hoveredReaction, setHoveredReaction] = useState("");

  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

  const summary = useMemo(() => {
    const reactionCount = {};
    let totalConfidence = 0;
    
    // Scoring logic for Sentiment Health
    let healthScore = 0;
    const scoreMap = {
      like: 10, repost: 15, comment: 5, volunteer: 20,
      ignore: -2, dislike: -10, alert_authority: -25
    };

    for (const item of results) {
      const reaction = item.reaction || "unknown";
      reactionCount[reaction] = (reactionCount[reaction] || 0) + 1;
      totalConfidence += Number(item.confidence || 0);
      healthScore += (scoreMap[reaction] || 0);
    }

    const avgConfidence = results.length ? (totalConfidence / results.length).toFixed(2) : "0.00";
    
    // Normalize health from arbitrary score to a 0-100 scale roughly
    const maxPossible = results.length * 20; 
    const minPossible = results.length * -25;
    const normalizedHealth = results.length 
      ? Math.max(0, Math.min(100, Math.round(((healthScore - minPossible) / (maxPossible - minPossible)) * 100)))
      : 50;

    let sentimentClass = "neutral";
    if (normalizedHealth >= 65) sentimentClass = "positive";
    else if (normalizedHealth <= 35) sentimentClass = "negative";

    return {
      reactionCount,
      avgConfidence,
      healthScore: normalizedHealth,
      sentimentClass
    };
  }, [results]);

  const handleCardHover = useCallback((finalMessage, reaction) => {
    setHoveredMessage(finalMessage || "");
    setHoveredReaction(reaction || "");
  }, []);

  const handleCardLeave = useCallback(() => {
    setHoveredMessage("");
    setHoveredReaction("");
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();

    if (!postText.trim()) {
      setError("Please provide post text before running simulation.");
      return;
    }

    setIsLoading(true);
    setError("");
    setResults([]);

    try {
      const form = new FormData();
      form.append("post_text", postText);
      form.append("post_id", crypto.randomUUID());
      form.append("image_url", imageUrl);

      const response = await axios.post(`${apiBaseUrl}/simulate/`, form);
      const data = response.data;

      if (data?.error) {
        setResults(DUMMY_RESPONSES);
        setError(data.error);
        return;
      }

      if (!Array.isArray(data) || data.length === 0) {
        setResults(DUMMY_RESPONSES);
        setError("No reactions returned. Showing dummy data.");
        return;
      }

      setResults(data);
    } catch (requestError) {
      /* Backend is down — use dummy data */
      setResults(DUMMY_RESPONSES);
      setError("Backend unavailable — showing simulated dummy responses.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className={`page-shell ambient-${summary.sentimentClass}`}>
      <div className="orb orb-a" />
      <div className="orb orb-b" />

      <header className="topbar">
        <p className="eyebrow">TwinSphere AI</p>
        <h1>Social Reaction Simulation Console</h1>
        <p className="subtitle">Run campaign posts against digital twins and inspect sentiment-grade reactions in one place.</p>
      </header>

      <main className="layout">
        <section className="panel panel-form">
          <h2>Post Input</h2>
          <form onSubmit={handleSubmit}>
            <label htmlFor="postText">Post Text</label>
            <textarea
              id="postText"
              value={postText}
              onChange={(event) => setPostText(event.target.value)}
              maxLength={280}
              placeholder="Write the campaign or crisis post you want to test..."
            />
            <div className="char-row">{postText.length}/280</div>

            <label htmlFor="imageUrl">Image URL (Optional)</label>
            <input
              id="imageUrl"
              type="url"
              value={imageUrl}
              onChange={(event) => setImageUrl(event.target.value)}
              placeholder="https://images.example.com/post.jpg"
            />

            <button type="submit" disabled={isLoading}>
              {isLoading ? "Running Simulation..." : "Simulate Agent Reactions"}
            </button>
          </form>

          {error ? <div className="alert error">{error}</div> : null}
          {!error && results.length > 0 ? <div className="alert success">Simulation completed successfully.</div> : null}
        </section>

        <section className="panel panel-results">
          <h2>Response Dashboard</h2>

          {isLoading ? (
            <div className="loading-dashboard" aria-live="polite">
              <div className="signal-track">
                <span className="signal-dot" />
                <span className="signal-dot" />
                <span className="signal-dot" />
              </div>
              <p className="loading-copy">Running simulation across active digital twins...</p>
              <div className="stats-grid skeleton-stats">
                {[0, 1, 2].map((item) => (
                  <article key={item} className="stat skeleton-box">
                    <div className="skeleton-line line-sm" />
                    <div className="skeleton-line line-lg" />
                  </article>
                ))}
              </div>

              <div className="reaction-strip skeleton-strip">
                {[0, 1, 2, 3, 4].map((item) => (
                  <span key={item} className="pill skeleton-pill" />
                ))}
              </div>

              <div className="card-list skeleton-card-list">
                {[0, 1, 2, 3].map((item) => (
                  <article key={item} className="result-card skeleton-card" style={{ "--delay": `${item * 0.1}s` }}>
                    <div className="card-head">
                      <div className="skeleton-line line-name" />
                      <div className="skeleton-chip" />
                    </div>
                    <div className="skeleton-line line-md" />
                    <div className="skeleton-line line-full" />
                    <div className="skeleton-line line-full" />
                    <div className="skeleton-line line-md" />
                  </article>
                ))}
              </div>
            </div>
          ) : null}

          {!isLoading ? (
            <>
              {/* Distribution Bar Visual */}
              <div className="distribution-wrapper">
                <div className="distribution-bar">
                  {Object.entries(summary.reactionCount).map(([reaction, count]) => {
                    const widthPct = (count / results.length) * 100;
                    return (
                      <div 
                        key={reaction} 
                        className="dist-segment" 
                        style={{ width: `${widthPct}%`, backgroundColor: reactionColors[reaction] || "#22303c" }}
                        title={`${toTitle(reaction)}: ${count}`}
                      />
                    );
                  })}
                </div>
              </div>

              <div className="stats-grid">
                <article className="stat">
                  <p>Total Reactions</p>
                  <h3>{results.length}</h3>
                </article>
                <article className="stat">
                  <p>Sentiment Health</p>
                  <h3>
                    {summary.healthScore}%
                    <span 
                      className="health-indicator" 
                      style={{ 
                        backgroundColor: summary.sentimentClass === 'positive' ? 'var(--success)' : 
                                         summary.sentimentClass === 'negative' ? 'var(--danger)' : '#a8bfd3' 
                      }} 
                    />
                  </h3>
                </article>
                <article className="stat">
                  <p>Average Confidence</p>
                  <h3>{summary.avgConfidence}</h3>
                </article>
              </div>

              <div className="reaction-strip">
                {Object.entries(summary.reactionCount).map(([reaction, count]) => (
                  <span
                    key={reaction}
                    className="pill"
                    style={{ backgroundColor: reactionColors[reaction] || "#22303c" }}
                  >
                    {toTitle(reaction)}: {count}
                  </span>
                ))}
              </div>

              <div className="card-list">
                {results.map((entry, index) => (
                  <article
                    key={`${entry.agent_name}-${index}`}
                    className="result-card hoverable-card"
                    onMouseEnter={() => handleCardHover(entry.final_message, entry.reaction)}
                    onMouseLeave={handleCardLeave}
                  >
                    <div className="card-head">
                      <div className="agent-identity">
                        <img 
                          className="agent-avatar" 
                          src={`https://api.dicebear.com/7.x/bottts/svg?seed=${encodeURIComponent(entry.agent_name)}&backgroundColor=0ec9b5,2963b7&radius=50`} 
                          alt="avatar" 
                          loading="lazy"
                        />
                        <h4>
                          {entry.persona_icon && <span className="persona-icon">{entry.persona_icon}</span>}
                          {entry.agent_name || "Unknown Agent"}
                        </h4>
                      </div>
                      <span
                        className="tag"
                        style={{ color: reactionColors[entry.reaction] || "#103041", borderColor: reactionColors[entry.reaction] || "#103041" }}
                      >
                        {toTitle(entry.reaction)}
                      </span>
                    </div>

                    <p><strong>Confidence:</strong> {entry.confidence ?? "N/A"}</p>
                    <p><strong>Reasoning:</strong> {entry.reasoning || "No reasoning available"}</p>
                    <p><strong>Final Message:</strong> {entry.final_message || "No final message"}</p>
                    <p><strong>Tags:</strong> {(entry.tags || []).join(", ") || "None"}</p>
                  </article>
                ))}
              </div>
            </>
          ) : null}
        </section>
      </main>

      {/* 2D Avatar in bottom-right corner */}
      <Avatar message={hoveredMessage} reaction={hoveredReaction} />

      <footer className="footer-bar">
        <div className="footer-inner">
          <div className="team-info">
            <span className="footer-label">Built by DigitalTwins Engineers</span>
          </div>
          <div className="links-group">
            <a href="https://github.com/ganeshb2334" target="_blank" rel="noopener noreferrer" className="contributor">
              <span className="contributor-name">Ganesh Bastapure</span>
              <span className="contributor-user">@ganeshb2334</span>
            </a>
            <a href="https://github.com/TanmayMachkar" target="_blank" rel="noopener noreferrer" className="contributor">
              <span className="contributor-name">Tanmay Machkar</span>
              <span className="contributor-user">@TanmayMachkar</span>
            </a>
            <a href="https://github.com/TusharLOL" target="_blank" rel="noopener noreferrer" className="contributor">
              <span className="contributor-name">Tushar Dontulwar</span>
              <span className="contributor-user">@TusharLOL</span>
            </a>
          </div>
          <div className="system-status">
            <span className="status-dot"></span> Simulation Environment Active
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
