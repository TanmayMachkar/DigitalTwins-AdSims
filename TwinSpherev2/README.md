# 🌀 Twinsphere AI — Simulate Social Media Reactions with Digital Twins

Twinsphere AI is an experimental tool designed to simulate how real-world social media personalities would react to campaigns, crisis posts, or promotional content. It builds digital twins of public figures by analyzing their tweet history, and allows these agents to "see" new posts and respond using their learned persona. 

## Demo
[![Watch the Demo]](https://youtu.be/pjAP1of0YYA)

## 🔍 What It Does

- Extracts personality traits from real Twitter data (interests, tone, sentiment, engagement style).
- Uses Letta agents to simulate each digital twin with memory and tool-based reactions.
- Allows you to upload a social post (text + image) and see how agents would respond in real-time.
- Presents agent reactions visually along with analytics for research or creative refinement.

---

## 🧠 Letta Agents: Built on MemGPT + Memory Layers

Twinsphere relies on Letta AI’s **stateful agents**, inspired by the **MemGPT paper**, to create realistic digital personas with memory and learning capabilities.

Each agent is powered by:
- **Persona Memory Block** (read-only): stores personality traits extracted from tweet history.
- **Interaction Memory Block** (read-write): remembers prior interactions with posts.
- **Shared Memory Block**: lets agents observe how others reacted to the same post (population-level modeling).

### Why This Matters:
✅ **Memory-augmented reasoning**: lets agents “act” like the real person over time.  
✅ **Realistic behavior**: responses reflect the user's tone, sentiment, and engagement patterns.  
✅ **Scalable context**: MemGPT-style memory means agents don't forget who they are or what they've seen.  
✅ **Supports multimodal input**: with image + text awareness in post simulations.

Without Letta's layered memory system, it wouldn’t be feasible to ingest large-scale tweet data and simulate accurate, long-lived persona behaviors.

---

## 💡 Use Cases for Marketers & Creators

**Twinsphere AI is ideal for:**

✅ **Marketing teams**: Pre-test ad campaigns to see how different audience archetypes might respond.

✅ **Content writers & creatives**: Check how variations of tone or language affect perceived sentiment before publishing.

✅ **Social media strategists**: Simulate reactions from influencer personas and tailor messaging accordingly.

✅ **Brand safety & crisis teams**: Predict negative or polarized reactions to sensitive content—before going live.

✅ **Product teams & UX writers**: Reduce feedback cycles by testing messaging on realistic digital personas.

No need to A/B test in the wild—Twinsphere shortens the loop.

---

## ⚙️ How It Works

**Phase 1: Extract Personas**
- Load celebrity tweet dataset from Kaggle.
- Group tweets by username and analyze recent 100 tweets.
- Extract persona profile: topics, tone, sentiment, engagement.
- Store results in `agent_personalities.csv`.

**Phase 2: Create Agents**
- Build Letta agents from the extracted personas.
- Each agent is initialized with:
  - Memory (persona description)
  - Tools (reply, repost, ignore, alert, etc.)
  - Access to shared memory for inter-agent awareness

**Phase 3: Simulation UI**
- Upload a social post via Streamlit UI.
- Post is passed to backend (FastAPI).
- Each agent receives the post and reacts according to personality.
- All reactions are recorded and visualized with stats.

---

## 🛠 Tech Stack

- 🧠 [Letta AI](https://letta.com): Memory-based agent framework (MemGPT-style)
- 🧾 OpenRouter (DeepSeek LLM): Persona extraction from tweets
- 🐍 Python + FastAPI: Backend for simulation coordination
- 📊 Streamlit: UI for creating posts and visualizing agent responses
- 🗃 Pandas / CSV: Lightweight tweet and persona processing
- 📸 Multimodal: Supports image+text posts

---

## 🚀 Setup Instructions

1. **Clone this repo**
```bash
git clone https://github.com/yourname/twinsphere-ai.git
cd twinsphere-ai
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set your API keys**
- Create a .env file in the root directory:
```bash
LETTA_API_KEY=your_letta_api_key_here
OPENROUTER_API_KEY=your_openrouter_key_here
```

4. **Prepare Tweet Data**
Follow these steps:
- Run the Group_Tweets.ipynb notebook:
  - This script groups 100 random tweets for each user (by name) and concatenates them using a separator (<ENDOFTWEET>).
  - The grouped results are saved as group_concatenated_tweets.csv.
- Run the ExtractPersonaFromTweets.ipynb notebook:
  - This script loads the grouped tweets and queries an LLM (e.g. DeepSeek via OpenRouter) to extract a structured persona description.
  - The final output is agent_personalities.csv with two columns:
    - name: Twitter username
    - personality_description: Rich persona inferred from the user's tweets.

5. **Extract Personas**
```bash
python scripts/extract_personas.py
```

6. **Create Agents**
```bash
python scripts/create_agents.py
```

7. **Launch the App**
- First, the backend
```bash
uvicorn backend.main:app --reload
```
- Then in another terminal, start the UI
```bash
streamlit run frontend\app.py
```

# 📊 Sample Outputs
Each agent will output:
- Reaction: like, repost, comment, ignore, alert_authority, volunteer
- Reasoning
- Confidence score
- Final public-facing message
- Tag
- Persona attribution
Analytics shown:
- Reaction distribution
- Confidence heatmap
- Persona engagement map
