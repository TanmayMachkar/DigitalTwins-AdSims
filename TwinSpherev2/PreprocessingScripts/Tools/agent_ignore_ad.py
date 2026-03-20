import json

def agent_ignore_ad(agent_id: str, ad_id: str, **kwargs) -> str:
    """
    Use this tool to ignore an advertisement without any engagement.
    This represents scrolling past or dismissing an ad without interaction.

    Args:
        agent_id (str): The ID of the agent performing the action.
        ad_id (str): The unique identifier of the ad being ignored.

    Returns:
        str: A JSON string confirming the action was successful.
    """
    return json.dumps({"status": "success", "action": "ignore", "agent": agent_id, "ad": ad_id})