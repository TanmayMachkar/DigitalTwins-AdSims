import json, random
from pathlib import Path
from src.agents.letta_agent import send_ad_and_get_response, append_episodic_memory

TWINS_DIR = Path("data/twins")
ADS = [
    {"id":"ad_eco_shoe","title":"Eco running shoes","body":"...", "channel":"instagram", "price":2999},
    {"id":"ad_sneaker_sale","title":"Sneaker sale","body":"...", "channel":"youtube", "price":1999}
]

def should_expose(twin, ad, day, freq_caps):
    return ad["channel"] in twin["channels"] and twin.get("exposures",0) < freq_caps.get(twin["id"],3)

def map_llm_to_outcome(llm_json):
    p = float(llm_json.get("prob", 0.0))
    decision = llm_json.get("decision")
    outcome = {"decision": decision, "prob": p, "sampled": random.random() < p}
    return outcome

def run_one_day(agent_id, day_index=0):
    for twin_file in TWINS_DIR.glob("*.json"):
        twin = json.load(open(twin_file))
        ad = random.choice(ADS)
        if should_expose(twin, ad, day_index, freq_caps={}):
            llm_out = send_ad_and_get_response(agent_id, twin, ad)
            print(llm_out)
            outcome = map_llm_to_outcome(llm_out)
            twin.setdefault("exposures", 0)
            twin["exposures"] += 1

            twin.setdefault("memory", {}).setdefault("episodic", [])
            twin["memory"]["episodic"].append(
                f"{ad['id']} -> {outcome['decision']} ({outcome['prob']:.2f})"
            )
            
            append_episodic_memory(agent_id, twin["id"], twin["memory"]["episodic"][-1])
            open(twin_file, "w").write(json.dumps(twin, indent=2))

if __name__ == "__main__":
    run_one_day(agent_id="agent-167261ad-bf82-40bc-8d4b-4ee57b0e3118")
