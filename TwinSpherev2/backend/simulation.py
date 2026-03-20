import base64
import json
import asyncio
import re
from letta_client import Base64Image, Letta, MessageCreate, TextContent, ImageContent
from letta_client.types import AgentState, ImageContentSource
from typing import List, Dict, Optional
from dotenv import load_dotenv
import os
load_dotenv()

LETTA_AI_API_KEY = os.getenv("LETTA_API_KEY")
if not LETTA_AI_API_KEY:
    raise ValueError("LETTA_API_KEY not found in .env file. Please create a .env file in the 'digital-clone' directory.")

client = Letta(
    token=LETTA_AI_API_KEY,
    base_url=os.getenv("LETTA_SERVER_URL", "https://api.letta.com")
)

def encode_image_to_base64(image_path: str) -> dict:
    """Reads and encodes a local image to base64 format for Letta."""
    with open(image_path, "rb") as f:
        encoded_data = base64.b64encode(f.read()).decode("utf-8")
    return {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": "image/jpeg",  # Update to png if needed
            "data": encoded_data
        }
    }

async def run_simulation_with_image(
    agents: List[AgentState],
    post_id: str,
    post_text: str,
    image_url: Optional[str] = None,
    shared_block_id: Optional[str] = None
) -> Dict[str, dict]:
    """
    Simulate each agent reacting to a crisis post with optional image.
    Returns a dictionary of agent_id -> reaction dict.
    """
    try:
        results = {}
        # encoded_image = encode_image_to_base64(image_path)

        #Present the ad to each agent concurrently
        tasks = [run_simulation_agent(agent, post_text, image_url) for agent in agents]
        results = await asyncio.gather(*tasks)

        # Filter out any None results from failed interactions
        successful_results = [res for res in results if res]
        
        print("\n--- Simulation Complete ---")
        print(f"Successfully collected {len(successful_results)} results.")
        return successful_results

            # messages = [{
            #     "role": "user",
            #     "content": [
            #         {
            #             "type": "text",
            #             "text": text_prompt["text"]
            #         },
            #         {
            #             "type": "image",
            #             "source": {
            #                 "type": "base64",
            #                 "media_type": "image/jpg",
            #                 "data": encode_image
            #             }
            #         }
            #     ]
            # }]
            
            # response = client.agents.messages.create(
            #     agent_id=agent.id,
            #     messages=messages
            # )

            # print(f"Response: {response.content}")

            # if hasattr(response, "content"):
            #     results[agent.id] = {
            #         "agent_name": agent.name,
            #         "json_reaction": response.content.strip()
            #     }
            # else:
            #     results[agent.id] = {"agent_name": agent.name, "json_reaction": "No response"}

    except Exception as e:
        print(f"❌ Error while running simulation: {e}")

    return results

async def run_simulation_agent(agent, ad_content: str, image_url: str = None):
    """Presents an ad to a single agent and processes its response."""
    print(f"\n🎭 Presenting post to agent: {agent.name} ({agent.id})")

    prompt = f"""
    You are on a social media platform and you see the following ad.
    Your name is {agent.name}. Your personality is stored in your 'persona' memory block.

    POST:
    {ad_content}

    {f'The image url for this post is {image_url} and the image is attached after the post text' if image_url else ''}

    You must complete this task in TWO PHASES:

    PHASE 1 - TAKE ACTIONS:
    Based on your persona, use the provided tools to react to this ad. You can use one or more tools (e.g., like and comment).
    Add a log to the shared memory so that other agents are able to view your reaction to the post.
    You are also allowed to read from the shared memory to see how other agents are reacting to it.

    PHASE 2 - PROVIDE ANALYSIS (MANDATORY):
    After your tool calls, you MUST immediately provide a JSON analysis of your reaction.

    Your JSON response must be a single line with no other text, starting with {{{{ and ending with }}}}.

    **If you took multiple actions, for the "reaction" field in the JSON, choose the one that you feel is your PRIMARY reaction.** For example, if you liked and commented, and the comment is more significant, use "comment".

    Required format:
    {{"reaction": "primary_action", "confidence": 0-100, "reasoning": "why you reacted this way", "tags": ["keyword1", "keyword2"], "final_message": "your social media post"}}

    The `reaction` value should be one of `like`, `dislike`, `comment`, `repost`, or `ignore`.

    IMPORTANT: You MUST complete both phases. Do not stop after phase 1.

    Example complete interaction:
    1. [Agent uses tool: agent_like_ad]
    2. [Agent uses tool: agent_comment_ad]
    3. {{"reaction": "comment", "confidence": 90, "reasoning": "I liked it, but my main action is commenting to ask for more details.", "tags": ["eco", "fashion"], "final_message": "Love it! Can you provide more info on your ethical sourcing?"}}
    """

    try:
        # Prepare message content
        content = [{"type": "text", "text": prompt}]
        
        if image_url and image_url.strip():
            content.append({
                "type": "image",
                "source": {
                    "type": "url",
                    "url": image_url
                }
            })

        # Send the prompt to the agent
        print(f"  - Sending prompt to {agent.name}...")
        response = client.agents.messages.create_stream(
            agent_id=agent.id,
            messages=[{
                "role": "user",
                "content": content
            }]
        )

        # Track tool calls and content
        tool_calls = []
        response_content = ""

        for chunk in response:
            msg_type = getattr(chunk, 'message_type', 'unknown')
            # Letta 0.1.x may use 'internal_monologue' or 'assistant_message' for text
            if msg_type in ["assistant_message", "internal_monologue"]:
                text = getattr(chunk, 'content', '') or ''
                response_content += text
            elif msg_type == "tool_call_message":
                tool_name = chunk.tool_call.name
                tool_calls.append(tool_name)
                print(f"  [DEBUG] Tool Call by {agent.name}: {tool_name}")
        
        print(f"  [DEBUG] Tool calls made: {tool_calls}")
        print(f"  [DEBUG] Raw response from {agent.name} (length: {len(response_content)}): '{response_content}'")

        # If we got an empty response but tool calls were made, try to get a follow-up
        if not response_content.strip() and tool_calls:
            print(f"  - Agent {agent.name} made tool calls but gave empty response. Requesting JSON...")
            follow_up_stream = client.agents.messages.create_stream(
                agent_id=agent.id,
                messages=[MessageCreate(role="user", content="Please provide your JSON analysis now as required in the format: {\"reaction\": \"action\", \"confidence\": 0-100, \"reasoning\": \"explanation\", \"tags\": [\"tag1\", \"tag2\"], \"final_message\": \"your post\"}")],
            )
            follow_up_content = ""
            for chunk in follow_up_stream:
                if chunk.message_type == "assistant_message" and chunk.content:
                    follow_up_content += chunk.content
            response_content = follow_up_content
            print(f"  - Follow-up response from {agent.name} (length: {len(response_content)}): '{response_content}'")
        
        if not response_content.strip():
            print("Warning: Empty or whitespace-only response received")
            return None
        
        # Extract the JSON from the agent's final response
        json_response = extract_json_from_string(response_content)

        if json_response:
            # Add agent info to the response
            json_response['agent_id'] = agent.id
            json_response['agent_name'] = agent.name
            # FIX: The agent object from list() doesn't contain memory_blocks.
            # We will return a placeholder for now.
            json_response['description'] = "Persona description (details not available from list view)."
            return json_response
        else:
            print(f"  - Error: Could not parse JSON response from agent '{agent.name}'")
            return None

    except Exception as e:
        print(f"  - Error interacting with agent '{agent.name}': {e}")
        return None
    
def extract_json_from_string(text: str) -> dict:
    """
    Finds and parses the first valid JSON object within a string.
    Handles cases where the JSON is embedded in other text.
    """
    if not text or not text.strip():
        print(f"Warning: Empty or whitespace-only response received")
        return None
    
    # Try to find JSON object enclosed in curly braces
    # Look for the first { and the last } to handle nested objects
    start_idx = text.find('{')
    end_idx = text.rfind('}')
    
    if start_idx == -1 or end_idx == -1 or start_idx >= end_idx:
        print(f"Warning: No valid JSON structure found in text: '{text[:100]}...'")
        return None
    
    json_str = text[start_idx:end_idx + 1]
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"Warning: Could not decode JSON from string: '{json_str[:100]}...', Error: {e}")
        
        # Try to clean up common issues
        # Remove any trailing commas before closing braces/brackets
        cleaned = re.sub(r',(\s*[}\]])', r'\1', json_str)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            print(f"Warning: Even cleaned JSON failed to parse: '{cleaned[:100]}...'")
            return None