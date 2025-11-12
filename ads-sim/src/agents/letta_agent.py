import os, json
import re
from pathlib import Path
from dotenv import load_dotenv
from letta_client import Letta
load_dotenv()

client = Letta(token=os.getenv("LETTA_API_KEY"))

AGENT_ID = None

def create_agent_template(name="ad-twin-agent"):
    agent = client.agents.create(
        name="CampaignSimAgent",
        description="Simulates ad campaigns among digital twins",
        model="anthropic/claude-3-5-sonnet-20241022"
    )
    return agent

def send_ad_and_get_response(agent_id, twin_profile, ad):
    prompt = {
      "system": "You are a simulated person. Use the twin profile and memories to respond to an ad.",
      "profile": twin_profile,
      "ad": ad,
      "instructions": "Return JSON: {reaction, decision, prob, reason}."
    }
    response = client.agents.messages.create(
        agent_id=agent_id,
        messages=[{"role": "user", "content": json.dumps(prompt)}]
    )

    assistant_text = None
    for msg in response.messages:
        if msg.message_type == "assistant_message":
            assistant_text = msg.content
            break

    if not assistant_text:
        print(response)
        raise ValueError("No assistant message found in response")

    match = re.search(r'\{.*\}', assistant_text, re.DOTALL)
    if not match:
        print("Assistant response:\n", assistant_text)
        raise ValueError("Could not extract JSON from assistant message")

    json_text = match.group()
    parsed = json.loads(json_text)
    return parsed

def append_episodic_memory(agent_id, twin_id, memory_text):
    client.agents.passages.insert(
        agent_id=agent_id,
        content=memory_text,
        tags=["episodic", twin_id]
    )

if __name__ == "__main__":
    a = create_agent_template()
    print("Created agent:", a.id)
