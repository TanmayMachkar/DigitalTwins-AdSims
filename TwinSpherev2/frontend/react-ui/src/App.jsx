import { useMemo, useState } from "react";
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

function toTitle(value) {
  if (!value) return "Unknown";
  return value
    .replace(/_/g, " ")
    .split(" ")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function App() {
  const [postText, setPostText] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;

  const summary = useMemo(() => {
    const reactionCount = {};
    let totalConfidence = 0;

    for (const item of results) {
      const reaction = item.reaction || "unknown";
      reactionCount[reaction] = (reactionCount[reaction] || 0) + 1;
      totalConfidence += Number(item.confidence || 0);
    }

    const avgConfidence = results.length ? (totalConfidence / results.length).toFixed(2) : "0.00";

    return {
      reactionCount,
      avgConfidence
    };
  }, [results]);

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
        setResults([]);
        setError(data.error);
        return;
      }

      if (!Array.isArray(data) || data.length === 0) {
        setResults([]);
        setError("No reactions returned. Agents may have skipped this post.");
        return;
      }

      setResults(data);
    } catch (requestError) {
      const message =
        requestError?.response?.data?.error ||
        requestError?.response?.data ||
        requestError?.message ||
        "Unable to run simulation";
      setResults([]);
      setError(String(message));
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="page-shell">
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
              <div className="stats-grid">
                <article className="stat">
                  <p>Total Reactions</p>
                  <h3>{results.length}</h3>
                </article>
                <article className="stat">
                  <p>Average Confidence</p>
                  <h3>{summary.avgConfidence}</h3>
                </article>
                <article className="stat">
                  <p>Unique Reaction Types</p>
                  <h3>{Object.keys(summary.reactionCount).length}</h3>
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
                  <article key={`${entry.agent_name}-${index}`} className="result-card">
                    <div className="card-head">
                      <h4>{entry.agent_name || "Unknown Agent"}</h4>
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
    </div>
  );
}

export default App;
