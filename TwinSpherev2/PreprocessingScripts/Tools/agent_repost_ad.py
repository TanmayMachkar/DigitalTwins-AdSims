import json

def agent_repost_ad(agent_id: str, ad_id: str, repost_reason: str, **kwargs) -> str:
    """
    Use this tool to repost an advertisement, similar to a retweet.

    Args:
        agent_id (str): The ID of the agent performing the action.
        ad_id (str): The unique identifier of the ad being reposted.
        repost_reason (str): The reason or commentary for the repost.

    Returns:
        str: A JSON string confirming the action was successful.
    """
    return json.dumps({"status": "success", "action": "repost", "agent": agent_id, "ad": ad_id, "reason": repost_reason})