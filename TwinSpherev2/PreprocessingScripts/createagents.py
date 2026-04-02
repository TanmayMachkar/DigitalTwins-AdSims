import os
import csv
import inspect
import sys
import asyncio
import Tools.agent_comment_ad, Tools.agent_dislike_ad, Tools.agent_ignore_ad, Tools.agent_like_ad, Tools.agent_repost_ad, Tools.read_shared_knowledge, Tools.write_shared_knowledge
from dotenv import load_dotenv
from letta_client import Letta
load_dotenv()

LETTA_AI_API_KEY = os.getenv("LETTA_API_KEY")
LETTA_SERVER_URL = os.getenv("LETTA_SERVER_URL", "https://api.letta.com")

if not LETTA_AI_API_KEY:
    raise ValueError("LETTA_API_KEY not found in .env file. Please check your .env file in the root directory.")

print(f"[i] Connecting to Letta server at: {LETTA_SERVER_URL}")
CLIENT = Letta(api_key=LETTA_AI_API_KEY, base_url=LETTA_SERVER_URL)
SHARED_BLOCK_LABEL = "public_reactions"

PERSONA_CSV = os.path.join(os.path.dirname(__file__), '..', 'Data', 'Persona.csv')
AGENT_CONFIG = {
    "model": "openai/gpt-4o-mini",
    "embedding": "openai/text-embedding-3-small"
}

TOOL_NAME_MAPPING = {
    "agent_like_ad": Tools.agent_like_ad,
    "agent_dislike_ad": Tools.agent_dislike_ad,
    "agent_comment_ad": Tools.agent_comment_ad,
    "agent_repost_ad": Tools.agent_repost_ad,
    "agent_ignore_ad": Tools.agent_ignore_ad,
    "read_shared_knowledge": Tools.read_shared_knowledge,
    "write_shared_knowledge": Tools.write_shared_knowledge
}

# Manually define tool schemas to handle extra server-side args
CUSTOM_TOOL_SCHEMAS = [
    {
        "name": "agent_like_ad",
        "description": "Use this tool to express a 'like' for an advertisement.",
        "parameters": {
            "type": "object",
            "properties": {
                "agent_id": {"type": "string", "description": "The ID of the agent performing the action."},
                "ad_id": {"type": "string", "description": "The unique identifier of the ad being liked."},
                "**kwargs": {
                    "type": "any",
                    "description": "Any additional parameters that agent would like to pass and use for dynamic use."
                }
            },
            "required": ["agent_id", "ad_id"]
        }
    },
    {
        "name": "agent_dislike_ad",
        "description": "Use this tool to express a 'dislike' for an advertisement.",
        "parameters": {
            "type": "object",
            "properties": {
                "agent_id": {"type": "string", "description": "The ID of the agent performing the action."},
                "ad_id": {"type": "string", "description": "The unique identifier of the ad being disliked."},
                "**kwargs": {
                    "type": "any",
                    "description": "Any additional parameters that agent would like to pass and use for dynamic use."
                }
            },
            "required": ["agent_id", "ad_id"]
        }
    },
    {
        "name": "agent_comment_ad",
        "description": "Use this tool to post a comment on an advertisement.",
        "parameters": {
            "type": "object",
            "properties": {
                "agent_id": {"type": "string", "description": "The ID of the agent performing the action."},
                "ad_id": {"type": "string", "description": "The unique identifier of the ad for the comment."},
                "comment_text": {"type": "string", "description": "The content of the comment."},
                "**kwargs": {
                    "type": "any",
                    "description": "Any additional parameters that agent would like to pass and use for dynamic use."
                }
            },
            "required": ["agent_id", "ad_id", "comment_text"]
        }
    },
    {
        "name": "agent_repost_ad",
        "description": "Use this tool to repost an advertisement, similar to a retweet.",
        "parameters": {
            "type": "object",
            "properties": {
                "agent_id": {"type": "string", "description": "The ID of the agent performing the action."},
                "ad_id": {"type": "string", "description": "The unique identifier of the ad being reposted."},
                "repost_reason": {"type": "string", "description": "The reason or commentary for the repost."},
                "**kwargs": {
                    "type": "any",
                    "description": "Any additional parameters that agent would like to pass and use for dynamic use."
                }
            },
            "required": ["agent_id", "ad_id", "repost_reason"]
        }
    },
    {
        "name": "agent_ignore_ad",
        "description": "Use this tool to ignore an advertisement without any engagement.",
        "parameters": {
            "type": "object",
            "properties": {
                "agent_id": {"type": "string", "description": "The ID of the agent performing the action."},
                "ad_id": {"type": "string", "description": "The unique identifier of the ad being ignored."},
                "**kwargs": {
                    "type": "any",
                    "description": "Any additional parameters that agent would like to pass and use for dynamic use."
                }
            },
            "required": ["agent_id", "ad_id"]
        }
    },
    {
        "name": "read_shared_knowledge",
        "description": "Reads the shared knowledge base accessible to all agents.",
        "parameters": {"type": "object", "properties": {
            "**kwargs": {
                    "type": "any",
                    "description": "Any additional parameters that agent would like to pass and use for dynamic use."
                }
        }}
    },
    {
        "name": "write_shared_knowledge",
        "description": "Writes or appends content to the shared knowledge base.",
        "parameters": {
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "The information to add to the shared knowledge base."},
                "**kwargs": {
                    "type": "any",
                    "description": "Any additional parameters that agent would like to pass and use for dynamic use."
                }
            },
            "required": ["content"]
        }
    }
]

def register_tools():
    """
    Registers all custom tools with the Letta server using manual schemas and source code.
    Returns a list of tool name strings (as expected by agents.create()).
    """
    print("Registering fresh tools...")
    tool_names = []
    for schema in CUSTOM_TOOL_SCHEMAS:
        try:
            tools_source_code = inspect.getsource(TOOL_NAME_MAPPING[schema["name"]])
            tool = CLIENT.tools.create(
                json_schema=schema,
                source_code=tools_source_code
            )
            tool_names.append(tool.name)
            print(f"  - Registered tool '{tool.name}'")
        except Exception as e:
            if "already exists" in str(e):
                tool_names.append(schema['name'])
                print(f"  - Tool '{schema['name']}' already exists.")
            else:
                print(f"Error registering tool '{schema['name']}': {e}")
                sys.exit(1)
    return tool_names

# --- Create Shared Memory ---
def ensure_shared_block():
    existing = list(CLIENT.blocks.list(label=SHARED_BLOCK_LABEL))
    if existing:
        print(f"[=] Shared memory already exists: {existing[0].id}")
        return existing[0]
    block = CLIENT.blocks.create(label=SHARED_BLOCK_LABEL, value="Shared public reaction memory block")
    print(f"[+] Created shared memory block: {block.id}")
    return block

# --- Create Agents ---
def create_agents_from_csv(csv_path: str, tools: list, shared_block_id: str):
    with open(csv_path, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            name = row.get("name")
            persona = row.get("persona")
            if not name or not persona:
                print(f"[!] Skipping invalid row: {row}")
                continue
        
            existing = list(CLIENT.agents.list(name=name))
            if existing:
                print(f"[=] Agent already exists: {name}")
                continue

            agent = CLIENT.agents.create(
                name=name,
                memory_blocks=[
                    {"label": "persona", "value": persona},
                    {"label": "engagement_history", "value": "Stores this agent's post reactions.", "description": "Private reaction history"}
                ],
                block_ids=[shared_block_id],
                tools=tools,
                model=AGENT_CONFIG["model"],
                embedding=AGENT_CONFIG["embedding"]
            )
            print(f"[+] Created agent: {agent.name} ({agent.id})")

async def delete_all_agents():
    """Deletes all agents from the Letta server."""
    print("Deleting all existing agents...")
    try:
        agents = CLIENT.agents.list()
        if not agents:
            print("  - No agents found to delete.")
            return
        
        print(f"  - Found {len(agents)} agents to delete.")
        
        # Delete agents one by one to avoid overwhelming the API
        deleted_count = 0
        for agent in agents:
            try:
                CLIENT.agents.delete(agent.id)
                deleted_count += 1
                print(f"  - Deleted agent {agent.name} ({deleted_count}/{len(agents)})")
                # Small delay to avoid rate limiting
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"  - Warning: Failed to delete agent {agent.name}: {e}")
                # Continue with other agents even if one fails
                continue
        
        print(f"  - Successfully deleted {deleted_count} out of {len(agents)} agents.")
    except Exception as e:
        print(f"An error occurred while listing/deleting agents: {e}")
        # We re-raise the exception to be handled by the API endpoint
        raise e

if __name__ == "__main__":
    tool_names = register_tools()
    shared_block = ensure_shared_block()
    create_agents_from_csv(PERSONA_CSV, tool_names, shared_block.id)
    # asyncio.run(delete_all_agents())