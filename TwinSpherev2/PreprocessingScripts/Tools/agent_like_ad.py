import json

def agent_like_ad(agent_id: str, ad_id: str, **kwargs) -> str:
    """
    Use this tool to express a 'like' for an advertisement.

    Args:
        agent_id (str): The ID of the agent performing the action.
        ad_id (str): The unique identifier of the ad being liked.

    Returns:
        str: A JSON string confirming the action was successful.
    """
    return json.dumps({"status": "success", "action": "like", "agent": agent_id, "ad": ad_id})