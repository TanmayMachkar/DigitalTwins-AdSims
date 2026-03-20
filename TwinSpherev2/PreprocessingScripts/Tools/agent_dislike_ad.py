import json

def agent_dislike_ad(agent_id: str, ad_id: str, **kwargs) -> str:
    """
    Use this tool to express a 'dislike' for an advertisement.

    Args:
        agent_id (str): The ID of the agent performing the action.
        ad_id (str): The unique identifier of the ad being disliked.

    Returns:
        str: A JSON string confirming the action was successful.
    """
    return json.dumps({"status": "success", "action": "dislike", "agent": agent_id, "ad": ad_id})